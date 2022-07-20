"""This is the only module allowed to communicate with the database."""

from sdn_controller.database.db import local_db, local_models, shared_db, shared_models

__all__ = [
    "local_db",
    "local_models",
    "shared_db",
    "shared_models",
]
