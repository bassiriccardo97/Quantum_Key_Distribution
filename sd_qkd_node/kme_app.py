"""Main app."""
from typing import Final

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from sd_qkd_node.configs import Config
from sd_qkd_node.database import local_models, local_db, shared_db
from sd_qkd_node.model.errors import BadRequest, ServiceUnavailable, Unauthorized
from sd_qkd_node.routers.kme import dec_keys, enc_keys, status, key_relay, block_used
from sd_qkd_node.routers.sdn_agent import open_key_session, register_app, link_confirmed, close_connection

app: Final[FastAPI] = FastAPI(
    debug=Config.DEBUG,
    title=f"{Config.KME_IP}:{Config.SAE_TO_KME_PORT}",
    responses={
        400: {"model": BadRequest},
        401: {"model": Unauthorized},
        503: {"model": ServiceUnavailable},
    },
)

app.include_router(enc_keys.router, prefix=Config.KME_BASE_URL)
app.include_router(dec_keys.router, prefix=Config.KME_BASE_URL)
app.include_router(status.router, prefix=Config.KME_BASE_URL)
app.include_router(key_relay.router, prefix=Config.KME_BASE_URL)
app.include_router(block_used.router, prefix=Config.KME_BASE_URL)
app.include_router(open_key_session.router, prefix=Config.AGENT_BASE_URL)
app.include_router(register_app.router, prefix=Config.AGENT_BASE_URL)
app.include_router(link_confirmed.router, prefix=Config.AGENT_BASE_URL)
app.include_router(close_connection.router, prefix=Config.AGENT_BASE_URL)


@app.get("/", include_in_schema=False)
async def redirect() -> RedirectResponse:
    """Redirect to docs."""
    return RedirectResponse("/docs", 302)


@app.on_event("startup")
async def startup() -> None:
    """Create ORM tables inside the database, if not already present."""
    await local_models.create_all()
    await local_db.connect()
    await shared_db.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    """Disconnect from shared DB."""
    await local_models.drop_all()
    await local_db.disconnect()
    await shared_db.disconnect()


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
