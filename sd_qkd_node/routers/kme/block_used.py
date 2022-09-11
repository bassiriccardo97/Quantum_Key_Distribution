import logging
from typing import Final
from uuid import UUID

from fastapi import APIRouter

from sd_qkd_node.database.dbms import update_available_bits
from sd_qkd_node.model.errors import BlockNotFound

router: Final[APIRouter] = APIRouter(tags=["block_used"])


@router.post(
    path="/block_used",
    summary="Update available bits on blocks used by the companion KME.",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def block_used(
    block_id: UUID, used: int
) -> None:
    """
    API to set the used bits of the block in the companion KME.
    """
    try:
        await update_available_bits(block_id=block_id, used=used)
    except BlockNotFound:
        logging.getLogger().error(f"Byte update on block failed.")
