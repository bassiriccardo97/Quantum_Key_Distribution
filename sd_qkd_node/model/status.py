"""The implementation of a Status object."""
from typing import Any

from pydantic.dataclasses import dataclass

from sd_qkd_node.configs import Config


@dataclass(frozen=True)
class Status:
    """Status.

    Status contains information on keys available to be requested by a
    master SAE for a specified slave SAE.
    """

    source_KME_ID: str
    """KME ID of the KME"""

    target_KME_ID: str
    """KME ID of the target KME"""

    master_SAE_ID: str
    """SAE ID of the calling master SAE"""

    slave_SAE_ID: str
    """SAE ID of the specified slave SAE"""

    key_size: int = Config.DEFAULT_KEY_SIZE
    """Default size of key the KME can deliver to the SAE (in bit)"""

    stored_key_count: int = Config.STORED_KEY_COUNT
    """Number of stored keys KME can deliver to the SAE"""

    max_key_count: int = Config.MAX_KEY_COUNT
    """Maximum number of stored_key_count"""

    max_key_per_request: int = Config.MAX_KEY_PER_REQUEST
    """Maximum number of keys per request"""

    max_key_size: int = Config.MAX_KEY_SIZE
    """Maximum size of key the KME can deliver to the SAE (in bit)"""

    min_key_size: int = Config.MIN_KEY_SIZE
    """Minimum size of key the KME can deliver to the SAE (in bit)"""

    max_SAE_ID_count: int = Config.MAX_SAE_ID_COUNT
    """Maximum number of additional_slave_SAE_IDs the KME allows. "0" when
    the KME does not support key multicast"""

    status_extension: Any | None = None
    """(Option) for future use"""
