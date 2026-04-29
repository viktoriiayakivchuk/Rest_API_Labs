import os
import pytest
import uuid
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import text

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from app.main import app
from app.core.database import Base, engine, async_session
from app.books.models import Book

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())
    yield
    loop.run_until_complete(engine.dispose())

@pytest.fixture(autouse=True)
def reset_db_data():
    async def reset():
        async with async_session() as session:
            await session.execute(text("DELETE FROM books"))
            await session.execute(text("DELETE FROM users"))
            await session.commit()
            book = Book(
                title="1984",
                author="George Orwell",
                description="Dystopian novel",
                status="available",
                year_published=1949,
            )
            session.add(book)
            await session.commit()
    asyncio.run(reset())

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_client(client):
    user_data = {"username": "testuser", "password": "testpassword", "email": "test@kpi.ua", "full_name": "Test User"}
    client.post("/api/auth/register", json=user_data)
    login_data = {"username": "testuser", "password": "testpassword"}
    tokens = client.post("/api/auth/login", data=login_data).json()
    client.headers.update({"Authorization": f"Bearer {tokens['access_token']}"})
    return client

def test_auth_register_and_login(client):
    username = f"user_{uuid.uuid4().hex[:4]}"
    user_data = {"username": username, "password": "password123", "email": f"{username}@kpi.ua", "full_name": "New User"}
    assert client.post("/api/auth/register", json=user_data).status_code == 201
    assert client.post("/api/auth/login", data={"username": username, "password": "password123"}).status_code == 200

def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"username": "w_user", "password": "123", "email": "w@kpi.ua", "full_name": "W"})
    response = client.post("/api/auth/login", data={"username": "w_user", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Неправильне ім'я користувача або пароль"

def test_get_books_authorized(auth_client):
    response = auth_client.get("/api/books")
    assert response.status_code == 200
    data = response.json()
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    assert any(b["title"] == "1984" for b in items)

def test_create_book_validation_error(auth_client):
    invalid_book = {"title": "F", "author": "A", "description": "D", "status": "available", "year_published": 2099}
    assert auth_client.post("/api/books", json=invalid_book).status_code == 422

def test_get_book_by_id(auth_client):
    books_res = auth_client.get("/api/books")
    data = books_res.json()
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    book_id = items[0]["id"]

    response = auth_client.get(f"/api/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "1984"

def test_get_book_not_found(auth_client):
    random_id = str(uuid.uuid4())
    response = auth_client.get(f"/api/books/{random_id}")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_delete_book_authorized(auth_client):
    books_res = auth_client.get("/api/books")
    data = books_res.json()
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    book_id = items[0]["id"]

    del_res = auth_client.delete(f"/api/books/{book_id}")
    assert del_res.status_code == 200

    check_res = auth_client.get(f"/api/books/{book_id}")
    assert check_res.status_code == 404

def test_unauthorized_access_denied(client):
    assert client.get("/api/books").status_code == 401
    assert client.post("/api/books", json={"title": "Unauthorized"}).status_code == 401

def test_get_books_pagination(auth_client):
    new_book = {
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "description": "Dystopian",
        "status": "available",
        "year_published": 1932
    }
    auth_client.post("/api/books", json=new_book)

    response = auth_client.get("/api/books?limit=1&offset=0")
    assert response.status_code == 200
    data = response.json()
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    assert len(items) == 1
    
    if isinstance(data, dict) and "total" in data:
        assert data["total"] >= 2