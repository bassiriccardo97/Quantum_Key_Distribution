from typing import Final

from fastapi import APIRouter

from sdn_controller.database.dbms import add_new_kme
from sdn_controller.model.new_kme import NewKmeResponse, NewKmeRequest

router: Final[APIRouter] = APIRouter(tags=["new_kme"])


@router.post(
    path="/new_kme",
    summary="Register a new KME",
    response_model=NewKmeResponse,
    response_model_exclude_none=True,
    include_in_schema=False
)
async def new_kme(
        request: NewKmeRequest
) -> NewKmeResponse:
    """
    API to add a new KME in the network.
    """
    kme: Final[NewKmeResponse] = await add_new_kme(request)

    return kme
