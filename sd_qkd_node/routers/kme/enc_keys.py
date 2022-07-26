import logging
from os import environ
from typing import Final
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm
from sd_qkd_node.database.dbms import dbms_get_kme_address, dbms_get_ksid, get_local_key, dbms_generate_keys_direct, \
    dbms_generate_keys_relay, dbms_generate_encryption_key_for_relay
from sd_qkd_node.external_api import kme_api_key_relay, kme_api_exchange_key
from sd_qkd_node.model import Key
from sd_qkd_node.model.errors import BlockNotFound
from sd_qkd_node.model.exchange_key import ExchangeKeyRequest
from sd_qkd_node.model.key_container import KeyContainer
from sd_qkd_node.model.key_relay import KeyRelayRequest, KeyRelayResponse
from sd_qkd_node.utils import encrypt_key


router: Final[APIRouter] = APIRouter(tags=["enc_keys"])


@router.get(
    path="/{slave_sae_id}/enc_keys",
    summary="Get key",
    response_model_exclude_none=True,
    response_model=KeyContainer
)
async def get_key(
        slave_sae_id: UUID,
        master_sae_id: UUID,
        number: int = Query(default=1, description="Number of keys requested", ge=1),
        size: int = Query(default=64, description="Size of each key in bits", ge=1)
) -> KeyContainer | None:
    """
    API to get the Key for the calling master SAE. Starts the key relay if needed.
    """
    # TODO number param not implemented
    logging.getLogger().warning(f"start enc_keys [[...{str(master_sae_id)[25:]} -> ...{str(slave_sae_id)[25:]}]]")
    ksid: orm.Ksid = await dbms_get_ksid(slave_sae_id=slave_sae_id, master_sae_id=master_sae_id)
    kc: KeyContainer
    try:
        if ksid.relay:
            kc = await __get_key_relay(ksid=ksid, size=size)
        else:
            kc = await __get_key_direct(ksid=ksid, size=size)
    except BlockNotFound:
        raise HTTPException(
            status_code=500,
            detail=f"Block not found [[...{str(ksid.src)[25:]} -> ...{str(ksid.dst)[25:]}]]"
        )
    logging.getLogger().warning(f"finish enc_keys [[...{str(master_sae_id)[25:]} -> ...{str(slave_sae_id)[25:]}]]")
    return kc


async def __get_key_direct(ksid: orm.Ksid, size: int) -> KeyContainer:
    new_key: Key | None = None
    if environ.get("qkp") == "yes":
        # gets key generated ahead and stored locally
        logging.getLogger().info("QKP: Searching local keys")
        new_key = await get_local_key(ksid=ksid.ksid)
        if new_key is None:
            logging.getLogger().info("QKP: No local key, generating new ones")
            # generates Config.FUTURE_KEYS + 1 keys, 1 stored on the shared db and returned,
            # while the others stored locally AND on the shared db:
            # - locally to exploit get_local_key on master kme
            # - on shared db to make the slave kme retrieve the instructions
            new_key = await dbms_generate_keys_direct(ksid=ksid, size=size, local=True)
    else:
        # generates and return 1 key stored on the shared db
        logging.getLogger().info("NO QKP: generating new key")
        new_key = await dbms_generate_keys_direct(ksid=ksid, size=size, local=False)
    return KeyContainer(keys=tuple([new_key]))


async def __get_key_relay(ksid: orm.Ksid, size: int) -> KeyContainer | None:
    new_key: Key | None = None
    future_keys: list[Key] = []
    first = ksid.kme_src == Config.KME_ID
    # if not first:
    #    await dbms_generate_encryption_key_for_relay(ksid=ksid, size=size)
    if environ.get("qkp") == "yes":
        # gets key generated ahead and stored locally
        logging.getLogger().info("QKP: Searching local keys (relay)")
        new_key = await get_local_key(ksid=ksid.ksid)
        if new_key is None:
            # generates and return Config.FUTURE_KEYS + 1 keys,
            # the first Config.FUTURE_KEYS stored locally ('future_keys')
            # the last ('new_key') is the one that will be immediately returned, thus not even stored
            logging.getLogger().info("QKP: No local key, generating new ones (relay)")
            new_key, future_keys = await dbms_generate_keys_relay(ksid=ksid, size=size, local=True)
        else:
            return KeyContainer(keys=tuple([new_key]))
    else:
        logging.getLogger().info("NO QKP: generating new key (relay)")
        # generates only one key that is not even stored since is returned immediately
        new_key = await dbms_generate_keys_relay(ksid=ksid, size=size, local=False)
    # if it comes to this point means that new keys have been generated together with encryption keys chain,
    # so they must be relayed
    # await dbms_generate_encryption_key_for_relay(ksid=ksid, size=size)
    next_kme_addr = await dbms_get_kme_address(dst=ksid.kme_dst)
    # await kme_api_enc_key(ksid.src, ksid.dst, next_kme_addr, size)
    # if first:
    await __start_relay(
        ksid=ksid, size=size, future_keys=future_keys, new_key=new_key, next_kme_addr=next_kme_addr
    )
    return KeyContainer(keys=tuple([new_key]))


async def __start_relay(ksid: orm.Ksid, size: int, future_keys: list[Key], new_key: Key, next_kme_addr: str) -> None:
    key_copies: list[Key] = []
    # gets the enc key generated by the second node
    # enc_key: Final[Key] = await dbms_get_encryption_key(ksid=ksid)
    enc_key: Key = await dbms_generate_encryption_key_for_relay(ksid=ksid, size=size)
    # logging.getLogger().error(f"GENERATED ENC KEY {enc_key.key}")
    # encrypt_key(key_to_enc=enc_key, enc_key=enc_key)
    req: KeyRelayRequest = KeyRelayRequest(
        keys=Key(key_ID=UUID('00000000-0000-0000-0000-000000000000'), key=""), ksid=ksid.ksid, size=size
    )
    res: KeyRelayResponse = await kme_api_key_relay(request=req, next_kme_addr=next_kme_addr)
    if res.addr == "":
        raise HTTPException(
            status_code=500,
            detail="Internal error."
        )
    # logging.getLogger().error(f"THE LAST KME ADDR IS {res.addr}")
    # TODO probably also the key_id should be encrypted to avoid leak of any type
    logging.getLogger().info(f"AAAAA ENCRYPTION KEY {enc_key.key}")
    if environ.get("qkp") == "yes":
        logging.getLogger().info("QKP: encrypting keys (relay)")
        for k in future_keys:
            logging.getLogger().info(f"KEY TO BE ENCRYPTED {k.key}")
            key_copies.append(encrypt_key(key_to_enc=k, enc_key=enc_key))
            logging.getLogger().info(f"KEY JUST ENCRYPTED {key_copies[-1].key}")
    else:
        logging.getLogger().info("NO QKP: encrypting key (relay)")
    logging.getLogger().info(f"KEY TO BE ENCRYPTED {new_key.key}")
    key_copies.append(encrypt_key(key_to_enc=new_key, enc_key=enc_key))
    logging.getLogger().info(f"KEY JUST ENCRYPTED {key_copies[-1].key}")
    request: ExchangeKeyRequest = ExchangeKeyRequest(
        ksid=ksid.ksid, size=size, keys=KeyContainer(keys=tuple(key_copies))
    )
    await kme_api_exchange_key(kme_addr=res.addr, request=request)

