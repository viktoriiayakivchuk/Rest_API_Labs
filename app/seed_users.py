# app/seed_users.py

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.auth.models import User
from app.core.security import get_password_hash
from app.core.database import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def seed_users():
    users_to_seed = [
        {
            "username": "admin",
            "password": "books-admin"
        },
        {
            "username": "vika_kpi",
            "password": "securepassword123"
        }
    ]
    
    async with async_session() as session:
        for user_data in users_to_seed:
            hashed_pwd = await get_password_hash(user_data["password"])
            
            db_user = User(
                username=user_data["username"],
                hashed_password=hashed_pwd
            )
            session.add(db_user)
            
        try:
            await session.commit()
            print("Користувачі успішно додані до бази даних.")
        except Exception as e:
            await session.rollback()
            print(f"Помилка при сидуванні (можливо, користувачі вже існують): {e}")

if __name__ == "__main__":
    async def main():
        await seed_users()
        await engine.dispose()
        
    asyncio.run(main())