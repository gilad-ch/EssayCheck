from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated
from pydantic import BaseModel, Field
from security.ClerkAuth import authenticate_user
from services.essay_checker import check_essay_with_ai
from controllers.db import PsycheckDB, get_db
from datetime import datetime, timezone

router = APIRouter()

class CheckEssayPayload(BaseModel):
    question: str = Field(
        ..., 
        min_length=10, 
        max_length=3000, 
        description="The essay question"
    )
    essay: str = Field(
        ..., 
        min_length=50, 
        max_length=6000, 
        description="The essay text"
    )

class User(BaseModel):
    _id = str, Field(..., alias="_id")
    clerk_id: str
    credits: int
    created_at: datetime

class Test(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    created_at: datetime
    results: dict
    question: str
    essay: str

    class Config:
        allow_population_by_field_name = True  # lets you return either _id or id

async def auth_and_get_user(request: Request , db: PsycheckDB):
    clerk_user_details = authenticate_user(request)
    clerk_id = clerk_user_details.get("user_id")
    user_obj = await db.get_user_obj(clerk_id)
    if not user_obj:
        user_obj = await db.create_user(clerk_id)
    return user_obj

@router.post("/check-essay", response_model=Test, tags=["Checks"])
async def check_essay(
    payload: CheckEssayPayload,
    request: Request,
    db: PsycheckDB = Depends(get_db),
):
    user = await auth_and_get_user(request, db)
    if not user:
        raise HTTPException(401, "Unauthorized")

    if user["credits"] <= 0:
        raise HTTPException(429, "Credits exhausted")

    results = await check_essay_with_ai(
        question=payload.question,
        essay=payload.essay,
    )

    test = await db.create_test(
        user_id=user["_id"],
        created_at=datetime.now(timezone.utc),
        results=results,
        question=payload.question,
        essay=payload.essay,
    )

    await db.update_user(
        _id=user["_id"],
        credits = user["credits"] - 1,
    )

    return test



@router.get("/my-history", tags=["Checks"], response_model=list[Test])
async def my_history(
    request: Request,
    db: PsycheckDB = Depends(get_db)
):

    user_obj = await auth_and_get_user(request, db)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tests = await db.get_user_tests(user_obj['_id'])
    return tests or []



@router.get("/user-details", tags=["Checks"])
async def get_user(
    request: Request,
    db: PsycheckDB = Depends(get_db)
):
    user_obj = await auth_and_get_user(request, db)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_obj

