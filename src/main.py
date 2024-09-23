
import logging
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse

from core.config import uvicorn_options
from api.v1 import api_router
from core.logger import setup_logging


app = FastAPI(
    docs_url="/api/openapi",
)
logger = logging.getLogger("my_app")

app.include_router(api_router)

setup_logging()


@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        logger.error(f"{request.url} | HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail}
        )
    except Exception as e:
        logger.error(f"{request.url} | Error in application: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"}
        )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"{request.url} | Error in application: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"{request.url} | HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


if __name__ == '__main__':
    print(uvicorn_options)
    uvicorn.run(
        'main:app',
        **uvicorn_options
    )
