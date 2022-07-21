from typing import Final
from uuid import UUID

from fastapi import APIRouter, Query

from sd_qkd_node.database import orm
from sd_qkd_node.database.dbms import dbms_get_kme_address, dbms_first_kme, dbms_last_kme, \
    dbms_generate_key, dbms_get_key, get_ksid_on_db
from sd_qkd_node.external_api import kme_api_enc_key, kme_api_start_key_relay
from sd_qkd_node.model import Key
from sd_qkd_node.model.key_container import KeyContainer
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
    # number param not implemented
    ksid: orm.Ksid = await get_ksid_on_db(slave_sae_id=slave_sae_id, master_sae_id=master_sae_id)
    new_key: Key
    if not ksid.relay:
        new_key = await dbms_generate_key(ksid=ksid, size=size, relay=False)
        return KeyContainer(keys=tuple([new_key]))
    else:
        first: Final[bool] = await dbms_first_kme(ksid=ksid)
        last: Final[bool] = await dbms_last_kme(ksid=ksid)
        if not last:
            new_key, next_kme = await dbms_generate_key(ksid=ksid, size=size, relay=True)
            next_kme_addr = await dbms_get_kme_address(dst=next_kme)
            await kme_api_enc_key(master_sae_id, slave_sae_id, next_kme_addr, size)
            if first:
                key_relay: Final[KeyContainer] = await dbms_get_key(ksid=ksid)
                key_copy = encrypt_key(key_to_enc=new_key, enc_key=key_relay.keys[0])
                await kme_api_start_key_relay(key_copy, ksid.ksid, next_kme_addr)
                return KeyContainer(keys=tuple([new_key]))

    return None
