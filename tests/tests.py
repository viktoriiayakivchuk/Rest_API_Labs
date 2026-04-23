import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Налаштування тестової БД
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from app.main import app
from app.database import get_db
from app.models import Base, BookModel
from app.schemas import BookStatus

# Створюємо двигун та сесію для тестів
test_engine = create_async_engine("sqlite+aiosqlite:///./test.db", echo=False)
AsyncTestSession = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

# Підміна залежності бази даних
async def override_get_db():
    async with AsyncTestSession() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    async def init():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init())
    yield
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(autouse=True)
def clean_db():
    async def reset():
        async with AsyncTestSession() as session:
            await session.execute(text("DELETE FROM books"))
            await session.commit()
    asyncio.run(reset())

# --- ТЕСТИ ---

def test_create_book():
    payload = {
        "title": "1984",
        "author": "George Orwell",
        "year": 1949,
        "status": "наявна",
        "description": "Класична антиутопія"
    }
    response = client.post("/books/", json=payload)
    assert response.status_code == 201
    assert response.json()["title"] == "1984"
    assert "id" in response.json()

def test_get_book_by_id():
    # Створюємо книгу (автор обов'язково > 2 символів)
    post_resp = client.post("/books/", json={
        "title": "Test Book", 
        "author": "Author", 
        "year": 2020
    })
    assert post_resp.status_code == 201
    book_id = post_resp.json()["id"]
    
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"

def test_delete_book():
    post_resp = client.post("/books/", json={
        "title": "To Delete", 
        "author": "Author", 
        "year": 2000
    })
    book_id = post_resp.json()["id"]
    
    del_resp = client.delete(f"/books/{book_id}")
    assert del_resp.status_code == 204
    
    # Перевіряємо, що книги більше немає
    assert client.get(f"/books/{book_id}").status_code == 404

def test_validation_error():
    # Перевірка валідації: порожній заголовок
    payload = {"title": " ", "author": "Valid Author", "year": 2020}
    response = client.post("/books/", json=payload)
    assert response.status_code == 422