"""Representation of a Ksid inside the database."""
import uuid

from orm import Model, UUID, JSON, Integer

from sdn_controller.database.db import local_models
from sdn_controller.utils import now


class Ksid(Model):  # type: ignore
    """Representation of a Ksid inside the database."""

    ksid: UUID
    src: UUID
    dst: UUID
    kme_src: UUID
    kme_dst: UUID
    start_time: int
    qos: dict[str, int | bool | float]

    tablename = "ksids"
    registry = local_models
    fields = {
        "ksid": UUID(primary_key=True, default=uuid.uuid4),
        "src": UUID(unique=False, allow_null=False),
        "dst": UUID(unique=False, allow_null=False),
        "kme_src": UUID(unique=False, allow_null=True),
        "kme_dst": UUID(unique=False, allow_null=True),
        "qos": JSON(allow_null=False),
        "start_time": Integer(unique=False, allow_null=False, default=now)
    }
