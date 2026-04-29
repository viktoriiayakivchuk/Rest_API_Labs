import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from app.main import app
from app.database import get_db
from app.books.models import Base, BookModel
from app.books.schemas import BookStatus

# Створюємо окремий двигун для тестів
test_engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=False)
test_session = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

# Підміняємо базу в додатку
async def override_get_db():
    async with test_session() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Створюємо схему БД"""
    async def init():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init())
    yield
    # Після тестів видаляємо файл
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(autouse=True)
def clean_db():
    """Очищення та наповнення даними"""
    async def reset():
        async with test_session() as session:
            await session.execute(text("DELETE FROM books"))
            book = BookModel(
                title="1984",
                author="George Orwell",
                description="Dystopia",
                year=1949,
                status=BookStatus.AVAILABLE
            )
            session.add(book)
            await session.commit()
    asyncio.run(reset())

# --- ТЕСТИ ---

def test_read_books():
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json()["items"][0]["title"] == "1984"

def test_create_book():
    payload = {
        "title": "Animal Farm",
        "author": "George Orwell",
        "year": 1945,
        "status": "наявна"
    }
    response = client.post("/books/", json=payload)
    assert response.status_code == 201
    assert response.json()["title"] == "Animal Farm"

def test_pagination():
    client.post("/books/", json={"title": "Test", "author": "Auth", "year": 2000})
    response = client.get("/books/", params={"limit": 1, "offset": 0})
    data = response.json()
    assert data["total_count"] == 2
    assert len(data["items"]) == 1

def test_delete_book():
    books = client.get("/books/").json()
    book_id = books["items"][0]["id"]
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404