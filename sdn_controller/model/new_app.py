from uuid import UUID
from pydantic.dataclasses import dataclass
from pydantic import Field


@dataclass(frozen=True)
class NewAppRequest:
    """Request for the API new_app."""
    master: bool
    src: UUID
    dst: UUID
    kme: UUID
    qos: dict[str, int | float | bool] = Field(
        default_factory=dict,
        description="""
        The QoS requested by the SAEs.
        """
    )


@dataclass(frozen=True)
class WaitingForResponse:
    """Response to API new_app, when the other SAE is not registered yet."""
    wait: bool = True


@dataclass(frozen=False)
class RegisterApp:
    """Response to API new_app, when the two SAEs have been registered."""
    ksid: UUID
    src: UUID
    dst: UUID
    kme_src: UUID
    kme_dst: UUID
    start_time: int
    relay: bool
    qos: dict[str, int | float | bool] = Field(
        default_factory=dict,
        description="""
            The QoS requested by the SAEs.
            """
    )
