"""Utility functions."""
from base64 import b64decode, b64encode
from datetime import datetime
from typing import Collection

from sd_qkd_node.model import Key


def b64_to_tupleint(b64_string: str) -> tuple[int, ...]:
    """Converts a base64 string into a tuple of integer in [0, 255]."""
    assert is_base64(b64_string)
    return tuple(b for b in b64decode(b64_string))


def collectionint_to_b64(c: Collection[int]) -> str:
    """Converts a collection of integer in [0, 255] into a base64 string."""
    assert all(n in range(0, 256) for n in c)
    return str(b64encode(bytes(c)), "utf-8")


def bit_length(c: Collection[int]) -> int:
    """Returns number of bits represented by the given collection of integer.

    Each positive integer number is considered 8-bits long, in range [0, 255].
    """
    assert all(n in range(0, 256) for n in c)
    return len(c) * 8


def bit_length_b64(b64_string: str) -> int:
    """Returns the number of bits represented by the given base64 string."""
    assert is_base64(b64_string)
    return bit_length(b64_to_tupleint(b64_string))


def is_base64(s: str) -> bool:
    """Returns True if 's' is a valid base64 string, else False."""
    bytes_s = bytes(s, "ascii")
    return bytes_s == b64encode(b64decode(bytes_s))


def now() -> int:
    """Returns the actual timestamp as an integer."""
    return int(datetime.now().timestamp())


def encrypt_key(key_to_enc: Key, enc_key: Key) -> Key:
    """Encrypts a key making the bitwise XOR with the key relay."""
    key_to_encrypt: tuple[int, ...] = b64_to_tupleint(key_to_enc.key)
    encryption_key: tuple[int, ...] = b64_to_tupleint(enc_key.key)
    bytes_list: list[int] = []
    for i in range(0, len(key_to_encrypt)):
        bytes_list.append(key_to_encrypt[i] ^ encryption_key[i])
    encrypted_key: tuple[int, ...] = tuple(bytes_list)
    key = collectionint_to_b64(encrypted_key)
    return Key(key_ID=key_to_enc.key_ID, key=key)


def decrypt_key(key_to_dec: Key, dec_key: Key) -> Key:
    """Decrypts a key making the bitwise XOR with the key relay."""
    key_to_decrypt: tuple[int, ...] = b64_to_tupleint(key_to_dec.key)
    decryption_key: tuple[int, ...] = b64_to_tupleint(dec_key.key)
    bytes_list: list[int] = []
    for i in range(0, len(key_to_decrypt)):
        bytes_list.append(decryption_key[i] ^ key_to_decrypt[i])
    decrypted_key: tuple[int, ...] = tuple(bytes_list)
    key = collectionint_to_b64(decrypted_key)
    return Key(key_ID=key_to_dec.key_ID, key=key)
