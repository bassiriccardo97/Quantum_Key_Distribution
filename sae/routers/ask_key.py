import time
from typing import Final
from uuid import UUID

from fastapi import APIRouter
from httpx import Response

from sae.external_api import kme_api_dec_key
from sae.strings import log_got_key, log_error


router: Final[APIRouter] = APIRouter(tags=["ask_key"])


@router.post(
    path="/ask_key",
    summary="To make the SAE ask a key.",
    response_model_exclude_none=True,
    include_in_schema=False,
)
async def ask_key(
        master_sae_id: UUID,
        key_ids: UUID
) -> None:
    """
    API to make the SAE ask a key.
    Called by the SAE which started the connection.
    """
    response: Response = await kme_api_dec_key(master_sae_id, key_ids)
    if response.status_code == 200:
        log_got_key(response, master_sae_id)
    else:
        log_error(response, None)

