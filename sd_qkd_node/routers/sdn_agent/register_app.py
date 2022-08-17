import logging
from typing import Final
from uuid import UUID

from fastapi import APIRouter

from sd_qkd_node.configs import Config
from sd_qkd_node.database.dbms import dbms_save_ksid, dbms_get_sae_address
from sd_qkd_node.database.orm import Ksid
from sd_qkd_node.external_api import sae_api_assign_ksid
from sd_qkd_node.model.new_app import RegisterApp, WaitingForResponse


router: Final[APIRouter] = APIRouter(tags=["register_app"])


@router.post(
    path="/register_app",
    include_in_schema=False
)
async def register_app(
        request: RegisterApp | WaitingForResponse
) -> None:
    """
    API called by the SDN Controller to comunicate the assigned Ksid for a connection.
    """
    if isinstance(request, WaitingForResponse):
        pass
    else:
        logging.getLogger().info(f"registering app ...{str(request.src)[25:]} -> ...{str(request.dst)[25:]}")
        ksid: Final[Ksid] = Ksid(
            ksid=request.ksid, src=request.src, dst=request.dst, kme_src=request.kme_src,
            kme_dst=request.kme_dst, qos=request.qos, start_time=request.start_time, relay=request.relay
        )
        await dbms_save_ksid(ksid=ksid)
        sae_id: Final[UUID] = request.src if request.kme_src == Config.KME_ID else request.dst
        address, exists = await dbms_get_sae_address(sae_id=sae_id)
        logging.getLogger().info(f"sae_id = {sae_id}, exists = {exists}")
        if exists:
            await sae_api_assign_ksid(ksid, address)
