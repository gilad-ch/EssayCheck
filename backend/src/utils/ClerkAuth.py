from dotenv import load_dotenv
from fastapi import HTTPException, Depends, Request
from clerk_backend_api import Clerk, AuthenticateRequestOptions
import os

from controllers.db import PsycheckDB

load_dotenv()
CLERK_SECRET = os.getenv("CLERK_SECRET_KEY")
JWT_KEY = os.getenv("JWT_KEY")

if not CLERK_SECRET or not JWT_KEY:
    raise RuntimeError("Missing required Clerk environment variables")

clerk_sdk = Clerk(bearer_auth=CLERK_SECRET)


def authenticate_user(request: Request):
    request_state = clerk_sdk.authenticate_request(
        request,
        AuthenticateRequestOptions(
            authorized_parties=[
                "http://localhost:5173",
                "http://localhost:5174",
                "http://localhost:8080",
            ],
            jwt_key=JWT_KEY,
        ),
    )

    if not request_state.is_signed_in:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = request_state.payload.get("sub")
    return {"user_id": user_id}


async def auth_and_get_user(request: Request, db: PsycheckDB):
    clerk_user_details = authenticate_user(request)
    clerk_id = clerk_user_details.get("user_id")
    if not isinstance(clerk_id, str) or not clerk_id:
        raise HTTPException(401, "Invalid or missing user_id")

    user_obj = await db.get_user_obj(clerk_id)
    if not user_obj:
        user_obj = await db.create_user(clerk_id)
    return user_obj
