from typing import Final
from uuid import UUID

from fastapi import APIRouter

from sd_qkd_node.database import orm
from sd_qkd_node.database.dbms import dbms_get_key, get_ksid_on_db
from sd_qkd_node.model.key_container import KeyContainer

router: Final[APIRouter] = APIRouter(tags=["dec_keys"])


@router.get(
    path="/{master_sae_id}/dec_keys",
    summary="Get key with key IDs",
    response_model=KeyContainer,
    response_model_exclude_none=True
)
async def get_key_with_key_i_ds(
    master_sae_id: UUID,
    slave_sae_id: UUID,
    key_ids: UUID
) -> KeyContainer:
    """
    API to get the Key for the calling slave SAE.
    """
    ksid: orm.Ksid = await get_ksid_on_db(slave_sae_id=slave_sae_id, master_sae_id=master_sae_id)
    kc = await dbms_get_key(ksid=ksid, key_id=key_ids)
    return kc
