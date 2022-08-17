from uuid import UUID

from pydantic.dataclasses import dataclass

from sd_qkd_node.model.key_container import KeyContainer


@dataclass(frozen=False)
class KeyRelayRequest:
    """Request to relay a key."""
    ksid: UUID
    keys: KeyContainer
