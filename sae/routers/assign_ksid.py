import logging
from typing import Final

from fastapi import APIRouter
from starlette.background import BackgroundTasks

from sae.configs import Config
from sae.model.ksids import connections, Connection
from sae.model.open_session import OpenSessionResponse

router: Final[APIRouter] = APIRouter(tags=["assign_ksid"])


@router.post(
    path="/assign_ksid",
    summary="Assign the KSID to a connection",
    response_model_exclude_none=True,
    include_in_schema=False
)
async def assign_ksid(
        request: OpenSessionResponse,
        background_tasks: BackgroundTasks
) -> None:
    """
    API To get the Ksid assigned to a connection.
    Called by the KME the SAE refers to.
    """
    logging.getLogger().info(f"assigning ksid for connection towards ...{str(request.dst)[25:]}")
    connections[request.ksid] = Connection(
        ksid=request.ksid, src=request.src, dst=request.dst, qos=request.qos, logger=logging.getLogger()
    )
    if Config.SAE_ID == request.src:
        logging.getLogger().warning(f"ksid assigned for connection towards ...{str(request.dst)[25:]}")
        Config.get_connection_by_sae_id_on_src(request.dst)["ksid"] = request.ksid
        background_tasks.add_task(connections[request.ksid].ask_key_thread.run)
    else:
        Config.get_connection_by_sae_id_on_dst(request.src)["ksid"] = request.ksid
