import logging
from typing import Final

from httpx import Response

from sd_qkd_node.database.dbms import dbms_save_sae

from fastapi import APIRouter, HTTPException

from sd_qkd_node.external_api import sdnc_api_new_app
from sd_qkd_node.model.errors import Error
from sd_qkd_node.model.open_session import OpenSessionRequest


router: Final[APIRouter] = APIRouter(tags=["open_key_session"])


@router.post(
    path="/open_key_session",
    summary="Open session with another app",
    response_model_exclude_none=True,
    include_in_schema=True
)
async def open_key_session(
        osr: OpenSessionRequest
) -> None:
    """
    API to make the KME request a connection to the SDN Controller.
    """
    logging.getLogger().warning(
        f"start open_key_session [[...{str(osr.src)[25:]} -> ...{str(osr.dst)[25:]}]]"
    )
    if osr.src_flag:
        await dbms_save_sae(sae_id=osr.src, ip=osr.ip, port=osr.port)
    else:
        await dbms_save_sae(sae_id=osr.dst, ip=osr.ip, port=osr.port)
    response: Final[Response] = await sdnc_api_new_app(osr)
    if response.status_code != 200:
        error = Error(**response.json())
        raise HTTPException(
            status_code=response.status_code,
            detail=error.message
        )

    logging.getLogger().warning(
        f"finish open_key_session [[...{str(osr.src)[25:]} -> ...{str(osr.dst)[25:]}]]"
    )
