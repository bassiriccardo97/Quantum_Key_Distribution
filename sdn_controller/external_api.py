import logging
from uuid import UUID

from fastapi import HTTPException
from httpx import AsyncClient, ReadError, ConnectError

from sdn_controller.encoder import dump
from sdn_controller.model.new_app import WaitingForResponse, RegisterApp
from sdn_controller.model.new_link import NewLinkResponse


async def agent_api_register_app(kme_addr: str, response: WaitingForResponse | RegisterApp) -> None:
    """Calls the API register_app."""
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"DEBUG -> calling register_app on KME {kme_addr}"
            )
            await client.post(
                url=f"{kme_addr}/sdn_agent/register_app",
                json=dump(response),
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def agent_api_link_confirmed(link_id: UUID, kme1: UUID, kme2: UUID, addr1: str, addr2: str) -> None:
    """Calls the API link_confirmed of the two KMEs connected by the new link."""
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"DEBUG -> calling link_confirmed on KME {addr1}"
            )
            await client.post(
                url=f"{addr1}/sdn_agent/link_confirmed",
                json=dump(NewLinkResponse(link_id=link_id, kme=kme2, addr=addr2)),
                timeout=None
            )
            logging.getLogger().info(
                f"DEBUG -> calling link_confirmed on KME {addr2}"
            )
            await client.post(
                url=f"{addr2}/sdn_agent/link_confirmed",
                json=dump(NewLinkResponse(link_id=link_id, kme=kme1, addr=addr1)),
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )
