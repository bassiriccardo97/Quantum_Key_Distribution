from typing import Final
from uuid import UUID

from fastapi import APIRouter

from sdn_controller.database.dbms import add_new_link, get_kme_address, dbms_update_link
from sdn_controller.external_api import agent_api_link_confirmed
from sdn_controller.model.new_link import NewLinkRequest


router: Final[APIRouter] = APIRouter(tags=["update_link"])


@router.post(
    path="/update_link",
    summary="Register a new link",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def update_link(
        link_id: UUID, updates: dict[str, int | float]
) -> None:
    """
    API to add a new QC Link in the network.
    """
    await dbms_update_link(link_id, **updates)
