import logging
from uuid import UUID

import httpx

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm
from sd_qkd_node.model.errors import Error


class Bcolors:
    """Unicode's characters to color the output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def set_logging() -> None:
    """Initialize logging."""
    logging.basicConfig(
        level=logging.WARNING, filename="logs.log",
        format=f'%(asctime)s KME {Config.KME_IP}:{Config.SAE_TO_KME_PORT}: %(message)s'
    )


def log_qc_server_started() -> None:
    """QKD Node running on http://ip:port... Press CTRL+C to quit."""


def log_qc_shutdown_completed() -> None:
    """QCServer shutdown completed."""


def log_qc_listening(host: str, port: int) -> None:
    """QCServer listening on *host:port*"""


def log_connection_created(ksid: orm.Ksid) -> None:
    """
    [OK]    Connection added:
    ASSIGNED KSID: *ksid*
    SAE src: *src*
    SAE dst: *dst*
    KME src: *kme_src*
    KME dst: *kme_dst*
    Relay: *relay*
    """


def log_connection_closed(ksid: UUID) -> None:
    """[!]  Connection closed: *ksid*"""


def log_added_sae(sae: orm.Sae) -> None:
    """
    SAE added:
    UUID: *sae_id*
    ip: *ip*
    port: *port*
    """


def log_waiting_app() -> None:
    """[-]  Waiting the other app for Ksid"""


def log_kme_id(kme: UUID) -> None:
    """Kme id: *kme*"""


def log_shutdown_completed() -> None:
    """QKD Node shutdown completed."""


def log_error(response: httpx.Response, ksid: UUID | None) -> None:
    """[ERR]    *error-message*."""
    err = Error(**response.json())
    if "not found" in err.message:
        if ksid is not None:
            logging.getLogger().error(
                f"{Bcolors.HEADER}CRITICAL{Bcolors.ENDC} -> Connection ...{str(ksid)[25:]} {err.message}"
            )
        else:
            logging.getLogger().error(
                f"{Bcolors.HEADER}CRITICAL{Bcolors.ENDC} -> {err.message}"
            )
    else:
        if ksid is not None:
            logging.getLogger().error(
                f"{Bcolors.FAIL}ERROR{Bcolors.ENDC} -> Connection ...{str(ksid)[25:]} {err.message}"
            )
        else:
            logging.getLogger().error(
                f"{Bcolors.FAIL}ERROR{Bcolors.ENDC} -> {err.message}"
            )
