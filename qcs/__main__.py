"""A quantum channel simulator."""
import configparser
import logging
import os
from argparse import Namespace, ArgumentParser
from asyncio import open_connection, sleep, run
from dataclasses import dataclass
from datetime import datetime
from struct import pack
from typing import Final
from uuid import uuid4

from jsons import dumps

from qcs import Block


@dataclass
class KME:
    """A KME (host, port) couple."""

    host: str
    port: int


KME_A = KME("localhost", 8000)
KME_B = KME("localhost", 8001)
KMEs = (KME_A, KME_B)

DEBUG: bool = True
GEN_INTERVAL: int = 5
LINK_ID = uuid4()

LB = 1000
UB = 2000


def timestamp() -> int:
    """The current integer timestamp."""
    return int(datetime.now().timestamp())


def get_random_bits() -> tuple[int, ...]:
    """Simulate the generation of a random number of bits.

    More precisely, a random number of bytes, each constituted by 8 random
    bits, is returned. The randomness is simulated exploiting Python's
    "random" library.

    :return: a tuple, containing a random number of random bytes.
    """
    from random import getrandbits, randint

    return tuple(getrandbits(8) for _ in range(randint(LB, UB)))


async def send(block: Block, kme: KME) -> None:
    """Send to the key kme a newly-generated block."""
    _, writer = await open_connection(kme.host, kme.port)

    message: Final[str] = dumps(block, indent=4) + "\n"
    len_message: Final[int] = len(message)

    writer.write(pack(">I", len_message))
    await writer.drain()

    writer.write(bytes(message, "utf-8"))
    await writer.drain()

    writer.close()
    await writer.wait_closed()


def set_logging() -> None:
    """Initialize logging."""
    logger = logging.getLogger("qcs")
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    logger.addHandler(logging.StreamHandler())


def read_args() -> Namespace:
    """Read parameters from CLI."""
    parser = ArgumentParser(prog="poetry run python -m qcs")
    parser.add_argument(
        "-k1",
        "--kme1",
        type=str,
        help="The address of the first KME to which the qcs is referred. Default localhost:8000",
        default="localhost:8000",
    )
    parser.add_argument(
        "-k2",
        "--kme2",
        type=str,
        help="The address of the second KME to which the qcs is referred. Default localhost:8001",
        default="localhost:8001",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=str,
        help="The generation interval of bytes in seconds. Default 10",
        default="10",
    )
    parser.add_argument(
        "-lb",
        "--lowerb",
        type=str,
        help="The lower bound number of bytes generated. Default 1000",
        default="1000",
    )
    parser.add_argument(
        "-ub",
        "--upperb",
        type=str,
        help="The upper bound number of bytes generated. Default 2000",
        default="2000",
    )

    return parser.parse_args()


# Check Config file for info
def set_params(kme1: str, kme2: str, interval: str, lb: str, ub: str) -> None:
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
    global KME_A, KME_B, DEBUG, GEN_INTERVAL, KMEs, LB, UB
    KME_A = KME(kme1.split(":")[0], int(kme1.split(":")[1]))
    KME_B = KME(kme2.split(":")[0], int(kme2.split(":")[1]))
    DEBUG = bool(config["SHARED"]["DEBUG"])
    GEN_INTERVAL = int(interval)
    KMEs = (KME_A, KME_B)
    LB = int(lb)
    UB = int(ub)


async def main() -> None:
    """Main function."""
    set_logging()
    args = read_args()
    set_params(kme1=args.kme1, kme2=args.kme2, interval=args.interval, lb=args.lowerb, ub=args.upperb)

    count = 0
    while True:
        await sleep(GEN_INTERVAL)

        new_block = Block(timestamp(), uuid4(), get_random_bits(), LINK_ID)
        count += 1
        for kme in KMEs:
            await send(new_block, kme)


if __name__ == "__main__":
    run(main())
