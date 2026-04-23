import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

def get_test_engine():
    return create_async_engine(TEST_DATABASE_URL, echo=False)

async def override_get_db():
    engine = get_test_engine()
    TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    # Ініціалізуємо БД синхронним обгортком перед запуском тестів
    async def init():
        engine = get_test_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()
    
    asyncio.run(init())
    yield
    
    # Видаляємо тестову БД після тестів
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except OSError:
            pass

client = TestClient(app)

def test_library_api():
    # --- 1. ТЕСТ СТВОРЕННЯ КНИГИ (POST) ---
    new_book = {
        "title": "The Call of Cthulhu",
        "author": "H.P. Lovecraft",
        "description": "A classic horror story",
        "year": 1928,
        "status": "наявна"
    }
    response = client.post("/books/", json=new_book)
    assert response.status_code == 201
    book_data = response.json()
    assert book_data["title"] == new_book["title"]
    assert "id" in book_data
    book_id = book_data["id"]

    # --- 2. ТЕСТ ОТРИМАННЯ ВСІХ КНИГ (GET) ---
    response = client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1

    # --- 3. ТЕСТ ОТРИМАННЯ ПО ID (GET) ---
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id

    # --- 4. ТЕСТ ФІЛЬТРАЦІЇ ---
    response = client.get("/books/", params={"author": "Lovecraft"})
    assert response.status_code == 200
    data = response.json()
    assert all("Lovecraft" in b["author"] for b in data["items"])

    # --- 5. ТЕСТ ВИДАЛЕННЯ (DELETE) ---
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    # --- 6. ТЕСТ ІДЕМПОТЕНТНОСТІ DELETE ---
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204