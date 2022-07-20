"""Contains the implementation of a Key Container object."""
from typing import Any
from uuid import UUID

from pydantic.dataclasses import dataclass


@dataclass(frozen=False)
class Key:
    """Random digital data with an associated universally unique ID."""

    key_ID: UUID
    """ID of the key"""

    key: str
    """Key data encoded by base64. The key size is specified by
    the "size" parameter in "Get key". If not specified, the
    "key_size" value in Status data model is used as the default
    size."""

    key_ID_extension: Any | None = None
    """(Option) for future use."""

    key_extension: Any | None = None
    """(Option) for future use."""


@dataclass(frozen=True)
class KeyContainer:
    """Key container is used for 'Get key' and 'Get key with key IDs'."""

    keys: tuple[Key, ...]
    """Array of keys. The number of keys is specified by the
    "number" parameter in "Get key". If not specified, the default
    number of keys is 1."""

    key_container_extension: Any | None = None
    """(Option) for future use."""
