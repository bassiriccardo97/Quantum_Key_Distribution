"""Manage everything about database of the SDN Controller."""
import asyncio
import uuid
from typing import Final

from fastapi import HTTPException
from orm import NoMatch

from sdn_controller.configs import Config
from sdn_controller.database import orm
from sdn_controller.info.network_info import add_kme_in_network, add_link_in_network, get_path, \
    use_rate_in_path, get_shortest_path, free_rate_in_path, update_rate
from sdn_controller.model.new_app import NewAppRequest, RegisterApp, WaitingForResponse
from sdn_controller.model.new_kme import NewKmeRequest, NewKmeResponse
from sdn_controller.strings import log_connection_closed, log_link_added, log_connection_required, \
    log_connection_created, log_kme_added
from sdn_controller.utils import now

lock = asyncio.Lock()


async def add_new_kme(new_kme: NewKmeRequest) -> NewKmeResponse:
    """Adds a new KME assigning a new UUID.

    Args:
        new_kme: object containing information about the KME to add in the network.

    Returns:
        object: object containing the UUID assigned by the SDN Controller to the new KME.
    """
    kme: Final[orm.Kme] = await orm.Kme.objects.create(ip=new_kme.ip, port=new_kme.port)
    add_kme_in_network(kme.kme_id)
    log_kme_added(kme.kme_id, f"{kme.ip}:{kme.port}")
    return NewKmeResponse(kme_id=kme.kme_id)


async def find_peer(new_app: NewAppRequest) -> tuple[RegisterApp | WaitingForResponse, list[uuid.UUID]]:
    """Creates the KSID for a connection.
    It checks if the connection request is already present in the database:
    if not, then creates the Ksid object but not assigns the Ksid UUID;
    if yes then retrieves the shortest path for the connection and if it exists, assigns the Ksid UUID and
    returns the path.

    Args:
        new_app: object containing information about the SAE which wants to create or join a connection.

    Returns:
        object: tuple containing an object that indicates if the SAE has to wait for the other one or the connection has
            been created, and the list of the KMEs along the path.
    """
    async with lock:
        await __remove_expired_waiting_ksids()
        try:
            ksid: Final[orm.Ksid] = await orm.Ksid.objects.get(
                src=new_app.src, dst=new_app.dst, qos=new_app.qos
            )
            req_rate = new_app.qos["Key_chunk_size"] / new_app.qos["Request_interval"]
            path: list[uuid.UUID] = []
            if ksid.kme_src is not None:
                path = get_path(kme_src=ksid.kme_src, kme_dst=new_app.kme, req_rate=req_rate)
            else:
                path = get_path(kme_src=new_app.kme, kme_dst=ksid.kme_dst, req_rate=req_rate)
            log_connection_created(ksid=ksid, new_kme=new_app.kme)
            relay = False
            if len(path) > 2:
                relay = True
            use_rate_in_path(path, req_rate)
            if new_app.master:
                await ksid.update(kme_src=new_app.kme)
                return RegisterApp(
                    ksid=ksid.ksid, src=new_app.src, dst=ksid.dst, kme_src=new_app.kme,
                    kme_dst=ksid.kme_dst, qos=ksid.qos, start_time=ksid.start_time, relay=relay
                ), path
            else:
                await ksid.update(kme_dst=new_app.kme)
                return RegisterApp(
                    ksid=ksid.ksid, src=new_app.src, dst=ksid.dst, kme_src=ksid.kme_src,
                    kme_dst=new_app.kme, qos=ksid.qos, start_time=ksid.start_time, relay=relay
                ), path
        except NoMatch:
            start_time = now()
            log_connection_required(src=new_app.src, dst=new_app.dst)
            await orm.Ksid.objects.create(
                src=new_app.src, dst=new_app.dst, qos=new_app.qos, kme_dst=new_app.kme, start_time=start_time
            )
            return WaitingForResponse(), []


async def get_kme_address(kme_uuid: uuid.UUID) -> str:
    """Gets the address of the KME referred to a SAE."""
    try:
        kme: Final[orm.Kme] = await orm.Kme.objects.get(kme_id=kme_uuid)
    except NoMatch:
        raise HTTPException(
            status_code=500,
            detail=f"KME ...{str(kme_uuid)[25:]} not found"
        )
    return f"http://{kme.ip}:{kme.port}"


async def add_new_link(
        link_id: uuid.UUID, kme_id: uuid.UUID, rate: float, ttl: int
) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID | None]:
    """Adds the new QC Link with the ids of the KMEs that it's connected to."""
    async with lock:
        link, created = await orm.Link.objects.get_or_create(
            link_id=link_id, defaults={"link_id": link_id, "kme1": kme_id, "rate": rate, "ttl": ttl, "used": 0.0}
        )
        if not created:
            await link.update(kme2=kme_id)
            log_link_added(kme1=link.kme1, kme2=kme_id)
            add_link_in_network(link.kme1, kme_id, link.rate)
            return link_id, link.kme1, kme_id
        return link_id, kme_id, None


async def dbms_update_link(link_id: uuid.UUID, **kwargs: dict[str, int | float]) -> None:
    async with lock:
        link: orm.Link = await orm.Link.objects.get(link_id=link_id)
        await link.update(**kwargs)
        if 'rate' in kwargs.keys():
            update_rate((link.kme1, link.kme2), **kwargs['rate'])


async def delete_ksid(ksid: uuid.UUID) -> None:
    """Deletes the Ksid when a SAE closes the connection and frees the rate in the links."""
    try:
        ksid_to_del: Final[orm.Ksid] = await orm.Ksid.objects.get(ksid=ksid)
        if ksid_to_del.kme_src is not None and ksid_to_del.kme_dst is not None:
            path: list[uuid.UUID] = get_shortest_path(ksid_to_del.kme_src, ksid_to_del.kme_dst)
            rate = ksid_to_del.qos["Key_chunk_size"] / ksid_to_del.qos["Request_interval"]
            async with lock:
                free_rate_in_path(path, rate)
        await ksid_to_del.delete()
        log_connection_closed(ksid=ksid)
    except NoMatch:
        raise HTTPException(
            status_code=500,
            detail=f"Ksid ...{str(ksid)[25:]} not found"
        )


async def __remove_expired_waiting_ksids() -> None:
    """Deletes the connections that waited for the second SAE more than Config.TTL seconds."""
    await orm.Ksid.objects.filter(start_time__lt=now() - Config.TTL, kme_src=None).delete()
    await orm.Ksid.objects.filter(start_time__lt=now() - Config.TTL, kme_dst=None).delete()
