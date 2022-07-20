"""Configuration parameters for KME."""
from argparse import Namespace, ArgumentParser
from os import environ
from typing import Final

from sd_qkd_node.configs.configs import Base, Dev, Test, Prod


def read_args() -> Namespace:
    """Read parameters from CLI."""
    parser = ArgumentParser(prog="poetry run python -m sd_qkd_node")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="The sd_qkd_node address and port. Default 'localhost:5000'.",
        default="localhost:5000",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        help="The port to listen for qc new blocks. Default 8000.",
        default="8000",
    )

    return parser.parse_args()


def __set_config() -> Base:
    """Initialize the configuration."""
    env: str | None = environ.get("env")
    if env != "test":
        args = read_args()
        if env == "prod":
            return Prod(address=args.address, qc_port=args.port)
        else:
            return Dev(address=args.address, qc_port=args.port)
    else:
        return Test()


Config: Final[Base] = __set_config()
