from pydantic import BaseModel, Field
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