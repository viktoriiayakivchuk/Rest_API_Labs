from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum
from datetime import datetime

class BookStatus(str, Enum):
    AVAILABLE = "наявна"
    ISSUED = "видана"

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=400)
    year: int = Field(..., gt=0)
    status: BookStatus = BookStatus.AVAILABLE

    @field_validator("title", "author")
    @classmethod
    def check_not_empty(cls, v: str):
        if not v.strip():
            raise ValueError("Поле не може бути порожнім або містити лише пробіли")
        return v

    @field_validator("year")
    @classmethod
    def check_year(cls, v: int):
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Рік не може бути більшим за поточний ({current_year})")
        return v

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: UUID = Field(default_factory=uuid4)
    model_config = ConfigDict(from_attributes=True)

class PaginatedBooks(BaseModel):
    items: List[Book]
    total_count: int
    limit: int
    offset: int
    next_page: Optional[str] = None
    prev_page: Optional[str] = None