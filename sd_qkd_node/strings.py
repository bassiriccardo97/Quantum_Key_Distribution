import logging
from uuid import UUID

from sd_qkd_node.configs import Config
from sd_qkd_node.database import orm


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
    print(
        f"QKD Node running on http://{Config.KME_IP}:{Config.SAE_TO_KME_PORT}... Press CTRL+C to quit."
    )


def log_qc_shutdown_completed() -> None:
    """QCServer shutdown completed."""
    print(f"QCServer shutdown completed.")


def log_qc_listening(host: str, port: int) -> None:
    """QCServer listening on *host:port*"""
    print(f"QCServer listening on {host}:{port}")


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
    print(
        f"\n{Bcolors.OKGREEN}[OK]{Bcolors.ENDC}\tConnection added:\n"
        f"\tASSIGNED KSID: {Bcolors.BOLD}{ksid.ksid}{Bcolors.ENDC}\n"
        f"\tSAE src: {ksid.src}\n"
        f"\tSAE dst: {ksid.dst}\n"
        f"\tKME src: {ksid.kme_src}\n"
        f"\tKME dst: {ksid.kme_dst}\n"
        f"\tRelay: {ksid.relay}\n"
    )


def log_connection_closed(ksid: UUID) -> None:
    """[!]  Connection closed: *ksid*"""
    print(
        f"\n{Bcolors.WARNING}[!]{Bcolors.ENDC}\tConnection closed: {Bcolors.BOLD}{ksid}{Bcolors.ENDC}"
    )


def log_added_sae(sae: orm.Sae) -> None:
    """
    SAE added:
    UUID: *sae_id*
    ip: *ip*
    port: *port*
    """
    print(
        f"\n{Bcolors.OKGREEN}SAE added:{Bcolors.ENDC}\n"
        f"\tUUID: {sae.sae_id}\n"
        f"\tip: {sae.ip}\n"
        f"\tport: {sae.port}\n"
    )


def log_waiting_app() -> None:
    """[-]  Waiting the other app for Ksid"""
    print(f"{Bcolors.OKBLUE}[-]{Bcolors.ENDC}\tWaiting the other app for Ksid")


def log_kme_id(kme: UUID) -> None:
    """Kme id: *kme*"""
    print(
        f"\n{Bcolors.OKGREEN}Kme id:{Bcolors.ENDC} {Bcolors.BOLD}{kme}{Bcolors.ENDC}"
    )


def log_shutdown_completed() -> None:
    """QKD Node shutdown completed."""
    print(
        f"\nQKD Node shutdown completed."
    )
