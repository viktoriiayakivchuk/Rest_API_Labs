from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import BookRepository
from app.schemas import BookCreate
from uuid import uuid4

class BookService:
    def __init__(self, db: AsyncSession):
        self.repo = BookRepository(db)

    async def get_books(self, limit: int, offset: int, status: str = None, author: str = None):
        items = await self.repo.get_all(limit=limit, offset=offset, status=status, author=author)
        total_count = await self.repo.get_total_count(status=status, author=author)
        
        base_url = "/books/"
        params = []
        if status: params.append(f"status={status}")
        if author: params.append(f"author={author}")
        
        query_str = "&".join(params)
        prefix = f"?{query_str}&" if query_str else "?"

        next_page = None
        if offset + limit < total_count:
            next_page = f"{base_url}{prefix}limit={limit}&offset={offset + limit}"

        prev_page = None
        if offset > 0:
            prev_offset = max(0, offset - limit)
            prev_page = f"{base_url}{prefix}limit={limit}&offset={prev_offset}"
        
        return {
            "items": items,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "next_page": next_page,
            "prev_page": prev_page
        }

    async def create_book(self, book_in: BookCreate):
        book_data = book_in.model_dump()
        if not book_data.get("id"):
            book_data["id"] = uuid4()
        return await self.repo.add(book_data)