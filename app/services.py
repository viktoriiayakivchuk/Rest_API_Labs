import uuid
from urllib.parse import urlencode
from app.schemas import BookRequest
from app.repository import BookRepository

class BookService:
    @staticmethod
    def get_all_books(limit: int = 10, offset: int = 0, status: str = None, author: str = None):
        items, total_count = BookRepository.get_all(
            limit=limit, 
            offset=offset, 
            status=status, 
            author=author
        )
        
        filter_params = {}
        if status: filter_params["status"] = status
        if author: filter_params["author"] = author

        def _build_url(lim: int, off: int) -> str:
            params = {**filter_params, "limit": lim, "offset": off}
            return f"/books?{urlencode(params)}"

        next_page = None
        if offset + limit < total_count:
            next_page = _build_url(limit, offset + limit)

        prev_page = None
        if offset > 0:
            prev_page = _build_url(limit, max(0, offset - limit))
        
        return {
            "items": items,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "next_page": next_page,
            "prev_page": prev_page
        }

    @staticmethod
    def get_book_by_id(book_id: str):
        return BookRepository.get_by_id(book_id)

    @staticmethod
    def create_book(book_data: dict):
        if not book_data.get("id"):
            book_data["id"] = uuid.uuid4()
        return BookRepository.add(book_data)

    @staticmethod
    def delete_book(book_id: str):
        return BookRepository.delete(book_id)