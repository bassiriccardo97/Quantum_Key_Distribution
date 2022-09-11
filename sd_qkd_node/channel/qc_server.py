"""The server listening to new blocks from the quantum channel."""
import asyncio
import logging
import struct
from socketserver import TCPServer, StreamRequestHandler, ThreadingMixIn
from struct import unpack
from threading import Thread
from typing import Final, Any

from jsons import loads

from sd_qkd_node.configs import Config
from qcs import Block
from sd_qkd_node.database.dbms import dbms_save_link, create_from_qcs_block

from sd_qkd_node.external_api import sdnc_api_new_link, sdnc_api_update_link
from sd_qkd_node.info.link_info import update_rate


class QCServer:
    """The server listening to new blocks from the quantum channel.

    Usage:
    with QCServer():
        *do things*

    Otherwise, you can start it with .start(),
    BUT then you have to remember to close it calling .stop()
    """

    def __init__(self, host: str = Config.KME_IP, port: int = Config.QC_TO_KME_PORT):
        """Initialize the server."""
        self.host = host
        self.port = port
        self.server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)

        def start_server() -> None:
            self.server.serve_forever(poll_interval=Config.POLL_INTERVAL)

        self.server_thread = Thread(
            target=start_server,
            daemon=True,
        )

    def __enter__(self) -> None:
        """Start the simulator."""
        self.start()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop the simulator."""
        self.stop()

    def start(self) -> None:
        """Start the QC Simulator.

        If you start the QCS calling .start() directly, then you must
        explicitly stop it with a call to .stop(). For this reason, usage with
        the 'with' statement should be preferred.
        """
        self.server_thread.start()

    def stop(self) -> None:
        """Stop the QC Simulator.

        If you stop the QCS calling .stop() directly, before you must
        have explicitly started it with a call to .start(). For this reason,
        usage with the 'with' statement should be preferred.
        """
        self.server.shutdown()
        self.server.server_close()
        self.server_thread.join()


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    """Provide thread anc TCP functionalities to the QCServer."""

    allow_reuse_address = True


class ThreadedTCPRequestHandler(StreamRequestHandler):
    """Class for handling TCP requests."""

    def handle(self) -> None:
        """Handle a TCP request."""
        try:
            len_data: Final[int] = unpack(">I", self.rfile.read(4))[0]
        except struct.error:
            # When the qc is terminated by the simulator, the package sent can be corrupted
            # Only for testing purposes
            return
        data: Final[str] = self.rfile.read(len_data).decode()

        new_block: Block = loads(data, Block, strict=True)

        if Config.COMPATIBILITY_MODE and new_block.link_id is None:
            from uuid import uuid4

            new_block = Block(
                time=new_block.time, id=new_block.id, key=new_block.key, link_id=uuid4()
            )

        asyncio.run(add_block(new_block))


async def add_block(new_block: Block) -> None:
    """Add newly-generated block to database."""
    await create_from_qcs_block(new_block)
    ttl = 15
    link, update = update_rate(new_block.link_id, len(new_block.key))
    if not update:
        new = await dbms_save_link(link_id=new_block.link_id, rate=link.rate, ttl=ttl)
        await sdnc_api_new_link(new_block.link_id, link.rate, ttl)
    else:
        await sdnc_api_update_link(link_id=new_block.link_id, rate=link.rate)
