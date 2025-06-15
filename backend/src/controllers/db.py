import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional, Dict, Any, List

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "psycheck"

logger = logging.getLogger(__name__)


class PsycheckDB:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db["users"]
        self.tests = db["tests"]

    # ------ user operations ------
    async def get_user_obj(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.users.find_one({"user_id": user_id})
        except Exception as e:
            logger.exception(f"Error fetching user {user_id}")
            return None

    async def create_user(self, user_id: str) -> Dict[str, Any]:
        user_obj = {
            "user_id": user_id,
            "credits": 2,
            "created_at": datetime.utcnow(),
        }
        try:
            await self.users.insert_one(user_obj)
            return user_obj
        except Exception as e:
            logger.exception(f"Error creating user {user_id}")
            raise

    async def update_user_obj(self, user_obj: Dict[str, Any]) -> None:
        try:
            await self.users.update_one(
                {"user_id": user_obj["user_id"]},
                {"$set": user_obj}
            )
        except Exception as e:
            logger.exception(f"Error updating user {user_obj.get('user_id')}")
            raise

    # ------ test operations ------
    async def create_test(
        self,
        user_id: str,
        created_at: datetime,
        results: dict,
        question: str,
        essay: str
    ) -> Dict[str, Any]:
        challenge = {
            "user_id": user_id,
            "created_at": created_at,
            "results": results,
            "question": question,
            "essay": essay
        }
        try:
            await self.tests.insert_one(challenge)
            return challenge
        except Exception as e:
            logger.exception(f"Error creating test for {user_id}")
            raise

    async def get_user_tests(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            cursor = self.tests.find({"user_id": user_id})
            return [doc async for doc in cursor]
        except Exception as e:
            logger.exception(f"Error getting tests for user {user_id}")
            return []


# Dependency for FastAPI
client = AsyncIOMotorClient(MONGO_URI)

def get_db() -> PsycheckDB:
    db = client[DB_NAME]
    return PsycheckDB(db)
