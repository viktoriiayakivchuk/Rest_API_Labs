from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from typing import Optional, List
from enum import Enum
from datetime import datetime

class BookStatus(str, Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"

class BookBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    author: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=2, max_length=400)
    year: int = Field(..., gt=0)
    status: BookStatus = BookStatus.AVAILABLE

    @field_validator("title", "author", "description")
    @classmethod
    def check_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Поле не може бути порожнім або містити лише пробіли")
        return v

    @field_validator("title")
    @classmethod
    def title_validator(cls, v: str) -> str:
        if v.startswith("_"):
            raise ValueError("Назва книги не може починатися з підкреслення")
        return v

    @field_validator("year")
    @classmethod
    def check_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Рік не може бути більшим за поточний ({current_year})")
        return v

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class PaginatedBookResponse(BaseModel):
    items: List[BookResponse]
    total: int
    limit: int
    offset: int
    next_page: Optional[str] = None
    prev_page: Optional[str] = None