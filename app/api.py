from typing import List
from fastapi import APIRouter, Depends, status, Request
from app.schemas import BookRequest, BookResponse, PaginatedBookResponse, BookQueryParams
from app.services import BookService

router = APIRouter(prefix="/books", tags=["Books"])

async def get_service(request: Request):
    """
    Ця функція тепер отримує доступ до бази через request.app.
    Це критично для коректної роботи тестів та уникнення помилок Event Loop.
    """
    service = BookService()
    service.repository.collection = request.app.mongodb_db["books"]
    return service

@router.get("/", response_model=PaginatedBookResponse)
async def get_all_books(
    params: BookQueryParams = Depends(),
    service: BookService = Depends(get_service),
):
    return await service.get_books(params)

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str, 
    service: BookService = Depends(get_service)
):
    return await service.get_book(book_id)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookResponse)
async def create_book(
    book: BookRequest, 
    service: BookService = Depends(get_service)
):
    return await service.create_book(book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str, 
    service: BookService = Depends(get_service)
):
    return await service.delete_book(book_id)