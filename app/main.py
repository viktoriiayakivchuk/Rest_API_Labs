from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api import router
from app.database import engine
from app.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ініціалізація БД при старті та очищення пулу з'єднань при зупинці.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="Library Management API",
    description="Advanced FastAPI logic with PostgreSQL, Pagination, and Validation",
    version="0.2.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Глобальний перехоплювач помилок бази даних.
    Захищає від витоку внутрішньої інформації про структуру БД.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "Помилка бази даних. Спробуйте пізніше."},
    )

@app.get("/", include_in_schema=False)
def root():
    """Перенаправлення на документацію Swagger"""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)