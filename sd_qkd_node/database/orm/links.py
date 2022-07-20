"""Representation of a QC between two KMEs inside the database of the KME."""

from orm import Model, UUID, Integer, Float, String

from sd_qkd_node.database import local_models


class Link(Model):  # type: ignore
    """Representation of a QC between two KMEs inside the database of the KME."""

    link_id: UUID
    companion: UUID
    ttl: int
    rate: float
    addr: str

    tablename = "links"
    registry = local_models
    fields = {
        "id": Integer(primary_key=True),
        "link_id": UUID(unique=True, allow_null=False),
        "companion": UUID(unique=False, allow_null=True),
        "ttl": Integer(unique=False, allow_null=False),
        "rate": Float(unique=False, allow_null=False),
        "addr": String(unique=False, allow_null=True, max_length=24)
    }
