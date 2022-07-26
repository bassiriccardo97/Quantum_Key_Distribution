"""Representation of a Relayed Key inside the database."""
from orm import Model, Integer, UUID, String, Boolean

from sd_qkd_node.configs import Config
from sd_qkd_node.database import local_models


class LocalKey(Model):  # type: ignore
    """Representation of a Key inside the database."""

    key_id: UUID
    key: str
    ksid: UUID
    relay: bool
    link_id: UUID

    tablename = "relayed_keys"
    registry = local_models
    fields = {
        "id": Integer(primary_key=True),
        "key_id": UUID(unique=True, allow_null=False),
        # length of the base64 encrypted max-length key
        "key": String(unique=True, max_length=int(((Config.MAX_KEY_SIZE / 8) // 3) * 4 + 4)),
        "ksid": UUID(unique=False, allow_null=False),
        "relay": Boolean(unique=False, default=False),
        "link_id": UUID(unique=False, allow_null=True)
    }
