import traceback
from fastapi import FastAPI, Request
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes import checks, users
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError
import logging

load_dotenv()
app = FastAPI(debug=True)
logger = logging.getLogger("uvicorn.error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    # just let FastAPI's default handler run; override only if you need a custom body
    logger.warning("HTTP Exception: %s - Detail: %s", exc.status_code, exc.detail)
    return await fastapi.exception_handlers.http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    traceback.print_exc()

    logger.exception("Validation error occurred during request processing." + str(exc))

    # Get first error message
    error_msg = exc.errors()[0]["msg"] if exc.errors() else "Invalid input"

    return JSONResponse(
        status_code=422,
        content={"detail": error_msg},
    )


@app.exception_handler(PyMongoError)
async def mongo_exception_handler(request, exc):
    traceback.print_exc()
    logger.exception("Mongo error" + str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Unhandled error" + str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(checks.router, prefix="/api")
app.include_router(users.router, prefix="/api")
# app.include_router(webhooks.router, prefix="/webhooks")
