from sqlalchemy.ext.asyncio import AsyncSession
from repository import BookRepository
from schemas import BookCreate
from uuid import uuid4

class BookService:
    def __init__(self, db: AsyncSession):
        self.repo = BookRepository(db)

    async def get_books(self, limit: int, offset: int, status: str = None, author: str = None):
        items = await self.repo.get_all(limit=limit, offset=offset, status=status, author=author)
        
        total_count = await self.repo.get_total_count(status=status, author=author)
        
        return {
            "items": items,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }

    async def create_book(self, book_in: BookCreate):
        book_data = book_in.model_dump()
        if not book_data.get("id"):
            book_data["id"] = uuid4()
        return await self.repo.add(book_data)