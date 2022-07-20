"""Contains the implementation of an Error object."""
from typing import Any

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Error:
    """Generic Error."""

    message: str

    details: tuple[dict[str, Any], ...] | None = None
    """(Option) Array to supply additional detailed error 
    information specified as name/value pairs. Values may be of any 
    type, including objects. """


@dataclass(frozen=True)
class ServiceUnavailable(Error):
    """Error with status code 503."""


@dataclass(frozen=True)
class BadRequest(Error):
    """Error with status code 400."""


@dataclass(frozen=True)
class Unauthorized(Error):
    """Error with status code 401."""
