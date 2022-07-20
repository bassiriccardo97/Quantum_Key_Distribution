import asyncio
from typing import Final

from httpx import Response
from uvicorn import run

from sd_qkd_node import kme_app
from sd_qkd_node.external_api import sdnc_api_new_kme
from sd_qkd_node.model.new_kme import NewKmeResponse
from sd_qkd_node.channel.qc_server import QCServer
from sd_qkd_node.configs import Config
from sd_qkd_node.strings import set_logging


async def connect_to_controller() -> None:
    """To connect the KME to the SDN Controller to be registered."""
    response: Final[Response] = await sdnc_api_new_kme()
    kme: Final[NewKmeResponse] = NewKmeResponse(**response.json())
    Config.KME_ID = kme.kme_id


if __name__ == "__main__":
    set_logging()
    with QCServer():
        asyncio.run(connect_to_controller())
        # noinspection PyTypeChecker
        run(app=kme_app.app, host=Config.KME_IP, port=Config.SAE_TO_KME_PORT, log_level="warning")
