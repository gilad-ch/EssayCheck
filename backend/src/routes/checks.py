from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from security.ClerkAuth import authenticate_user
from services.essay_checker import check_essay_with_ai
from controllers.db import PsycheckDB, get_db
from datetime import datetime, timedelta, timezone
from typing import Any, List

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
    last_credit_update: datetime

class CriterionResult(BaseModel):
    criterion: str
    score: float
    feedback: str

class ContentSectionResult(BaseModel):
    content_conclusion: Optional[str] = None
    score: float
    criterias: List[CriterionResult]

class LanguageSectionResult(BaseModel):
    language_conclusion: Optional[str] = None
    score: float
    criterias: List[CriterionResult]

class TestResults(BaseModel):
    length_conclusion: str
    complete_score: float
    task_topic: Optional[str] = None
    general_conclusion: str
    content: ContentSectionResult
    language: LanguageSectionResult
    suggestions: List[str]

class Test(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    created_at: datetime
    results: TestResults
    question: str
    essay: str

    class Config:
        allow_population_by_field_name = True  # lets you return either _id or id



async def auth_and_get_user(request: Request , db: PsycheckDB):
    clerk_user_details = authenticate_user(request)
    clerk_id = clerk_user_details.get("user_id")
    if not isinstance(clerk_id, str) or not clerk_id:
        raise HTTPException(401, "Invalid or missing user_id")
        
    user_obj = await db.get_user_obj(clerk_id)
    if not user_obj:
        user_obj = await db.create_user(clerk_id)
    return user_obj

async def check_essay_length(essay: str):
    essay_word_count = len(essay.split())
    essay_lines_count = essay_word_count // 12
    if essay_lines_count <= 10:
        raise HTTPException(400, "Essay too short")

    if essay_lines_count > 50:
        raise HTTPException(400, "Essay too long")
    return 

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

    await check_essay_length(payload.essay) # Preliminary check for essay length to avoid unnecessary LLM call

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

@router.get("/essay-results/{test_id}", tags=["Checks"], response_model=Test)
async def get_essay_results(
    test_id: Annotated[str, Field(..., description="The ID of the test", pattern="^[a-fA-F0-9]{24}$")],
    request: Request,
    db: PsycheckDB = Depends(get_db)
):
    user_obj = await auth_and_get_user(request, db)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    test = await db.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test['user_id'] != user_obj['_id']:
        raise HTTPException(status_code=403, detail="Forbidden")

    return test


@router.get("/user-details", tags=["Users"])
async def get_user(
    request: Request,
    db: PsycheckDB = Depends(get_db)
):
    user_obj = await auth_and_get_user(request, db)
    last_update = user_obj.get("last_credit_update")
    if last_update is not None and datetime.utcnow() - last_update > timedelta(days=1):
        user_obj = await db.update_user(
            _id=user_obj["_id"],
            credits=2,
            last_credit_update=datetime.utcnow()
        )
    if not user_obj:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user_obj

