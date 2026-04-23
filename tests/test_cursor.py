import pytest
import os
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Окрема БД для тестів пагінації
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_cursor.db"

from app.main import app
from app.database import get_db
from app.models import Base  

test_engine = create_async_engine("sqlite+aiosqlite:///./test_cursor.db", echo=False)
AsyncTestSession = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

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
    if os.path.exists("./test_cursor.db"):
        os.remove("./test_cursor.db")

@pytest.fixture(autouse=True)
def clean_db():
    async def reset():
        async with AsyncTestSession() as session:
            await session.execute(text("DELETE FROM books"))
            await session.commit()
    asyncio.run(reset())

# --- ТЕСТИ ПАГІНАЦІЇ ---

def test_pagination_logic():
    for i in range(3):
        client.post("/books/", json={
            "title": f"Book {i}", 
            "author": "Author", 
            "year": 2000 + i
        })

    r1 = client.get("/books/", params={"limit": 2, "sort_by": "year", "order": "asc"})
    data1 = r1.json()
    assert len(data1["items"]) == 2
    cursor = data1["next_cursor"]
    assert cursor is not None

    r2 = client.get("/books/", params={"limit": 2, "cursor": cursor, "sort_by": "year", "order": "asc"})
    data2 = r2.json()
    assert len(data2["items"]) == 1
    assert data2["items"][0]["title"] == "Book 2"
    assert data2["next_cursor"] is None

def test_sorting_by_title_desc():
    client.post("/books/", json={"title": "Apple", "author": "Author", "year": 2010})
    client.post("/books/", json={"title": "Zebra", "author": "Author", "year": 2020})

    resp = client.get("/books/", params={"sort_by": "title", "order": "desc"})
    items = resp.json()["items"]
    assert items[0]["title"] == "Zebra"
    assert items[1]["title"] == "Apple"

def test_invalid_cursor_format():
    response = client.get("/books/", params={"cursor": "not_a_base64_string"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid cursor format"

def test_empty_database_pagination():
    """Перевірка пагінації, коли в базі немає книг"""
    # clean_db вже очистив базу, тому просто робимо запит
    response = client.get("/books/", params={"limit": 10})
    data = response.json()
    
    assert response.status_code == 200
    assert data["items"] == []
    assert data["total_count"] == 0
    assert data["next_cursor"] is None

def test_pagination_last_page():
    """Перевірка, що на останній сторінці курсор зникає"""
    client.post("/books/", json={"title": "B1", "author": "Author", "year": 2000})
    
    # Запитуємо ліміт 5, маючи лише 1 книгу
    response = client.get("/books/", params={"limit": 5})
    data = response.json()
    
    assert len(data["items"]) == 1
    assert data["next_cursor"] is None

def test_tie_breaking_with_same_years():
    """Критичний тест: пагінація книг з однаковим роком видання"""
    # Створюємо 3 книги з одним роком
    for i in range(3):
        client.post("/books/", json={
            "title": f"Book {i}", 
            "author": "Author", 
            "year": 2022
        })
    
    # Отримуємо першу книгу
    r1 = client.get("/books/", params={"limit": 1, "sort_by": "year", "order": "asc"})
    cursor = r1.json()["next_cursor"]
    
    # Отримуємо другу книгу за курсором
    r2 = client.get("/books/", params={"limit": 1, "cursor": cursor, "sort_by": "year", "order": "asc"})
    
    assert r2.status_code == 200
    assert len(r2.json()["items"]) == 1
    # Перевіряємо, що це інша книга, хоча рік той самий
    assert r2.json()["items"][0]["id"] != r1.json()["items"][0]["id"]