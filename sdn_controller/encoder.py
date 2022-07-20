"""
The functions required for JSON encoding.

The functions are taken from 'jsons' library, but the value of some
parameters is enforced so to optimize performance.

Notice that this is not the encoder exploited by FastAPI. In fact, FastAPI
internally exploits Pydantic for JSON encoding.
"""
from typing import TypeVar, Type

import jsons

Self = TypeVar("Self")


def load(json_obj: object, cls: Type[Self]) -> Self:
    """Deserialize a JSON-object to a Python instance of type cls."""
    return jsons.load(json_obj, cls, strict=True)


def dump(obj: object) -> object:
    """Serialize the given Python-instance to an equivalent JSON object."""
    return jsons.dump(
        obj, strip_nulls=True, strip_privates=True, strip_properties=True, strict=True
    )
