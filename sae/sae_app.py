"""Main app."""
from typing import Final

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from sae.model.errors import BadRequest, Unauthorized, ServiceUnavailable
from sae.routers import assign_ksid, ask_connection, ask_key, ask_close_connection, debugging_start_connection

app: Final[FastAPI] = FastAPI(
    debug=True,
    title="Sae",
    responses={
        400: {"model": BadRequest},
        401: {"model": Unauthorized},
        503: {"model": ServiceUnavailable},
    },
)

app.include_router(assign_ksid.router)
app.include_router(ask_connection.router)
app.include_router(ask_key.router)
app.include_router(ask_close_connection.router)
app.include_router(debugging_start_connection.router)


@app.get("/", include_in_schema=False)
async def redirect() -> RedirectResponse:
    """Redirect to docs."""
    return RedirectResponse("/docs", 302)


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
