import logging

from sae import sae_app
from sae.configs import Config
from uvicorn import run


def set_logging() -> None:
    """Initialize logging."""
    logging.basicConfig(
        level=logging.WARNING, filename="logs.log", format=f'%(asctime)s SAE ...{str(Config.SAE_ID)[25:]}: %(message)s'
    )
    logging.getLogger().warning(
        f"Started SAE at {Config.SAE_IP}:{Config.SAE_PORT}, ref KME at {Config.KME_IP}:{Config.KME_PORT}"
    )


if __name__ == "__main__":
    set_logging()
    # noinspection PyTypeChecker
    run(app=sae_app.app, host=Config.SAE_IP, port=Config.SAE_PORT, log_level="warning")
