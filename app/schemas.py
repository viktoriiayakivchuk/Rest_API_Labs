from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from enum import Enum
from typing import Optional, List, Literal

class BookStatus(str, Enum):
    AVAILABLE = "наявна"
    ISSUED = "видана"

class BookRequest(BaseModel):
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

class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    description: Optional[str]
    year: int
    status: BookStatus

    model_config = ConfigDict(from_attributes=True)

class PaginatedBookResponse(BaseModel):
    items: List[BookResponse]
    total_count: int
    limit: int
    offset: int
    next_page: Optional[str] = None
    prev_page: Optional[str] = None

class BookQueryParams(BaseModel):
    status: Optional[BookStatus] = Field(None, description="Фільтр за статусом")
    author: Optional[str] = Field(None, description="Фільтр за автором")
    sort_by: Optional[Literal["title", "year"]] = Field(None, description="Сортувати за 'title' або 'year'")
    sort_order: Literal["asc", "desc"] = Field("asc", description="Порядок сортування")
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)