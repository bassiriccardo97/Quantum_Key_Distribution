from datetime import datetime


def now() -> int:
    """Returns the actual timestamp as an integer."""
    return int(datetime.now().timestamp())
