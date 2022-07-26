from uuid import UUID

from pydantic.dataclasses import dataclass

from sd_qkd_node.model.key_container import KeyContainer, Key


@dataclass(frozen=False)
class KeyRelayRequest:
    """Request to relay a key."""
    ksid: UUID
    size: int
    keys: Key


@dataclass(frozen=False)
class KeyRelayResponse:
    """Response to relay a key."""
    addr: str
