"""Representation of a Block inside the database."""
from orm import Model, Integer, UUID, JSON

from sd_qkd_node.database import local_models


class Block(Model):  # type: ignore
    """Representation of a Block inside the database."""

    link_id: UUID
    block_id: UUID
    timestamp: int
    material: list[int]
    available_bits: int
    in_use: int

    tablename = "blocks"
    registry = local_models
    fields = {
        "id": Integer(primary_key=True),
        "link_id": UUID(allow_null=False),
        "block_id": UUID(unique=True, allow_null=False),
        "timestamp": Integer(allow_null=False),
        "material": JSON(allow_null=False),
        "available_bits": Integer(allow_null=False),
        "in_use": Integer(allow_null=False, default=0, unique=False)
    }
