import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "library_db")
