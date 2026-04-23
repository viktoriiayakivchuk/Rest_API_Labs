from app.models import BookModel
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int, offset: int, status: str = None, author: str = None):
        stmt = select(BookModel)
        if status:
            stmt = stmt.where(BookModel.status == status)
        if author:
            stmt = stmt.where(BookModel.author.ilike(f"%{author}%"))
        stmt = stmt.limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()
        
    async def get_total_count(self, status: str = None, author: str = None):
        stmt = select(func.count(BookModel.id))
        if status:
            stmt = stmt.where(BookModel.status == status)
        if author:
            stmt = stmt.where(BookModel.author.ilike(f"%{author}%"))
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get_by_id(self, book_id: UUID):
        stmt = select(BookModel).where(BookModel.id == book_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, book_data: dict):
        book = BookModel(**book_data)
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete(self, book_id: UUID):
        book = await self.get_by_id(book_id)
        if book:
            await self.db.delete(book)
            await self.db.commit()
            return True
        return False