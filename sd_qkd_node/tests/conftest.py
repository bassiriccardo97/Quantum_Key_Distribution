"""Fixtures for pytest testing."""
from typing import AsyncIterator

from httpx import AsyncClient
from pytest_asyncio import fixture

from sd_qkd_node import kme_app
from sd_qkd_node.database import orm, local_models, shared_models
from sd_qkd_node.tests.examples import key_1, key_2, block_1, block_2, obsolete_block


@fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Return a client stub."""
    async with AsyncClient(app=kme_app.app, base_url="http://test") as client:
        await local_models.create_all()
        await shared_models.create_all()
        yield client
        await local_models.drop_all()
        await shared_models.drop_all()


@fixture
async def init_blocks() -> None:
    """Add example blocks into the database."""
    await orm.Block.create_from_qcs_block(block_1)
    await orm.Block.create_from_qcs_block(block_2)
    await orm.Block.create_from_qcs_block(obsolete_block)


@fixture
async def init_keys() -> None:
    """Add example keys into the database."""
    await orm.Key.objects.create(key_id=key_1.key_id, instructions=key_1.instructions)
    await orm.Key.objects.create(key_id=key_2.key_id, instructions=key_2.instructions)
