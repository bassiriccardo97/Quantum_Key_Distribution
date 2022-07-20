import os
from typing import Final

from sdn_controller.configs.configs import Base, Prod, Test, Dev


def __set_config() -> Base:
    """Initialize the configuration."""
    env: str | None = os.environ.get("env")
    if env == "prod":
        return Prod()
    elif env == "test":
        return Test()
    else:
        return Dev()


Config: Final[Base] = __set_config()
