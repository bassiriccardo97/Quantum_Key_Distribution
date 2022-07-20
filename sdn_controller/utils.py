"""Utility functions."""
from datetime import datetime


def now() -> int:
    """Return the actual timestamp as an integer."""
    return int(datetime.now().timestamp())
