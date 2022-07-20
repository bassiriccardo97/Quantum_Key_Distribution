"""Main app."""
from typing import Final

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from sdn_controller.database import local_models, shared_models, local_db
from sdn_controller.model.errors import BadRequest, Unauthorized, ServiceUnavailable
from sdn_controller.routers import new_app, new_kme, new_link, close_connection, update_link

app: Final[FastAPI] = FastAPI(
    debug=True,
    title="SDN Controller",
    responses={
        400: {"model": BadRequest},
        401: {"model": Unauthorized},
        503: {"model": ServiceUnavailable},
    },
)

app.include_router(new_app.router)
app.include_router(new_kme.router)
app.include_router(new_link.router)
app.include_router(close_connection.router)
app.include_router(update_link.router)


@app.get("/", include_in_schema=False)
async def redirect() -> RedirectResponse:
    """Redirect to docs."""
    return RedirectResponse("/docs", 302)


@app.on_event("startup")
async def startup() -> None:
    """Create ORM tables inside the database, if not already present."""
    await local_models.create_all()
    await shared_models.create_all()

    await local_db.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    """Disconnect from shared DB."""
    await local_models.drop_all()
    await shared_models.drop_all()

    await local_db.disconnect()


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    _: Request, error: RequestValidationError
) -> JSONResponse:
    """Always return 400 for a RequestValidationError."""
    return JSONResponse(status_code=400, content={"message": str(error.errors()[0])})


@app.exception_handler(HTTPException)
async def error_handler(_: Request, exception: HTTPException) -> JSONResponse:
    """Always return a body of type sd_qkd_node.model.Error for an HTTPException."""
    return JSONResponse(
        status_code=exception.status_code, content={"message": exception.detail}
    )
