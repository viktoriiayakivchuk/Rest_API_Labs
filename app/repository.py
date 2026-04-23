import uuid
from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, asc, desc, or_, and_, Select
from app.models import BookModel

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        limit: int,
        sort_by: str,
        sort_order: str,
        cursor_val: Optional[Any] = None,
        cursor_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        author: Optional[str] = None
    ) -> List[BookModel]:
        query = select(BookModel)
        query = self._apply_filters(query, status, author)
        
        sort_col = getattr(BookModel, sort_by)
        
        if cursor_id is not None:
             query = self._apply_cursor(query, sort_col, sort_order, cursor_val, cursor_id)
             
        query = self._apply_sorting(query, sort_col, sort_order)

        result = await self.db.execute(query.limit(limit))
        return list(result.scalars().all())

    def _apply_filters(self, query: Select, status: Optional[str], author: Optional[str]) -> Select:
        if status:
            query = query.where(BookModel.status == status)
        if author:
            query = query.where(BookModel.author.ilike(f"%{author}%"))
        return query

    def _apply_cursor(self, query: Select, sort_col, sort_order: str, cursor_val: Any, cursor_id: uuid.UUID) -> Select:
        if cursor_val is not None:
            if sort_order == "desc":
                return query.where(
                    or_(
                        sort_col < cursor_val, 
                        and_(sort_col == cursor_val, BookModel.id < cursor_id)
                    )
                )
            else:
                return query.where(
                    or_(
                        sort_col > cursor_val, 
                        and_(sort_col == cursor_val, BookModel.id > cursor_id)
                    )
                )
        return query.where(BookModel.id > cursor_id)

    def _apply_sorting(self, query: Select, sort_col, sort_order: str) -> Select:
        if sort_order == "desc":
            return query.order_by(desc(sort_col), desc(BookModel.id))
        return query.order_by(asc(sort_col), asc(BookModel.id))

    async def get_total_count(self, status: Optional[str] = None, author: Optional[str] = None):
        stmt = select(func.count(BookModel.id))
        stmt = self._apply_filters(stmt, status, author)
        result = await self.db.execute(stmt)
        return result.scalar()

    async def get_by_id(self, book_id: uuid.UUID) -> Optional[BookModel]:
        stmt = select(BookModel).where(BookModel.id == book_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, book_data: dict) -> BookModel:
        book = BookModel(**book_data)
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete(self, book_id: uuid.UUID) -> bool:
        book = await self.get_by_id(book_id)
        if book:
            await self.db.delete(book)
            await self.db.commit()
            return True
        return False