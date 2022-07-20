from uuid import UUID

from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass(frozen=True)
class AskConnectionRequest:
    """Request for ask_connection API."""
    sae_id: UUID
    ip: str
    port: int
    qos: dict[str, int | float | bool] = Field(
        default_factory=dict,
        description="""
        The QoS requested by the SAEs.
        """
    )
