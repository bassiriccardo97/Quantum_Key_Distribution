from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Block:
    """A block of random bits."""

    time: int
    id: UUID
    key: tuple[int, ...]
    link_id: UUID
