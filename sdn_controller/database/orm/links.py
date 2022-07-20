"""Representation of a Link inside the database."""

from orm import Model, UUID, Integer, Float

from sdn_controller.database.db import local_models


class Link(Model):  # type: ignore
    """Representation of a Link inside the database."""

    link_id: UUID
    kme1: UUID
    kme2: UUID
    rate: float
    ttl: int
    used: float

    tablename = "links"
    registry = local_models
    fields = {
        "id": Integer(primary_key=True, unique=True),
        "link_id": UUID(unique=True, allow_null=False),
        "kme1": UUID(unique=False, allow_null=False),
        "kme2": UUID(unique=False, allow_null=True),
        "rate": Float(unique=False, allow_null=False),
        "ttl": Integer(unique=False, allow_null=False),
        "used": Float(unique=False, allow_null=False)
    }
