import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "psycheck"

logger = logging.getLogger(__name__)


def oid_to_str(doc):
    """Recursively convert ObjectId to string in a dict or list"""
    if isinstance(doc, dict):
        return {k: oid_to_str(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [oid_to_str(i) for i in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    return doc

class PsycheckDB:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db["users"]
        self.tests = db["tests"]

    # ------ user operations ------
class PsycheckDB:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db["users"]
        self.tests = db["tests"]

    # ------ user operations ------
    async def get_user_obj(self, clerk_id: str) -> Optional[Dict[str, Any]]:
        try:
            user_obj = await self.users.find_one({"clerk_id": clerk_id})
            return oid_to_str(user_obj) if user_obj else None
        except Exception:
            logger.exception(f"Error fetching user {clerk_id}")
            return None

    async def create_user(self, clerk_id: str) -> Dict[str, Any]:
        user_obj = {
            "clerk_id": clerk_id,
            "credits": 2,
            "created_at": datetime.utcnow(),
            "last_credit_update": datetime.utcnow(),
        }
        try:
            result = await self.users.insert_one(user_obj)
            user_obj["_id"] = result.inserted_id
            return oid_to_str(user_obj)
        except Exception:
            logger.exception(f"Error creating user {clerk_id}")
            raise

    async def update_user(self, _id, **user_details):
        logger.debug(f"Updating user: {_id} with details {user_details}")
        filter_query = {"_id": ObjectId(_id)}
        try:
            await self.users.update_one(filter_query, {"$set": {**user_details}})
            logger.debug(f"User {_id} updated successfully.")
        except Exception as e:
            logger.error(f"Failed to update user {_id}: {e}")


    # ------ test operations ------
    async def create_test(
        self,
        user_id: str,
        created_at: datetime,
        results: dict,
        question: str,
        essay: str
    ) -> Dict[str, Any]:
        test = {
            "user_id": ObjectId(user_id),
            "created_at": created_at,
            "results": results,
            "question": question,
            "essay": essay
        }
        try:
            result = await self.tests.insert_one(test)
            test["_id"] = result.inserted_id
            return oid_to_str(test)
        except Exception:
            logger.exception(f"Error creating test for {user_id}")
            raise

    async def get_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        try:
            test = await self.tests.find_one({"_id": ObjectId(test_id)})
            if test:
                test['_id'] = str(test['_id'])
                test['user_id'] = str(test['user_id'])
            return test
        except Exception:
            logger.exception(f"Error fetching test {test_id}")
            return None



    async def get_user_tests(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            tests_cursor = self.tests.find({"user_id": ObjectId(user_id)})
            tests = await tests_cursor.to_list(length=None)

            for test in tests:
                test['_id'] = str(test['_id'])
                test['user_id'] = str(test['user_id'])
            return tests

        except Exception:
            logger.exception(f"Error getting tests for user {user_id}")
            return []




# Dependency for FastAPI
client = AsyncIOMotorClient(MONGO_URI)

def get_db() -> PsycheckDB:
    db = client[DB_NAME]
    return PsycheckDB(db)
