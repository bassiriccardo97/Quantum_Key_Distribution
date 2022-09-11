"""Configurations for KME."""
import configparser
import os
import uuid


class Configuration:
    """Config class."""

    # Check Config file for info
    def __init__(
            self, kme_addr: str, address: str
    ) -> None:
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
        self.SAE_ID = uuid.uuid4()
        self.SAE_IP = address.split(":")[0]
        self.SAE_PORT = int(address.split(":")[1])
        self.KME_IP = kme_addr.split(":")[0]
        self.KME_BASE_URL = config["SHARED"]["KME_BASE_URL"]
        self.AGENT_BASE_URL = config["SHARED"]["AGENT_BASE_URL"]
        self.average_duration = float(config["SHARED"]["average_duration"])
        self.KME_PORT = int(kme_addr.split(":")[1])
        self.CONNECTIONS = {}

    def get_connection_by_ip_port_on_src(self, ip: str, port: int) -> dict[str, str | int | uuid.UUID | dict]:
        for key, item in self.CONNECTIONS.items():
            keys = item.keys()
            if "dst_ip" in keys and "dst_port" in keys:
                if item["dst_ip"] == ip and item["dst_port"] == port:
                    return item

    def get_connection_by_sae_id_on_src(self, sae_id: uuid.UUID) -> dict[str, str | int | uuid.UUID | dict]:
        for key, item in self.CONNECTIONS.items():
            keys = item.keys()
            if "sae_id" in keys and "dst_ip" in keys:
                if item["sae_id"] == sae_id:
                    return item

    def get_connection_by_sae_id_on_dst(self, sae_id: uuid.UUID) -> dict[str, str | int | uuid.UUID | dict]:
        for key, item in self.CONNECTIONS.items():
            keys = item.keys()
            if "sae_id" in keys and "src_ip" in keys:
                if item["sae_id"] == sae_id:
                    return item

    def get_connection_by_ksid(self, ksid: uuid.UUID) -> dict[str, str | int | uuid.UUID | dict]:
        for key, item in self.CONNECTIONS.items():
            if "ksid" in item.keys():
                if item["ksid"] == ksid:
                    return item
