from models import books_storage
from uuid import UUID

class BookRepository:
    async def get_all(self):
        return books_storage

    async def get_by_id(self, book_id: UUID):
        return next((b for b in books_storage if b["id"] == book_id), None)

    async def add(self, book_data: dict):
        books_storage.append(book_data)
        return book_data

    async def delete(self, book_id: UUID):
        for i, b in enumerate(books_storage):
            if b["id"] == book_id:
                del books_storage[i]
                return True
        return False