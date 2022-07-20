"""Configuration parameters for SAE."""
from argparse import Namespace, ArgumentParser
from typing import Final

from sae.configs.configs import Configuration


def read_args() -> Namespace:
    """Read parameters from CLI."""
    parser = ArgumentParser(prog="poetry run python -m sae")
    parser.add_argument(
        "-k",
        "--kme",
        type=str,
        help="The KME's address to which connect. Default 'localhost:5000'",
        default="localhost:5000",
    )
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="The address of the SAE. Default 'localhost:9000'",
        default="localhost:9000",
    )

    return parser.parse_args()


def __set_config() -> Configuration:
    args = read_args()
    return Configuration(kme_addr=args.kme, address=args.address)


Config: Final[Configuration] = __set_config()
