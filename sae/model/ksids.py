import asyncio
import logging
import threading
import time
from random import randint, choices
from uuid import UUID

import httpx
import numpy.random
from httpx import Response, TimeoutException

from sae.external_api import sae_api_ask_close_connection, agent_api_close_connection, sae_api_ask_key, kme_api_enc_key
from sae.model.key_container import KeyContainer
from sae.strings import log_connection_closed, log_error, log_got_key, Bcolors
from sae.utils import now


class Connection:
    """Contains the info about a connection identified by a Ksid."""
    def __init__(self, ksid: UUID, src: UUID, dst: UUID, qos: dict[str, int | float | bool], duration: float, logger: logging.Logger):
        self.ksid = ksid
        self.src = src
        self.dst = dst
        self.qos = qos
        self.ask_key_thread = AskKeys(connection=self, logger=logger, duration=duration)


class AskKeys(threading.Thread):
    """Thread that makes the requests for the keys and makes the other app request the same."""
    def __init__(self, connection: Connection, logger: logging.Logger, duration: float):
        super().__init__()
        self.connection = connection
        self.logger = logger
        self.duration = duration

    async def run(self) -> None:
        # time.sleep(randint(0, self.connection.qos["Request_interval"]))
        last = numpy.random.exponential(self.duration, 1)
        while last > 2 * self.duration:
            # Too long durations make tests unreliable
            last = numpy.random.exponential(self.duration, 1)
        start = now()
        temp = start
        # while choices(population=[True, False], weights=[0.9, 0.1], k=1) == [True]:
        while temp - start < last:
            try:
                response: Response = await kme_api_enc_key(self.connection.dst)
                if response.status_code == 200:
                    key = KeyContainer(**response.json())
                    log_got_key(response, self.connection.dst)
                    await sae_api_ask_key(key_id=key.keys[0].key_ID, slave_sae_id=self.connection.dst)
                else:
                    log_error(response, None)
                time.sleep(self.connection.qos["Request_interval"])
                temp = now()
            except (httpx.ConnectError, httpx.ReadError):
                self.logger.error(
                    f"Connection ...{str(self.connection.ksid)[25:]}: {Bcolors.RED}ERROR{Bcolors.ENDC} Connection error"
                )
                break
        await agent_api_close_connection(self.connection.ksid)
        await sae_api_ask_close_connection(self.connection.ksid)
        log_connection_closed(self.connection.dst)


connections: dict[UUID, Connection] = {}
