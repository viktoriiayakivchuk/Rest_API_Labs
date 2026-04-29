from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.books.router import router as books_router
from app.core.database import engine, Base # Додано Base
from app.exceptions import NotFoundError

# Імпортуємо моделі, щоб Base їх "побачив" перед створенням таблиць
from app.auth.models import User
from app.books.models import Book

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Цей блок примусово створить таблицю users, якщо її немає
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    

app = FastAPI(
    title="Library API IPZ-33", 
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.detail},
    )

health_router = APIRouter(prefix="/api", tags=["Health"])

@health_router.get("/health")
async def health():
    return {"status": "ok"}

# Підключаємо твої роутери
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(health_router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)