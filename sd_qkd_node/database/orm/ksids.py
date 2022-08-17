"""Representation of a Ksid inside the database of the KME."""

from orm import Model, UUID, Integer, JSON, Boolean

from sd_qkd_node.database import local_models
from sd_qkd_node.utils import now


class Ksid(Model):  # type: ignore
    """Representation of a Ksid inside the database of the KME."""

    ksid: UUID
    src: UUID
    dst: UUID
    kme_src: UUID
    kme_dst: UUID
    relay: bool
    qos: dict[str, int | bool | float]
    start_time: int

    tablename = "ksids"
    registry = local_models
    fields = {
        # TODO dk why if ksid pk, when create a Ksid in the db, assigning the ksid gives NOT NULL constraint violated
        "id": Integer(primary_key=True),
        "ksid": UUID(unique=True, allow_null=False),
        "src": UUID(unique=False, allow_null=True),
        "dst": UUID(unique=False, allow_null=True),
        "kme_src": UUID(unique=False, allow_null=True),
        "kme_dst": UUID(unique=False, allow_null=True),
        "relay": Boolean(unique=False, allow_null=False),
        "qos": JSON(allow_null=False),
        "start_time": Integer(unique=False, allow_null=False, default=now)
    }
