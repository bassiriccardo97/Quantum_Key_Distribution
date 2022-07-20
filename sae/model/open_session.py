from uuid import UUID
from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass(frozen=True)
class OpenSessionRequest:
    """Request for open_key_session API."""
    src_flag: bool
    src: UUID
    dst: UUID
    port: int
    ip: str = "127.0.0.1"
    qos: dict[str, int | bool | float] = Field(
        default_factory=dict,
        description="""
        The QoS requested by the SAEs.
        """
    )


@dataclass(frozen=True)
class OpenSessionResponse:
    """Response to open_key_session API."""
    ksid: UUID
    src: UUID
    dst: UUID
    qos: dict[str, int | bool | float] = Field(
        default_factory=dict,
        description="""
            The QoS requested by the SAEs.
            """
    )

