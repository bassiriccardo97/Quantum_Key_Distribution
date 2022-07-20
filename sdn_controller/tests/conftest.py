"""Fixtures for pytest testing."""
from typing import AsyncIterator, Final

from httpx import AsyncClient
from pytest_asyncio import fixture

from sdn_controller import sdn_app
from sdn_controller.database import local_models, shared_models, orm
from sdn_controller.database.orm import Kme


@fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Return a client stub."""
    async with AsyncClient(app=sdn_app.app, base_url="http://test") as client:
        await local_models.create_all()
        await shared_models.create_all()
        yield client
        await local_models.drop_all()
        await shared_models.drop_all()


@fixture
async def init_kmes() -> list[Kme]:
    """Add example KMEs into the database."""
    kme1: Final[Kme] = await orm.Kme.objects.create(ip="localhost", port=5000)
    kme2: Final[Kme] = await orm.Kme.objects.create(ip="localhost", port=5001)
    return [kme1, kme2]
