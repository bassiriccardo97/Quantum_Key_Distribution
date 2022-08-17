from typing import Final
from uuid import UUID

from fastapi import APIRouter

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm
from sd_qkd_node.database.dbms import dbms_delete_ksid, dbms_get_ksid
from sd_qkd_node.external_api import agent_api_close_connection

router: Final[APIRouter] = APIRouter(tags=["close_connection"])


@router.post(
    path="/close_connection",
    summary="Close the connection between two SAEs",
    response_model_exclude_none=True,
    include_in_schema=True
)
async def close_connection(
        ksid: UUID
) -> None:
    """
    API called by a SAE to close a connection.
    """
    ksid_to_del: Final[orm.Ksid] = await dbms_get_ksid(ksid=ksid)
    first, last, next_kme_addr = await dbms_delete_ksid(ksid_to_del=ksid_to_del)
    if first:
        await agent_api_close_connection(Config.SDN_CONTROLLER_ADDRESS, ksid)
    if not last:
        await agent_api_close_connection(next_kme_addr + Config.AGENT_BASE_URL, ksid)

