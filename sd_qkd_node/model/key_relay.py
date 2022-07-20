from uuid import UUID

from pydantic.dataclasses import dataclass

from sd_qkd_node.model import Key


@dataclass(frozen=False)
class KeyRelayRequest:
    """Request to relay a key."""
    ksid: UUID
    kme_src: UUID
    key: Key
