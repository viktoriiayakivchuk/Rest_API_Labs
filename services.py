from repository import BookRepository
from schemas import BookCreate
from uuid import uuid4

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    async def get_books(self, status=None, author=None, sort_by=None):
        books = await self.repo.get_all()
        result = list(books)
        
        if status:
            result = [b for b in result if b["status"] == status]
        if author:
            result = [b for b in result if author.lower() in b["author"].lower()]
            
        if sort_by in ["title", "year"]:
            result = sorted(result, key=lambda x: x.get(sort_by, ""))
            
        return result

    async def create_book(self, book_in: BookCreate):
        book_dict = book_in.model_dump()
        book_dict["id"] = uuid4()
        return await self.repo.add(book_dict)