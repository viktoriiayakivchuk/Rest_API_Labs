from fastapi import APIRouter, HTTPException, status
from schemas import Book, BookCreate, BookStatus
from services import BookService
from uuid import UUID
from typing import List, Optional

router = APIRouter(prefix="/books", tags=["Books"])
service = BookService()

@router.get("/", response_model=List[Book])
async def get_all_books(
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    sort_by: Optional[str] = None
):
    return await service.get_books(status, author, sort_by)

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: UUID):
    # Використовуємо репозиторій через сервіс
    book = await service.repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    return book

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book: BookCreate):
    return await service.create_book(book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    # DELETE має бути ідемпотентним (204 незалежно від того, чи була книга)
    await service.repo.delete(book_id)
    return None