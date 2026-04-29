import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://user:password@library_db:5432/library_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass