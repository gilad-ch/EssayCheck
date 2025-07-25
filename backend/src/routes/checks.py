from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from utils.ClerkAuth import auth_and_get_user
from services.essay_checker import check_essay_with_ai
from controllers.db import PsycheckDB, get_db
from datetime import datetime, timedelta, timezone
from typing import Any, List
from routes.limiter import limiter

router = APIRouter(prefix="/checks")


class CheckEssayPayload(BaseModel):
    question: str = Field(
        ..., min_length=1, max_length=3000, description="The essay question"
    )
    essay: str = Field(..., min_length=1, max_length=6000, description="The essay text")


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
        validate_by_name = True  # lets you return either _id or id


async def check_essay_length(essay: str):
    essay_word_count = len(essay.split())
    essay_lines_count = essay_word_count // 12
    if essay_lines_count <= 10:
        raise HTTPException(422, "Essay too short")

    if essay_lines_count > 50:
        raise HTTPException(422, "Essay too long")
    return


@router.post("/check-essay", response_model=Test, tags=["Checks"])
@limiter.limit("5/minute")
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

    await check_essay_length(
        payload.essay
    )  # Preliminary check for essay length to avoid unnecessary LLM call

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
        credits=user["credits"] - 1,
    )

    return test


@router.get("/my-history", tags=["Checks"], response_model=list[Test])
@limiter.limit("20/minute")
async def my_history(request: Request, db: PsycheckDB = Depends(get_db)):

    user_obj = await auth_and_get_user(request, db)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Unauthorized")
    tests = await db.get_user_tests(user_obj["_id"])
    return tests or []


@router.get("/essay-results/{test_id}", tags=["Checks"], response_model=Test)
@limiter.limit("20/minute")
async def get_essay_results(
    test_id: Annotated[
        str, Field(..., description="The ID of the test", pattern="^[a-fA-F0-9]{24}$")
    ],
    request: Request,
    db: PsycheckDB = Depends(get_db),
):
    user_obj = await auth_and_get_user(request, db)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Unauthorized")

    test = await db.get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    if test["user_id"] != user_obj["_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return test
