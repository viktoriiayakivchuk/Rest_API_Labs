import uuid
from typing import List, Optional, Tuple

_books_db = []

class BookRepository:
    @staticmethod
    def get_all(
        status: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[dict], int]:
        query_set = _books_db

        if status:
            query_set = [b for b in query_set if b.get("status") == status]
        if author:
            query_set = [b for b in query_set if author.lower() in b.get("author", "").lower()]

        total_count = len(query_set)
        
        items = query_set[offset : offset + limit]
        
        return items, total_count

    @staticmethod
    def get_by_id(book_id: str) -> Optional[dict]:
        target_id = str(book_id)
        for book in _books_db:
            if str(book.get("id")) == target_id:
                return book
        return None

    @staticmethod
    def add(book_data: dict) -> dict:
        _books_db.append(book_data)
        return book_data

    @staticmethod
    def delete(book_id: str) -> bool:
        target_id = str(book_id)
        for i, book in enumerate(_books_db):
            if str(book.get("id")) == target_id:
                _books_db.pop(i)
                return True
        return False