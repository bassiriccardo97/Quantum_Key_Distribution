"""Examples exploited for testing purposes."""
from typing import Final
from uuid import UUID, uuid4

from sd_qkd_node.database import orm
from sd_qkd_node.utils import now
from qcs import Block

link_id = uuid4()

key_1: Final[orm.Key] = orm.Key(
    key_id=UUID("bc490419-7d60-487f-adc1-4ddcc177c139"),
    instructions=[
        {"block_id": "fa63d644-62c3-4818-a170-f3d0bd367888", "start": 0, "end": 32}
    ],
)

key_2: Final[orm.Key] = orm.Key(
    key_id=UUID("0a782fb5-3434-48fe-aa4d-14f41d46cf92"),
    instructions=[
        {"block_id": "22832407-7a17-4417-a754-71e51b968889", "start": 0, "end": 8}
    ],
)

block_1: Final[Block] = Block(
    time=now(),
    id=UUID("fa63d644-62c3-4818-a170-f3d0bd367888"),
    link_id=link_id,
    key=(
        189,
        28,
        36,
        21,
        180,
        130,
        118,
        221,
        89,
        26,
        100,
        118,
        171,
        84,
        254,
        110,
        148,
        170,
        255,
        39,
        142,
        235,
        153,
        225,
        224,
        252,
        161,
        232,
        141,
        159,
        210,
        172,
    ),
)

block_2: Final[Block] = Block(
    time=now(),
    id=UUID("22832407-7a17-4417-a754-71e51b968889"),
    link_id=link_id,
    key=(
        152,
        45,
        15,
        171,
        239,
        119,
        71,
        83,
        154,
        86,
        18,
        169,
        13,
        109,
        37,
        238,
        128,
        163,
        129,
        126,
        193,
        222,
        2,
        48,
    ),
)

# A fake block generated in december 2021.
obsolete_block = Block(
    time=1640034528,
    id=UUID("a0949845-2d58-45fe-9d54-913cff2da042"),
    link_id=link_id,
    key=(
        152,
        45,
        15,
        171,
        239,
        119,
        71,
        83,
        154,
        86,
        18,
        169,
        13,
        109,
        37,
        238,
        128,
        163,
        129,
        126,
        193,
        222,
        2,
        48,
    ),
)

qos = {"Key_chunk_size": 64, "Max_bps": 5, "Min_bps": 2, "TTL": 120, "Jitter": 10,
       "Priority": 0, "Timeout": 120}
