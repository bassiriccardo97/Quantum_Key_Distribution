from uuid import UUID

from pydantic.dataclasses import dataclass

from sd_qkd_node.model.key_container import KeyContainer, Key


@dataclass(frozen=False)
class ExchangeKeyRequest:
    """Request to relay a key."""
    ksid: UUID
    size: int
    keys: KeyContainer
