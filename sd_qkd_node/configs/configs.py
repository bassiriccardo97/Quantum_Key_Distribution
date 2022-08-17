"""Configurations for KME."""
import configparser
import logging
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import PostgresDsn


class Base(ABC):
    """Base Config class."""

    # Check Config file for info
    def __init__(self, address: str = "localhost:5000", qc_port: str = "8000"):
        super().__init__()
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
        self.KME_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")
        self.KME_IP = address.split(":")[0]
        self.SAE_TO_KME_PORT = int(address.split(":")[1])
        self.QC_TO_KME_PORT = int(qc_port)
        self.KME_BASE_URL = config["SHARED"]["KME_BASE_URL"]
        self.AGENT_BASE_URL = config["SHARED"]["AGENT_BASE_URL"]
        self.COMPATIBILITY_MODE = config["SHARED"]["COMPATIBILITY_MODE"]
        self.TTL = int(config["SHARED"]["TTL"])
        self.MIN_KEY_SIZE = int(config["SHARED"]["MIN_KEY_SIZE"])
        self.MAX_KEY_SIZE = int(config["SHARED"]["MAX_KEY_SIZE"])
        self.DEFAULT_KEY_SIZE = int(config["SHARED"]["DEFAULT_KEY_SIZE"])
        self.MAX_KEY_PER_REQUEST = int(config["SHARED"]["MAX_KEY_PER_REQUEST"])
        self.STORED_KEY_COUNT = int(config["SHARED"]["STORED_KEY_COUNT"])
        self.MAX_KEY_COUNT = int(config["SHARED"]["MAX_KEY_COUNT"])
        self.MAX_SAE_ID_COUNT = int(config["SHARED"]["MAX_SAE_ID_COUNT"])
        self.SDN_CONTROLLER_IP = config["SHARED"]["SDN_CONTROLLER_IP"]
        self.SND_CONTROLLER_PORT = int(config["SHARED"]["SND_CONTROLLER_PORT"])
        self.SDN_CONTROLLER_ADDRESS = f"http://{self.SDN_CONTROLLER_IP}:{self.SND_CONTROLLER_PORT}"
        self.SUPPORTED_EXTENSION_PARAMS: frozenset[str] = frozenset()
        self.LOCAL_DB_URL = f"sqlite:///{self.KME_IP}_{self.SAE_TO_KME_PORT}_local_db"
        self.KEYS_AHEAD = int(config["SHARED"]["KEYS_AHEAD"])

    @property
    @abstractmethod
    def DEBUG(self) -> bool:
        """Debug flag."""

    @property
    @abstractmethod
    def TESTING(self) -> bool:
        """Test flag."""

    @property
    @abstractmethod
    def SHARED_DB_URL(self) -> str:
        """URL for shared database connection."""

    @property
    @abstractmethod
    def POLL_INTERVAL(self) -> float:
        """The qcserver polls for shutdown every POLL_INTERVAL seconds."""


@dataclass(frozen=False, slots=True, init=False)
class Prod(Base):
    """Configuration for production environment."""

    DEBUG = False
    TESTING = False
    POLL_INTERVAL = 0.5

    @property
    def SHARED_DB_URL(self) -> str:
        """URL for database connection.

        1. Install PostgreSQL
        2. `sudo -i -u postgres psql`
        3. `ALTER ROLE postgres WITH PASSWORD 'secret';`
        4. `CREATE DATABASE prod_db;`
        """
        url: str = PostgresDsn.build(
            scheme="postgresql",
            user="postgres",
            password="secret",
            host="localhost",
            port="5432",
            path="/prod_db",
        )
        return url


@dataclass(frozen=False, slots=True, init=False)
class Dev(Base):
    """Configuration for development environment."""

    DEBUG = True
    TESTING = False
    SHARED_DB_URL = "sqlite:///devdb"
    POLL_INTERVAL = 0.001


@dataclass(frozen=False, slots=True, init=False)
class Test(Base):
    """Configuration for testing environment."""

    DEBUG = False
    TESTING = True
    SHARED_DB_URL = "sqlite:///testdb"
    POLL_INTERVAL = 0.001
