import logging
from uuid import UUID

import httpx
from fastapi import HTTPException
from httpx import AsyncClient, ReadError, ConnectError

from sae.configs import Config
from sae.encoder import dump
from sae.model.ask_connection import AskConnectionRequest
from sae.model.open_session import OpenSessionRequest


async def kme_api_enc_key(slave_id: UUID) -> httpx.Response:
    """Calls the KME's API enc_keys.
    Returns a httpx Response."""
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO calling enc_keys on KME {Config.KME_IP}:{Config.KME_PORT}"
            )
            resp: httpx.Response = await client.get(
                url=f"http://{Config.KME_IP}:{Config.KME_PORT}{Config.KME_BASE_URL}/{slave_id}/enc_keys",
                params={
                    "size": Config.get_connection_by_sae_id_on_src(slave_id)["qos"]["Key_chunk_size"],
                    "master_sae_id": str(Config.SAE_ID)
                },
                timeout=None
            )
            return resp
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def kme_api_dec_key(master_sae_id: UUID, key_ids: UUID) -> httpx.Response:
    """Calls the KME's API dec_keys.
    Returns a httpx Response."""
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO calling dec_keys on KME {Config.KME_IP}:{Config.KME_PORT}"
            )
            resp: httpx.Response = await client.get(
                url=f"http://{Config.KME_IP}:{Config.KME_PORT}{Config.KME_BASE_URL}/{master_sae_id}/dec_keys",
                params={"key_ids": str(key_ids), 'slave_sae_id': str(Config.SAE_ID)},
                timeout=None
            )
            return resp
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def sae_api_ask_key(key_id: UUID, slave_sae_id: UUID) -> None:
    """Calls the SAE's API ask_key."""
    connection = Config.get_connection_by_sae_id_on_src(sae_id=slave_sae_id)
    ip: str = connection["dst_ip"]
    port: int = connection["dst_port"]
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO calling ask_key on SAE {ip}:{port}"
            )
            await client.post(
                url=f"http://{ip}:{port}/ask_key",
                params={"master_sae_id": str(Config.SAE_ID), "key_ids": key_id},
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def agent_api_close_connection(ksid: UUID) -> None:
    """Calls the SAE's API close_connection."""
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO calling close_connection on KME {Config.KME_IP}:{Config.KME_PORT}"
            )
            await client.post(
                url=f"http://{Config.KME_IP}:{Config.KME_PORT}{Config.AGENT_BASE_URL}/close_connection",
                params={"ksid": str(ksid)},
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def sae_api_ask_close_connection(ksid: UUID) -> None:
    """Calls the SAE's API ask_close_connection."""
    ip: str = Config.get_connection_by_ksid(ksid)["dst_ip"]
    port: int = Config.get_connection_by_ksid(ksid)["dst_port"]
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO calling ask_close_connection on SAE {ip}:{port}"
            )
            await client.post(
                url=f"http://{ip}:{port}/ask_close_connection",
                params={"master_sae_id": str(Config.SAE_ID)},
                timeout=None
            )
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def sae_api_ask_connection(ip: str, port: int) -> httpx.Response:
    """Calls the SAE's API ask_connection.
    Return a httpx Response."""
    request = AskConnectionRequest(
        sae_id=Config.SAE_ID, qos=Config.get_connection_by_ip_port_on_src(ip, port)["qos"],
        ip=Config.SAE_IP, port=Config.SAE_PORT
    )
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO calling ask_connection on SAE {ip}:{port}"
            )
            resp: httpx.Response = await client.post(
                url=f"http://{ip}:{port}/ask_connection",
                json=dump(request),
                timeout=5
            )
            Config.get_connection_by_ip_port_on_src(ip, port)["sae_id"] = UUID(resp.json())
            return resp
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )


async def agent_api_open_key_session(
        sae_id: UUID, src: bool, qos: dict[str, int | float | bool]
) -> httpx.Response:
    """Calls the KME's API open_key_session.
    Returns a httpx Response."""
    if src:
        app_registration = OpenSessionRequest(
            ip=Config.SAE_IP, port=Config.SAE_PORT, src=Config.SAE_ID, dst=sae_id, qos=qos, src_flag=src
        )
    else:
        app_registration = OpenSessionRequest(
            ip=Config.SAE_IP, port=Config.SAE_PORT, src=sae_id, dst=Config.SAE_ID, qos=qos, src_flag=src
        )
    async with AsyncClient() as client:
        try:
            logging.getLogger().info(
                f"INFO calling open_key_session on KME {Config.KME_IP}:{Config.KME_PORT}"
            )
            resp: httpx.Response = await client.post(
                url=f"http://{Config.KME_IP}:{Config.KME_PORT}{Config.AGENT_BASE_URL}/open_key_session",
                json=dump(app_registration),
                timeout=None
            )
            return resp
        except (ConnectError, ReadError):
            raise HTTPException(
                status_code=500,
                detail="Failed to connect"
            )
