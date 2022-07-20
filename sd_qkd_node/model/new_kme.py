from uuid import UUID
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class NewKmeRequest:
    """Request for API new_kme."""
    ip: str
    port: int


@dataclass(frozen=True)
class NewKmeResponse:
    """Response for API new_kme."""
    kme_id: UUID
