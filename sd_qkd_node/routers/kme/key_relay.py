import logging
from typing import Final

from fastapi import APIRouter

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm
from sd_qkd_node.database.dbms import dbms_get_kme_address, dbms_save_relayed_key, \
    dbms_get_ksid, dbms_get_decryption_key, dbms_get_encryption_key
from sd_qkd_node.external_api import kme_api_key_relay
from sd_qkd_node.model.key_container import KeyContainer, Key
from sd_qkd_node.model.key_relay import KeyRelayRequest
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
) -> None:
    """
    API to relay a key to the next-hop KME.
    """
    ksid: orm.Ksid = await dbms_get_ksid(ksid=request.ksid)
    decryption_key: Final[Key] = await dbms_get_decryption_key(ksid=ksid)
    key_copies: list[Key] = []
    for k in request.keys.keys:
        key_copies.append(decrypt_key(key_to_dec=k, dec_key=decryption_key))
    if ksid.kme_dst != Config.KME_ID:
        next_kme_addr = await dbms_get_kme_address(dst=ksid.kme_dst)
        encryption_key = await dbms_get_encryption_key(ksid=ksid)
        encrypted_keys: list[Key] = []
        for k in key_copies:
            encrypted_keys.append(encrypt_key(key_to_enc=k, enc_key=encryption_key))
        request.keys = KeyContainer(keys=tuple(encrypted_keys))
        await kme_api_key_relay(request, next_kme_addr)
    else:
        await dbms_save_relayed_key(ksid=ksid, keys=key_copies)
