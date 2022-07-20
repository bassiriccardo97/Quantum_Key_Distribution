from typing import Final

from fastapi import APIRouter

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm
from sd_qkd_node.database.dbms import dbms_get_kme_address, dbms_last_kme, dbms_get_next_kme, dbms_save_relayed_key, \
    dbms_get_key, get_ksid_on_db
from sd_qkd_node.external_api import kme_api_key_relay
from sd_qkd_node.model.key_container import KeyContainer
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
    ksid: orm.Ksid = await get_ksid_on_db(ksid=request.ksid)
    decryption_key: Final[KeyContainer] = await dbms_get_key(ksid=ksid, kme_src=request.kme_src)
    key_copy = decrypt_key(key_to_dec=request.key, dec_key=decryption_key.keys[0])
    if not await dbms_last_kme(ksid=ksid):
        next_kme = await dbms_get_next_kme(ksid_id=request.ksid)
        next_kme_addr = await dbms_get_kme_address(dst=next_kme)
        encryption_key = await dbms_get_key(ksid=ksid)
        request.key = encrypt_key(key_to_enc=key_copy, enc_key=encryption_key.keys[0])
        request.kme_src = Config.KME_ID
        await kme_api_key_relay(request, next_kme_addr)
    else:
        await dbms_save_relayed_key(ksid=request.ksid, key=key_copy)
