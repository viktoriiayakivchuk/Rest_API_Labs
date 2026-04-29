import uuid
from fastapi import Request
from app.books.models import Book
from app.books.schemas import BookCreate, PaginatedBookResponse
from app.auth.schemas import MessageResponse
from app.books.repository import BookRepository
from app.exceptions import NotFoundError
from app.core.utils import generate_pagination_links

class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def get_books(
        self,
        request: Request,
        status: str | None = None,
        author: str | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ) -> PaginatedBookResponse:
        items, total = await self.repository.get_all(
            status=status,
            author=author,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )

        links = generate_pagination_links(request, total, limit, offset)

        return PaginatedBookResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            next_page=links["next_page"],
            prev_page=links["prev_page"]
        )

    async def get_book(self, book_id: uuid.UUID) -> Book:
        book = await self.repository.get_by_id(book_id)
        if not book:
            raise NotFoundError(detail="Книгу не знайдено")
        return book

    async def create_book(self, book_in: BookCreate) -> Book:
        book = Book(
            title=book_in.title,
            author=book_in.author,
            description=book_in.description,
            status=book_in.status,
            year=book_in.year,
        )
        return await self.repository.create(book)

    async def delete_book(self, book_id: uuid.UUID) -> MessageResponse:
        deleted = await self.repository.delete(book_id)
        if not deleted:
            raise NotFoundError(detail="Книгу не знайдено для видалення")
        return MessageResponse(message="Книгу успішно видалено")