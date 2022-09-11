import logging
from typing import Final

from fastapi import APIRouter, HTTPException

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm
from sd_qkd_node.database.dbms import dbms_get_kme_address, dbms_save_relayed_key, \
    dbms_get_ksid, dbms_get_decryption_key, dbms_generate_encryption_key_for_relay
from sd_qkd_node.external_api import kme_api_key_relay
from sd_qkd_node.model.key_container import Key
from sd_qkd_node.model.key_relay import KeyRelayRequest, KeyRelayResponse
from sd_qkd_node.utils import encrypt_key, decrypt_key


router: Final[APIRouter] = APIRouter(tags=["key_relay"])


@router.post(
    path="/key_relay",
    summary="Forwards the key relayed.",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def key_relay(
    request: KeyRelayRequest
) -> KeyRelayResponse:
    """
    API to relay a key to the next-hop KME.
    """
    ksid: orm.Ksid = await dbms_get_ksid(ksid=request.ksid)
    logging.getLogger().info(f"KEY RELAY RECEIVED {request.keys.key}")
    decryption_key: Final[Key] = await dbms_get_decryption_key(ksid=ksid)
    logging.getLogger().info(f"KEY RELAY DECRYPTION KEY {decryption_key.key}")
    key: Key | None = None
    if request.keys.key != "":
        # logging.getLogger().error(f"GOT DEC KEY {decryption_key.key}")
        key: Key = decrypt_key(key_to_dec=request.keys, dec_key=decryption_key)
        # logging.getLogger().error(f"DECRYPTED KEY {key.key}")
    else:
        key = decryption_key
        # logging.getLogger().error(f"FIRST RELAY NOT ENCRYPTED {key.key}")
    logging.getLogger().info(f"KEY RELAY DECRYPTED {key.key}")
    res: KeyRelayResponse
    if ksid.kme_dst != Config.KME_ID:
        next_kme_addr = await dbms_get_kme_address(dst=ksid.kme_dst)
        enc_key: Key = await dbms_generate_encryption_key_for_relay(ksid=ksid, size=request.size)
        logging.getLogger().info(f"KEY RELAY ENCRYPTION KEY {enc_key.key}")
        # encryption_key = await dbms_get_encryption_key(ksid=ksid)
        request.keys = encrypt_key(key_to_enc=key, enc_key=enc_key)
        logging.getLogger().info(f"KEY RELAY ENCRYPTED {request.keys.key}")
        res = await kme_api_key_relay(request, next_kme_addr)
        # logging.getLogger().error(f"RELAYING LAST KME ADDR {res.addr}")
        if res.addr == "":
            raise HTTPException(
                status_code=500,
                detail="Internal error relaying a key."
            )
        return res
    else:
        await dbms_save_relayed_key(ksid=ksid, keys=key)
        # logging.getLogger().error(f"RETURNING LAST KME ADDR http://{Config.KME_IP}:{Config.SAE_TO_KME_PORT}")
        return KeyRelayResponse(addr=f"http://{Config.KME_IP}:{Config.SAE_TO_KME_PORT}")
