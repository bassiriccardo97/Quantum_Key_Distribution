import logging
from uuid import UUID

from sdn_controller.database import orm


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


def log_kme_added(kme_id: UUID, addr: str) -> None:
    """[OK]   KME added: *kme_id*"""
    print(f"{Bcolors.UNDERLINE}Controller{Bcolors.ENDC}:\t{Bcolors.OKGREEN}[OK]{Bcolors.ENDC}\tKME added = "
          f"{Bcolors.BOLD}...{str(kme_id)[25:]}{Bcolors.ENDC}")
    logging.getLogger().warning(
        f"KME added = ...{str(kme_id)[25:]}, {addr}"
    )


def log_connection_created(ksid: orm.Ksid, new_kme: UUID) -> None:
    """
    [OK]   Connection added:
    ASSIGNED KSID: *ksid*
    SAE src: *src*
    SAE dst: *dst*
    KME src: *kme_src*
    KME dst: *kme_dst*
    """
    print(
        f"\n{Bcolors.UNDERLINE}Controller{Bcolors.ENDC}:\t{Bcolors.OKGREEN}[OK]{Bcolors.ENDC}\tConnection added:\n"
        f"\t\tASSIGNED KSID: {Bcolors.BOLD}...{str(ksid.ksid)[25:]}{Bcolors.ENDC}\n"
        f"\t\tSAE src: ...{str(ksid.src)[25:]}\n"
        f"\t\tSAE dst: ...{str(ksid.dst)[25:]}\n"
        f"\t\tKME src: ...{str(ksid.kme_src or new_kme)[25:]}\n"
        f"\t\tKME dst: ...{str(ksid.kme_dst or new_kme)[25:]}\n"
    )
    logging.getLogger().warning(f"{Bcolors.OKGREEN}OK{Bcolors.ENDC} Connection added: ...{str(ksid.ksid)[25:]} [...{str(ksid.src)[25:]} -> ...{str(ksid.dst)[25:]}]")


def log_connection_required(src: UUID, dst: UUID) -> None:
    """
    [?] Connection required:
    SAE src: *src*
    SAE dst: *dst*
    """
    print(
        f"\n{Bcolors.UNDERLINE}Controller{Bcolors.ENDC}:\t{Bcolors.OKBLUE}[?]{Bcolors.ENDC}\tConnection required:\n"
        f"\t\tSAE src: ...{str(src)[25:]}\n"
        f"\t\tSAE dst: ...{str(dst)[25:]}\n"
    )
    logging.getLogger().warning(f"{Bcolors.WARNING}WARNING{Bcolors.ENDC} Connection required: ...{str(src)[25:]} -> ...{str(dst)[25:]}")


def log_link_added(kme1: UUID, kme2: UUID) -> None:
    """
    [OK]    Link added between
    Kme 1: *kme1*
    Kme 2: *kme2*
    """
    print(
        f"\n{Bcolors.UNDERLINE}Controller{Bcolors.ENDC}:\t{Bcolors.OKGREEN}[OK]{Bcolors.ENDC}\tLink added between:\n"
        f"\t\tKme 1: ...{str(kme1)[25:]}\n"
        f"\t\tKme 2: ...{str(kme2)[25:]}"
    )
    logging.getLogger().warning(f"Link added: ...{str(kme1)[25:]} <-> ...{str(kme2)[25:]}")


def log_connection_closed(ksid: UUID) -> None:
    """[!]  Connection closed: *ksid*"""
    print(
        f"\n{Bcolors.UNDERLINE}Controller{Bcolors.ENDC}:\t{Bcolors.WARNING}[!]{Bcolors.ENDC}\tConnection closed:"
        f" {Bcolors.BOLD}...{str(ksid)[25:]}{Bcolors.ENDC}"
    )
    logging.getLogger().warning(f"Connection closed: ...{str(ksid)[25:]}")
