from uuid import UUID
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class NewKmeRequest:
    """Request for the API new_kme."""
    ip: str
    port: int
    link_stats_support: bool = True
    application_stats_support: bool = True
    key_relay_mode_enable: bool = True


@dataclass(frozen=True)
class NewKmeResponse:
    """Response to the API new_kme."""
    kme_id: UUID
