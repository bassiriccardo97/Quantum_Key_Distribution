"""Classes for handle requests of adding new QC links in the SDN Controller."""
from uuid import UUID

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class NewLinkRequest:
    """Request for the API new_link."""
    link_id: UUID
    kme_id: UUID
    rate: float
    ttl: int


@dataclass(frozen=True)
class NewLinkResponse:
    """Response for the API new_link."""
    link_id: UUID
    kme: UUID
    addr: str
