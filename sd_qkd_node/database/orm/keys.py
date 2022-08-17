"""Representation of a Key inside the database."""
from orm import Model, Integer, UUID, JSON, Boolean

from sd_qkd_node.database import shared_models


class Key(Model):  # type: ignore
    """Representation of a Key inside the database."""

    key_id: UUID
    ksid: UUID
    instructions: object
    relay: bool
    # when link_id is not assigned the key is a direct/relay key to be delivered to SAEs
    # otherwise it is an enc/dec key for key relay
    link_id: UUID

    tablename = "keys"
    registry = shared_models
    fields = {
        "id": Integer(primary_key=True),
        "key_id": UUID(unique=True, allow_null=False),
        "ksid": UUID(unique=False, allow_null=False),
        "relay": Boolean(unique=False, default=False),
        "instructions": JSON(allow_null=False),
        "link_id": UUID(unique=False, allow_null=True)
    }
