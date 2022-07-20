from typing import Final

from fastapi import APIRouter

from sd_qkd_node.configs import Config
from sd_qkd_node.database.dbms import dbms_update_link
from sd_qkd_node.model.new_link import NewLinkResponse

router: Final[APIRouter] = APIRouter(tags=["link_confirmed"])


@router.post(
    path="/link_confirmed",
    summary="Register a QC between two KMEs",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def link_confirmed(
        request: NewLinkResponse
) -> None:
    """
    API called by the SDN Controller to register the confirmed QC.
    """
    await dbms_update_link(link_id=request.link_id, companion=request.kme, addr=request.addr)
