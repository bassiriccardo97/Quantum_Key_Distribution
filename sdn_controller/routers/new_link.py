from typing import Final

from fastapi import APIRouter

from sdn_controller.database.dbms import add_new_link, get_kme_address
from sdn_controller.external_api import agent_api_link_confirmed
from sdn_controller.model.new_link import NewLinkRequest


router: Final[APIRouter] = APIRouter(tags=["new_link"])


@router.post(
    path="/new_link",
    summary="Register a new link",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def new_link(
        request: NewLinkRequest
) -> None:
    """
    API to add a new QC Link in the network.
    """
    link_id, kme1, kme2 = await add_new_link(
        link_id=request.link_id, kme_id=request.kme_id, rate=request.rate, ttl=request.ttl
    )
    if kme2 is not None:
        addr1 = await get_kme_address(kme1)
        addr2 = await get_kme_address(kme2)
        await agent_api_link_confirmed(link_id, kme1, kme2, addr1, addr2)
