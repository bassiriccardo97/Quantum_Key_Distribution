from typing import Final
from uuid import UUID

from fastapi import APIRouter

from sae.strings import log_connection_closed

router: Final[APIRouter] = APIRouter(tags=["ask_close_connection"])


@router.post(
    path="/ask_close_connection",
    summary="To close a connection",
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def ask_close_connection(
        master_sae_id: UUID
) -> None:
    """
    API to communicate the closure of the connection.
    Called by the SAE which started the connection.
    """
    log_connection_closed(master_sae_id)
