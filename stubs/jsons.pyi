from typing import Type, TypeVar

Self = TypeVar('Self')


def dumps(
        obj: object,
        indent: int
) -> str: ...


def load(
        json_obj: object,
        cls: Type[Self],
        strict: bool
) -> Self: ...


def dump(
        obj: Self,
        strip_nulls: bool,
        strip_privates: bool,
        strip_properties: bool,
        strict: bool
) -> object: ...


def loads(
        string: str,
        cls: Type[Self],
        strict: bool
) -> Self: ...


class DeserializationError(Exception):
    pass
