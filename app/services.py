import uuid
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository import BookRepository
from app.schemas import BookCreate
from app.utils import encode_cursor, decode_cursor

class BookService:
    def __init__(self, db: AsyncSession):
        self.repo = BookRepository(db)

    async def get_books(
        self, 
        limit: int, 
        sort_by: str, 
        sort_order: str, 
        cursor: Optional[str] = None, 
        status: Optional[str] = None, 
        author: Optional[str] = None
    ):
        cursor_val, cursor_id = None, None
        
        if cursor:
            cursor_val, cursor_id = decode_cursor(cursor)
            if cursor_val is None and cursor_id is None:
                raise HTTPException(status_code=400, detail="Invalid cursor format")
            
            if sort_by == "year":
                try:
                    cursor_val = int(cursor_val)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Cursor value must be an integer for year sorting")

        items = await self.repo.get_all(
            limit=limit + 1,
            sort_by=sort_by,
            sort_order=sort_order,
            cursor_val=cursor_val,
            cursor_id=cursor_id,
            status=status,
            author=author
        )

        total_count = await self.repo.get_total_count(status=status, author=author)

        next_cursor = None
        if len(items) > limit:
            last_item = items[limit - 1]
            items = items[:limit]
            
            sort_val = getattr(last_item, sort_by)
            next_cursor = encode_cursor(last_item.id, sort_by, sort_val)

        return {
            "items": items,
            "total_count": total_count,
            "limit": limit,
            "next_cursor": next_cursor
        }

    async def create_book(self, book_in: BookCreate):
        book_data = book_in.model_dump()
        if not book_data.get("id"):
            book_data["id"] = uuid.uuid4()
        return await self.repo.add(book_data)