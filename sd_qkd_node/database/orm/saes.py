"""Representation of a SAE inside the database of the KME."""
from orm import Model, UUID, Integer, String

from sd_qkd_node.database import local_models


class Sae(Model):  # type: ignore
    """Representation of a SAE inside the database of the KME."""

    sae_id: UUID
    ip: str
    port: int

    tablename = "saes"
    registry = local_models
    fields = {
        "id": Integer(primary_key=True),
        "sae_id": UUID(unique=True, allow_null=False),
        # TODO can be IPAddress
        "ip": String(unique=False, allow_null=False, max_length=15),
        "port": Integer(unique=False, allow_null=False)
    }
