import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.dependencies import get_current_user, get_book_service

client = TestClient(app)

async def mock_service_call(*args, **kwargs):
    return {
        "items": [],
        "total": 0,
        "limit": 10,
        "offset": 0
    }

@pytest.fixture(autouse=True)
def setup_overrides():
    mock_service = AsyncMock()
    mock_service.get_books.side_effect = mock_service_call
    
    app.dependency_overrides[get_book_service] = lambda: mock_service
    app.dependency_overrides[get_current_user] = lambda: None
    yield
    app.dependency_overrides.clear()

@patch("app.core.rate_limiter.RedisRateLimiter.check_allowance", new_callable=AsyncMock)
def test_anonymous_rate_limit_ok(mock_check):
    mock_check.return_value = True
    
    response = client.get("/api/books/")
    
    assert response.status_code == 200
    assert mock_check.called

@patch("app.core.rate_limiter.RedisRateLimiter.check_allowance", new_callable=AsyncMock)
def test_anonymous_rate_limit_exceeded(mock_check):
    mock_check.return_value = False
    
    response = client.get("/api/books/")
    
    assert response.status_code == 429
    assert response.json()["detail"] == "Too Many Requests"

@patch("app.core.rate_limiter.RedisRateLimiter.check_allowance", new_callable=AsyncMock)
def test_authenticated_rate_limit_ok(mock_check):
    app.dependency_overrides[get_current_user] = lambda: {"id": "test-uuid", "email": "vika@lpnu.ua"}
    mock_check.return_value = True
    
    headers = {"Authorization": "Bearer fake-token"}
    response = client.get("/api/books/", headers=headers)
    
    assert response.status_code == 200
    assert mock_check.called

@patch("app.core.rate_limiter.RedisRateLimiter.check_allowance", new_callable=AsyncMock)
def test_authenticated_rate_limit_exceeded(mock_check):
    app.dependency_overrides[get_current_user] = lambda: {"id": "test-uuid"}
    mock_check.return_value = False
    
    headers = {"Authorization": "Bearer fake-token"}
    response = client.get("/api/books/", headers=headers)
    
    assert response.status_code == 429