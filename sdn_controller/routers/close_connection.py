from typing import Final
from uuid import UUID

from fastapi import APIRouter

from sdn_controller.database.dbms import delete_ksid

router: Final[APIRouter] = APIRouter(tags=["close_connection"])


@router.post(
    path="/close_connection",
    summary="Close the connection between two SAEs",
    response_model_exclude_none=True,
    include_in_schema=True
)
async def close_connection(
        ksid: UUID
) -> None:
    """
    API to request the closure of a connection.
    """
    await delete_ksid(ksid)
