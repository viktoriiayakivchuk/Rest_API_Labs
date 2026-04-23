from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas import Book, BookCreate, BookStatus, PaginatedBooks, BookSortField, SortOrder
from app.services import BookService
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter(prefix="/books", tags=["Books"])

def get_service(db: AsyncSession = Depends(get_db)) -> BookService:
    return BookService(db)

@router.get("/", response_model=PaginatedBooks)
async def get_all_books(
    status: Optional[BookStatus] = None,
    author: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    sort_by: BookSortField = Query(BookSortField.ID),
    order: SortOrder = Query(SortOrder.ASC),
    cursor: Optional[str] = Query(None, description="Base64 курсор для пагінації"),
    service: BookService = Depends(get_service)
):
    return await service.get_books(
        limit=limit, 
        sort_by=sort_by.value, 
        sort_order=order.value, 
        cursor=cursor, 
        status=status, 
        author=author
    )

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: UUID, service: BookService = Depends(get_service)):
    book = await service.repo.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    return book

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(book: BookCreate, service: BookService = Depends(get_service)):
    return await service.create_book(book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, service: BookService = Depends(get_service)):
    success = await service.repo.delete(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Книгу не знайдено")
    return None