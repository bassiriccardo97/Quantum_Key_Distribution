from typing import Final

from fastapi import APIRouter

from sdn_controller.database.dbms import find_peer, get_kme_address
from sdn_controller.external_api import agent_api_register_app
from sdn_controller.model.new_app import NewAppRequest, WaitingForResponse


router: Final[APIRouter] = APIRouter(tags=["new_app"])


@router.post(
    path="/new_app",
    summary="Register a new app",
    response_model_exclude_none=True,
    include_in_schema=True
)
async def new_app(
        request: NewAppRequest
) -> None:
    """
    API to add a new connection.
    """
    response, kmes = await find_peer(request)
    if isinstance(response, WaitingForResponse):
        kme_addr = await get_kme_address(request.kme)
        await agent_api_register_app(kme_addr, response)
    else:
        for i in range(1, len(kmes) - 1):
            kme_addr = await get_kme_address(kmes[i])
            response.kme_src = kmes[i]
            response.kme_dst = kmes[i + 1]
            await agent_api_register_app(kme_addr, response)

        i = len(kmes) - 1
        kme_addr = await get_kme_address(kmes[i])
        response.kme_src = kmes[i - 1]
        response.kme_dst = kmes[i]
        await agent_api_register_app(kme_addr, response)

        i = 0
        kme_addr = await get_kme_address(kmes[i])
        response.kme_src = kmes[i]
        response.kme_dst = kmes[i + 1]
        await agent_api_register_app(kme_addr, response)
