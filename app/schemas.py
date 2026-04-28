from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from typing import Optional, List
from datetime import datetime

class BookRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    author: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=2, max_length=400)
    status: str = Field(..., min_length=2, max_length=40)
    year: int = Field(..., gt=0)

    @field_validator("title", "author", "description")
    @classmethod
    def check_not_empty(cls, v: str):
        if not v.strip():
            raise ValueError("Field cannot be empty or contain only spaces")
        return v

    @field_validator("title")
    @classmethod
    def title_validator(cls, v: str):
        if v.startswith("_"):
            raise ValueError("Title cannot start with an underscore")
        return v

    @field_validator("status")
    @classmethod
    def status_validator(cls, v: str):
        allowed_statuses = {"available", "issued", "borrowed"}
        val_lower = v.strip().lower()
        if val_lower not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return val_lower

    @field_validator("year")
    @classmethod
    def check_year(cls, v: int):
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(f"Year cannot be greater than the current year ({current_year})")
        return v

class BookResponse(BaseModel):
    id: UUID
    title: str
    author: str
    description: str
    status: str
    year: int
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedBookResponse(BaseModel):
    items: List[BookResponse]
    total: int
    limit: int
    offset: int
    next_page: Optional[str] = None
    prev_page: Optional[str] = None