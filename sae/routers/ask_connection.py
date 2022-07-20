import time
from typing import Final

from fastapi import APIRouter
from httpx import Response

from sae.configs import Config
from sae.external_api import agent_api_open_key_session
from sae.model.ask_connection import AskConnectionRequest
from sae.strings import log_connection_accepted_by_sae, log_error

router: Final[APIRouter] = APIRouter(tags=["ask_connection"])


@router.post(
    path="/ask_connection",
    summary="To open a connection",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def ask_connection(
        request: AskConnectionRequest
) -> str:
    """
    API to request the opening of a connection to a SAE.
    Called by the SAE which wants to start the connection.
    """
    Config.CONNECTIONS[len(Config.CONNECTIONS)] = {
        "sae_id": request.sae_id, "src_ip": request.ip, "src_port": request.port, "qos": request.qos
    }
    response: Final[Response] = await agent_api_open_key_session(request.sae_id, False, request.qos)
    log_connection_accepted_by_sae()
    if response.status_code != 200:
        log_error(response, None)
        time.sleep(2)
    return str(Config.SAE_ID)
