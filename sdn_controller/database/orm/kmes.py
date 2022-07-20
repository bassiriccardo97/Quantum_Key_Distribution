"""Representation of a KME inside the database."""
import uuid

from orm import Model, UUID, String, Integer

from sdn_controller.configs import Config
from sdn_controller.database.db import local_models


class Kme(Model):  # type: ignore
    """Representation of a KME inside the database."""

    kme_id: UUID
    ip: str
    port: int

    tablename = "kmes"
    registry = local_models
    fields = {
        "kme_id": UUID(primary_key=True, default=uuid.uuid4),
        # if debugging or testing the IP will be 'localhost', then not unique
        "ip": String(unique=False, allow_null=False, max_length=15),
        "port": Integer(allow_null=False, unique=True)
    }
