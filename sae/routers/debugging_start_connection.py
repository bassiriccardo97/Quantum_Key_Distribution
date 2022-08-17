import logging
from asyncio import CancelledError
from typing import Final
from uuid import UUID

import httpx
from fastapi import APIRouter
from httpx import Response

from sae.configs import Config
from sae.external_api import agent_api_open_key_session, sae_api_ask_connection
from sae.strings import log_error, log_connection_error, log_successfully_connected, Bcolors

router: Final[APIRouter] = APIRouter(tags=["debugging_start_connection"])


async def connect_to_app(ip: str, port: int, interval: int, key_length: int) -> None:
    """Starts the connection procedure towards a SAE."""
    qos = {"Key_chunk_size": key_length, "Request_interval": interval}
    Config.CONNECTIONS[len(Config.CONNECTIONS)] = {
        "dst_ip": ip, "dst_port": port, "qos": qos
    }
    try:
        connection_response: Final[Response] = await sae_api_ask_connection(ip, port)
        sae_id: UUID = UUID(connection_response.json())
        open_session_response: Final[Response] = await agent_api_open_key_session(sae_id, True, qos)
        if open_session_response.status_code == 200:
            log_successfully_connected()
        else:
            log_error(open_session_response, None)
    except httpx.ConnectError:
        log_connection_error()
        return
    # except httpx.ReadTimeout or httpx.ConnectTimeout or TimeoutError or CancelledError:
    #    logging.getLogger().error(f"{Bcolors.RED}ERROR{Bcolors.ENDC} -> Timeout connection.")


@router.get(
    path="/debugging_start_connection",
    summary="To make the SAE start a connection",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def start_connection(
        ip: str, port: int, interval: int, key_length: int
) -> None:
    await connect_to_app(ip=ip, port=port, interval=interval, key_length=key_length)
