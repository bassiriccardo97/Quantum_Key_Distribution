"""Configurations for KME."""
import configparser
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import PostgresDsn


class Base(ABC):
    """Base Config class."""

    # Check Config file for info
    def __init__(self) -> None:
        super().__init__()
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
        self.IP = config["GENERIC"]["IP"]
        self.PORT = int(config["GENERIC"]["PORT"])
        self.LOCAL_DB_URL = f"sqlite:///Controller_local_db"
        self.TTL = int(config["GENERIC"]["TTL"])
        self.FUTURE_KEYS = int(config["GENERIC"]["FUTURE_KEYS"])
        self.N_KMES = int(config["RING"]["n_kme"])

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


@dataclass(frozen=False, slots=True, init=False)
class Prod(Base):
    """Configuration for production environment."""

    DEBUG = False
    TESTING = False

    @property
    def SHARED_DB_URL(self) -> str:
        """URL for database connection.

        1. Install PostgreSQL
        2. `sudo -i -u postgres psql`
        3. `ALTER ROLE postgres WITH PASSWORD 'very_strong_password';`
        4. `CREATE DATABASE c_prod_db;`
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


@dataclass(frozen=False, slots=True, init=False)
class Test(Base):
    """Configuration for testing environment."""

    DEBUG = False
    TESTING = True
    SHARED_DB_URL = "sqlite:///testdb"
