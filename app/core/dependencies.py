import uuid
import logging
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

# Імпорти для Auth & Books
from app.auth.models import User
from app.auth.repository import UserRepository
from app.auth.service import AuthService
from app.books.repository import BookRepository
from app.books.service import BookService

# Налаштування простого логування для діагностики
logger = logging.getLogger(__name__)

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))

async def get_book_service(db: AsyncSession = Depends(get_db)) -> BookService:
    return BookService(BookRepository(db))

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(settings.oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не вдалося валідувати облікові дані",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодування токена
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_val = payload.get("sub")
        
        if user_id_val is None:
            print("DEBUG: Payload 'sub' is missing")
            raise credentials_exception
            
        user_id = uuid.UUID(str(user_id_val))
            
    except (JWTError, ValueError, AttributeError) as e:
        print(f"DEBUG: JWT Decode Error: {e}")
        raise credentials_exception

    repository = UserRepository(db)
    user = await repository.get_by_id(user_id)
    
    if user is None:
        print(f"DEBUG: User with ID {user_id} not found in database")
        raise credentials_exception
        
    return user