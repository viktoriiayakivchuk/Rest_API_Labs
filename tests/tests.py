import pytest
import uuid
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_current_user, get_book_service

client = TestClient(app)

mock_book_data = {
    "id": str(uuid.uuid4()),
    "title": "Test Book",
    "author": "Vika",
    "description": "Lab 7 description",
    "year": 2026,
    "status": "available"
}

async def mock_get_books_call(*args, **kwargs):
    return {
        "items": [mock_book_data],
        "total": 1,
        "limit": 10,
        "offset": 0
    }

@pytest.fixture(autouse=True)
def setup_overrides():
    mock_service = AsyncMock()
    mock_service.get_books.side_effect = mock_get_books_call
    mock_service.get_book.return_value = mock_book_data
    mock_service.create_book.return_value = mock_book_data
    mock_service.delete_book.return_value = None

    app.dependency_overrides[get_book_service] = lambda: mock_service
    app.dependency_overrides[get_current_user] = lambda: {"id": "test-uuid", "email": "vika@lpnu.ua"}
    yield
    app.dependency_overrides.clear()


@patch("app.core.rate_limiter.RedisRateLimiter.check_allowance", new_callable=AsyncMock)
def test_rate_limit_exceeded(mock_check):
    mock_check.return_value = False
    response = client.get("/api/books/")
    assert response.status_code == 429


@patch("app.core.rate_limiter.RedisRateLimiter.check_allowance", new_callable=AsyncMock)
def test_get_all_books_success(mock_check):
    mock_check.return_value = True
    response = client.get("/api/books/")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["items"][0]["description"] == "Lab 7 description"
    assert data["items"][0]["year"] == 2026

@patch("app.core.rate_limiter.RedisRateLimiter.check_allowance", new_callable=AsyncMock)
def test_create_book_valid_data(mock_check):
    mock_check.return_value = True
    book_data = {
        "title": "FastAPI Guide", 
        "author": "Victoria", 
        "description": "New book", 
        "year": 2026
    }
    
    response = client.post("/api/books", json=book_data)
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Book"

@patch("app.core.rate_limiter.RedisRateLimiter.check_allowance", new_callable=AsyncMock)
def test_delete_book_success(mock_check):
    mock_check.return_value = True
    book_id = str(uuid.uuid4())
    
    response = client.delete(f"/api/books/{book_id}")
    
    assert response.status_code == 204