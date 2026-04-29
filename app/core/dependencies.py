import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Request
from redis.asyncio import Redis

from app.core.database import async_session
from app.core.security import verify_token_type, oauth2_scheme, SECRET_KEY, ALGORITHM
from app.core.rate_limiter import RedisRateLimiter
from app.database.redis import get_redis  

limiter = RedisRateLimiter()

async def get_db():
    async with async_session() as session:
        yield session

async def rate_limit(request: Request, redis: Redis = Depends(get_redis)):
    user_id = None
    token = request.headers.get("Authorization")
    
    if token and token.startswith("Bearer "):
        try:
            raw_token = token.split(" ")[1]
            payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
        except jwt.PyJWTError:
            pass 
            
    if user_id:
        key = f"ratelimit:user:{user_id}"
        limit = 10
    else:
        forwarded_for = request.headers.get("X-Forwarded-For")
        host = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "unknown")
        key = f"ratelimit:ip:{host}"
        limit = 2
        
    allowed = await limiter.check_allowance(key, limit, redis_client=redis)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too Many Requests"
        )

async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)):
    from app.auth.repository import UserRepository
    
    user_id = verify_token_type(token, "access")
    
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_auth_service(db: AsyncSession = Depends(get_db)):
    from app.auth.repository import UserRepository
    from app.auth.service import AuthService
    return AuthService(repository=UserRepository(db))

async def get_book_service(db: AsyncSession = Depends(get_db)):
    from app.books.repository import BookRepository
    from app.books.service import BookService
    return BookService(repository=BookRepository(db))