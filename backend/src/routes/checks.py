from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated
from pydantic import BaseModel, Field
from services.essay_checker import check_essay_with_ai
from controllers.db import PsycheckDB, get_db
from datetime import datetime, timezone

router = APIRouter()

# Regex pattern to prevent basic injection

mock_user = {
    "user_id": "mock_user",
    "credits": 10,
    "created_at": datetime.now(timezone.utc)
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

@router.post("/check-essay", tags=["Checks"])
async def check_essay(
    payload: CheckEssayPayload,
    request: Request,
    db: PsycheckDB = Depends(get_db)
):
    try:
        # user_details = authenticate_user(request)
        user_details = mock_user  # For testing purposes, replace with authenticate_user(request)
        user_id = user_details.get("user_id")

        user_obj = await db.get_user_obj(user_id)
        if not user_obj:
            user_obj = await db.create_user(user_id)

        if user_obj['credits'] <= 0:
            raise HTTPException(status_code=429, detail="Credits exhausted")

        results_data = check_essay_with_ai(
            question=payload.question,
            essay=payload.essay
        )

        new_test = await db.create_test(
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            results=results_data,
            question=payload.question,
            essay=payload.essay
        )

        user_obj['credits'] -= 1
        await db.update_user_obj(user_obj)

        return new_test

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/my-history", tags=["Checks"])
async def my_history(
    request: Request,
    db: PsycheckDB = Depends(get_db)
):
    user_details = mock_user
    user_id = user_details.get("user_id")
    tests = await db.get_user_tests(user_id)
    return {"tests": tests or []}


@router.get("/user-details", tags=["Checks"])
async def get_user(
    request: Request,
    db: PsycheckDB = Depends(get_db)
):
    user_details = mock_user
    user_id = user_details.get("user_id")

    user_obj = await db.get_user_obj(user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_obj
