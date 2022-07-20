import logging
import threading
import time
from random import randint
from uuid import UUID

import httpx
from httpx import Response, TimeoutException

from sae.external_api import sae_api_ask_close_connection, agent_api_close_connection, sae_api_ask_key, kme_api_enc_key
from sae.model.key_container import KeyContainer
from sae.strings import log_connection_closed, log_error, log_got_key, Bcolors
from sae.utils import now


class Connection:
    """Contains the info about a connection identified by a Ksid."""
    def __init__(self, ksid: UUID, src: UUID, dst: UUID, qos: dict[str, int | float | bool], logger: logging.Logger):
        self.ksid = ksid
        self.src = src
        self.dst = dst
        self.qos = qos
        self.ask_key_thread = AskKeys(connection=self, logger=logger)


class AskKeys(threading.Thread):
    """Thread that makes the requests for the keys and makes the other app request the same."""
    def __init__(self, connection: Connection, logger: logging.Logger):
        super().__init__()
        self.connection = connection
        self.logger = logger

    async def run(self) -> None:
        while randint(1, 5) != 1:
            try:
                response: Response = await kme_api_enc_key(self.connection.dst)
                if response.status_code == 200:
                    key = KeyContainer(**response.json())
                    log_got_key(response, self.connection.dst)
                    await sae_api_ask_key(key_id=key.keys[0].key_ID, slave_sae_id=self.connection.dst)
                else:
                    log_error(response, None)
                time.sleep(self.connection.qos["Request_interval"])
            except (httpx.ConnectError, httpx.ReadError):
                self.logger.error(
                    f"Connection ...{str(self.connection.ksid)[25:]}: {Bcolors.RED}ERROR{Bcolors.ENDC} Connection error"
                )
                break
        await agent_api_close_connection(self.connection.ksid)
        await sae_api_ask_close_connection(self.connection.ksid)
        log_connection_closed(self.connection.dst)


connections: dict[UUID, Connection] = {}
