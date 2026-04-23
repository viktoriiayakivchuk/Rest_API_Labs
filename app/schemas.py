from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum

class BookStatus(str, Enum):
    AVAILABLE = "наявна"
    ISSUED = "видана"

class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=2)
    description: Optional[str] = None
    year: int = Field(..., gt=0)
    status: BookStatus = BookStatus.AVAILABLE

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