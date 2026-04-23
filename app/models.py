from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")

client = AsyncIOMotorClient(MONGO_URL)
db = client.library_db  

books_collection = db.books