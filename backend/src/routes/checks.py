from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated
from pydantic import BaseModel, Field
from services.essay_checker import check_essay_with_ai
from controllers.db import PsycheckDB, get_db
from datetime import datetime, timezone

router = APIRouter()

mock_user = {
    "user_id": "123"
}

class CheckEssayPayload(BaseModel):
    question: str = Field(
        ..., 
        min_length=10, 
        max_length=200, 
        description="The essay question"
    )
    essay: str = Field(
        ..., 
        min_length=50, 
        max_length=3000, 
        description="The essay text"
    )

class User(BaseModel):
    _id = str, Field(..., alias="_id")
    clerk_id: str
    credits: int
    created_at: datetime

class Test(BaseModel):
    user_id: str
    created_at: datetime
    results: dict
    question: str
    essay: str

async def auth_and_get_user(request: Request , db: PsycheckDB):
    # clerk_user_details = authenticate_user(request)
    clerk_user_details = mock_user 
    clerk_id = clerk_user_details.get("user_id")
    user_obj = await db.get_user_obj(clerk_id)
    if not user_obj:
        user_obj = await db.create_user(clerk_id)
    return user_obj

@router.post("/check-essay", tags=["Checks"], response_model=Test)
async def check_essay(
    payload: CheckEssayPayload,
    request: Request,
    db: PsycheckDB = Depends(get_db)
):
    try:
        user_obj = await auth_and_get_user(request, db)
        if not user_obj:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if user_obj['credits'] <= 0:
            raise HTTPException(status_code=429, detail="Credits exhausted")

        results_data = check_essay_with_ai(
            question=payload.question,
            essay=payload.essay
        )

        new_test = await db.create_test(
            user_id=user_obj['_id'],
            created_at=datetime.now(timezone.utc),
            results=results_data,
            question=payload.question,
            essay=payload.essay
        )

        user_obj['credits'] -= 1
        await db.update_user(_id=user_obj['_id'], user_details=user_obj)

        return new_test

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


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
