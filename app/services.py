from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas import BookRequest, BookQueryParams
from app.repository import BookRepository

class BookService:
    def __init__(self):
        self.repository = BookRepository()

    async def get_books(self, params: BookQueryParams) -> dict:
        items, total = await self.repository.get_all(params)
        
        base_url = "/books"
        query_parts = []
        if params.status: query_parts.append(f"status={params.status}")
        if params.author: query_parts.append(f"author={params.author}")
        if params.sort_by: query_parts.append(f"sort_by={params.sort_by}&sort_order={params.sort_order}")
        
        query_str = "&".join(query_parts)
        prefix = f"{query_str}&" if query_str else ""

        next_page = None
        if params.offset + params.limit < total:
            next_page = f"{base_url}/?{prefix}limit={params.limit}&offset={params.offset + params.limit}"

        prev_page = None
        if params.offset > 0:
            prev_offset = max(0, params.offset - params.limit)
            prev_page = f"{base_url}/?{prefix}limit={params.limit}&offset={prev_offset}"
            
        return {
            "items": items,
            "total_count": total,
            "limit": params.limit,
            "offset": params.offset,
            "next_page": next_page,
            "prev_page": prev_page
        }

    async def get_book(self, book_id: str) -> Dict[str, Any]:
        book = await self.repository.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Книгу не знайдено")
        return book

    async def create_book(self, book_request: BookRequest) -> Dict[str, Any]:
        book_dict = book_request.model_dump()
        return await self.repository.add(book_dict)

    async def delete_book(self, book_id: str):
        deleted = await self.repository.delete(book_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Книгу не знайдено")
        return None