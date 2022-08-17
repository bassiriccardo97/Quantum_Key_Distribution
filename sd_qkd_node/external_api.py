import logging
from uuid import UUID

import httpx
from fastapi import HTTPException
from httpx import AsyncClient, ConnectError, ReadError, Response

from sd_qkd_node import strings
from sd_qkd_node.configs import Config
from sd_qkd_node.database.orm import Ksid
from sd_qkd_node.encoder import dump
from sd_qkd_node.model import Key
from sd_qkd_node.model.key_container import KeyContainer
from sd_qkd_node.model.key_relay import KeyRelayRequest
from sd_qkd_node.model.new_app import NewAppRequest
from sd_qkd_node.model.new_kme import NewKmeRequest
from sd_qkd_node.model.new_link import NewLinkRequest
from sd_qkd_node.model.open_session import OpenSessionRequest, OpenSessionResponse


async def kme_api_enc_key(master_id: UUID, slave_id: UUID, next_kme_addr: str, size: int = 64) -> None:
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO -> calling enc_keys on KME {next_kme_addr}"
            )
            await client.get(
                url=f"{next_kme_addr}{Config.KME_BASE_URL}/{slave_id}/enc_keys",
                params={"size": size, "master_sae_id": str(master_id)},
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def kme_api_key_relay(request: KeyRelayRequest, next_kme_addr: str) -> None:
    async with AsyncClient() as client:
        try:
            res: Response = await client.post(
                url=f"{next_kme_addr}{Config.KME_BASE_URL}/key_relay",
                json=dump(request),
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def agent_api_close_connection(addr: str, ksid: UUID) -> None:
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO -> calling close_connection on {addr}"
            )
            await client.post(
                url=f"{addr}/close_connection",
                params={"ksid": str(ksid)},
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def sdnc_api_new_app(request: OpenSessionRequest) -> Response:
    app_registration: NewAppRequest = NewAppRequest(
        master=request.src_flag, src=request.src, dst=request.dst, kme=Config.KME_ID, qos=request.qos
    )
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO -> calling new_app on KME SDN Controller"
            )
            resp: Response = await client.post(
                url=f"{Config.SDN_CONTROLLER_ADDRESS}/new_app",
                json=dump(app_registration),
                timeout=None
            )
            return resp
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def sae_api_assign_ksid(ksid: Ksid, address: str) -> None:
    resp = OpenSessionResponse(ksid=ksid.ksid, src=ksid.src, dst=ksid.dst, qos=ksid.qos)
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"calling assign_ksid on SAE ...{str(ksid.src)[25:]}"
            )
            await client.post(
                url=f"{address}/assign_ksid",
                json=dump(resp),
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def sdnc_api_new_kme() -> Response:
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO -> calling new_kme on SDN Controller"
            )
            resp: Response = await client.post(
                url=f"{Config.SDN_CONTROLLER_ADDRESS}/new_kme",
                json=dump(NewKmeRequest(ip=Config.KME_IP, port=Config.SAE_TO_KME_PORT)),
                timeout=None
            )
            return resp
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def sdnc_api_new_link(link_id: UUID, rate: float, ttl: int) -> None:
    request = NewLinkRequest(link_id=link_id, kme_id=Config.KME_ID, rate=rate, ttl=ttl)
    async with AsyncClient() as client:
        try:
            '''logging.getLogger().info(
                f"INFO -> calling new_link on SDN Controller"
            )'''
            await client.post(
                url=f"{Config.SDN_CONTROLLER_ADDRESS}/new_link",
                json=dump(request),
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


# kwargs can be rate and ttl
async def sdnc_api_update_link(link_id: UUID, **kwargs: dict[str, int | float]) -> None:
    async with AsyncClient() as client:
        try:
            '''logging.getLogger().info(
                f"INFO -> calling update_link on SDN Controller"
            )'''
            await client.post(
                url=f"{Config.SDN_CONTROLLER_ADDRESS}/update_link",
                params={"link_id": link_id, "updates": kwargs},
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def kme_update_block(addr: str, block_id: UUID, used: int) -> None:
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO -> calling block_used on KME {addr}"
            )
            await client.post(
                url=f"{addr}{Config.KME_BASE_URL}/block_used",
                params={"block_id": str(block_id), "used": used},
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )
