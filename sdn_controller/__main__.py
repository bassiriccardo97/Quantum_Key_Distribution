import logging

from uvicorn import run

from sdn_controller import sdn_app
from sdn_controller.configs import Config


def set_logging() -> None:
    """Initialize logging."""
    logging.basicConfig(level=logging.WARNING, filename="logs.log", format='%(asctime)s CTR: %(message)s')


if __name__ == "__main__":
    set_logging()
    logging.getLogger().warning(f"Controller started at {Config.IP}:{Config.PORT}.")
    # noinspection PyTypeChecker
    run(app=sdn_app.app, host=Config.IP, port=Config.PORT, log_level="warning")
    logging.getLogger("sdn_controller").info(
        f"\nSDN Controller shutdown completed."
    )
