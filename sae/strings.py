import logging
from uuid import UUID

import httpx

from sae.model.errors import Error
from sae.model.key_container import KeyContainer


class Bcolors:
    """Unicode's characters to color the output."""
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def log_connection_closed(sae_id: UUID) -> None:
    """[END]    Connection closed."""
    print(f"\n{Bcolors.BLUE}[END]{Bcolors.ENDC}\tConnection closed.")
    logging.getLogger().warning(
        f"Connection with ...{str(sae_id)[25:]} closed."
    )


def log_got_key(response: httpx.Response, companion: UUID) -> None:
    """[-]    Got key: *b64-encoded-key*."""
    kc = KeyContainer(**response.json())
    print(
        f"\n{Bcolors.YELLOW}[-]{Bcolors.ENDC}\tGot key: {kc.keys[0].key}"
    )
    logging.getLogger().warning(
        f"{Bcolors.BLUE}KEY{Bcolors.ENDC} -> {kc.keys[0].key} [Companion SAE ...{str(companion)[25:]}]"
    )


def log_error(response: httpx.Response, ksid: UUID | None) -> None:
    """[ERR]    *error-message*."""
    err = Error(**response.json())
    print(
        f"\n{Bcolors.RED}[ERR]{Bcolors.ENDC}\t{err.message}"
    )
    if "not found" in err.message:
        if ksid is not None:
            logging.getLogger().error(
                f"{Bcolors.MAGENTA}CRITICAL{Bcolors.ENDC} -> Connection ...{str(ksid)[25:]} {err.message}"
            )
        else:
            logging.getLogger().error(
                f"{Bcolors.MAGENTA}CRITICAL{Bcolors.ENDC} -> {err.message}"
            )
    else:
        if ksid is not None:
            logging.getLogger().error(
                f"{Bcolors.RED}ERROR{Bcolors.ENDC} -> Connection ...{str(ksid)[25:]} {err.message}"
            )
        else:
            logging.getLogger().error(
                f"{Bcolors.RED}ERROR{Bcolors.ENDC} -> {err.message}"
            )


def log_connection_error() -> None:
    """[ERR]    Connection error, retry."""
    print(f"\n{Bcolors.RED}[ERR]{Bcolors.ENDC}\tConnection error, retry.")
    logging.getLogger().error(
        f"{Bcolors.RED}ERROR{Bcolors.ENDC} -> Connection error, retry."
    )


def log_successfully_connected() -> None:
    """[OK]    Successfully connected."""
    print(f"\n{Bcolors.GREEN}[OK]{Bcolors.ENDC}\tSuccessfully connected.")
    logging.getLogger().warning(
        f"Successfully connected."
    )


def log_connection_accepted_by_sae() -> None:
    """[OK]    Connection accepted by the SAE."""
    print(f"\n{Bcolors.GREEN}[OK]{Bcolors.ENDC}\tConnection accepted by dst SAE.")
    logging.getLogger().warning(
        f"Connection accepted by dst SAE."
    )
