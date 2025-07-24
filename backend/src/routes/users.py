from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from controllers.db import PsycheckDB, get_db
from utils.ClerkAuth import auth_and_get_user
from routes.limiter import limiter

router = APIRouter(prefix="/users")


class User(BaseModel):
    _id = str, Field(..., alias="_id")
    clerk_id: str
    credits: int
    created_at: datetime
    last_credit_update: datetime


@router.get("/user-details", tags=["Users"], response_model=User)
@limiter.limit("20/minute")
async def get_user(request: Request, db: PsycheckDB = Depends(get_db)):
    user_obj = await auth_and_get_user(request, db)
    last_update = user_obj.get("last_credit_update")
    if last_update is not None and datetime.utcnow() - last_update > timedelta(days=1):
        user_obj = await db.update_user(
            _id=user_obj["_id"], credits=2, last_credit_update=datetime.utcnow()
        )
    if not user_obj:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_obj
