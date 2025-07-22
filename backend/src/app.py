import traceback
from fastapi import FastAPI, Request, Response
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from routes import checks, users, limiter
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError
import logging

load_dotenv()

app = FastAPI(debug=True)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logger = logging.getLogger("uvicorn.error")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get first error message
    error_msg = "Invalid input"

    return JSONResponse(
        status_code=422,
        content={"detail": error_msg},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.error("Unhandled error" + str(exc), exc_info=True)
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


@app.get("/", tags=["Root"])
async def root():
    return Response("Server is ruuning")


app.include_router(checks.router, prefix="/api")
app.include_router(users.router, prefix="/api")
# app.include_router(webhooks.router, prefix="/webhooks")
