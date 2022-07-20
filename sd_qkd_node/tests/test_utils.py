from typing import Final

from sd_qkd_node import utils


def test_b64_to_iterableint_then_viceversa() -> None:
    s: Final[str] = "OeGMPxh1+2RpJpNCYixWHFLYRubpOKCw94FcCI7VdJA="
    assert s == utils.collectionint_to_b64(utils.b64_to_tupleint(s))


def test_iterableint_to_b64_then_viceversa() -> None:
    t: Final[tuple[int, ...]] = (8, 13, 255)
    assert t == utils.b64_to_tupleint(utils.collectionint_to_b64(t))
