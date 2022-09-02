import logging
from typing import Final

from fastapi import APIRouter

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm
from sd_qkd_node.database.dbms import dbms_get_kme_address, dbms_save_relayed_key, \
    dbms_get_ksid, dbms_get_decryption_key, dbms_get_encryption_key, dbms_generate_encryption_key_for_relay
from sd_qkd_node.external_api import kme_api_key_relay
from sd_qkd_node.model.exchange_key import ExchangeKeyRequest
from sd_qkd_node.model.key_container import KeyContainer, Key
from sd_qkd_node.model.key_relay import KeyRelayRequest
from sd_qkd_node.utils import encrypt_key, decrypt_key


router: Final[APIRouter] = APIRouter(tags=["exchange_key"])


@router.post(
    path="/exchange_key",
    summary="Forwards the key relayed.",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def exchange_key(
    request: ExchangeKeyRequest
) -> None:
    """
    API to relay a key to the next-hop KME.
    """
    ksid: orm.Ksid = await dbms_get_ksid(ksid=request.ksid)
    decryption_key: Final[Key] = await dbms_get_encryption_key(ksid=ksid)
    logging.getLogger().info(f"AAAAA DECRYPTION KEY {decryption_key.key}")
    for k in request.keys.keys:
        logging.getLogger().info(f"KEY RECEIVED {k.key}")
        await dbms_save_relayed_key(ksid=ksid, keys=decrypt_key(key_to_dec=k, dec_key=decryption_key))
        logging.getLogger().info(f"DECRYTPED AND STORED KEY {decrypt_key(key_to_dec=k, dec_key=decryption_key).key}")
