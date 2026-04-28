import pytest
import uuid
from app.main import app
from app.repository import _books_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        _books_db.clear()
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "ok"}

def test_create_book_success(client):
    payload = {
        "title": "1984",
        "author": "George Orwell",
        "description": "Dystopian novel",
        "year": 1949,
        "status": "available"
    }
    response = client.post('/books', json=payload)
    assert response.status_code == 201
    data = response.json
    assert data["title"] == "1984"
    assert "id" in data
    assert data["status"] == "available"

def test_create_book_validation_error(client):
    payload = {
        "title": "Future",
        "author": "Author",
        "description": "Desc",
        "year": 2099,
        "status": "available"
    }
    response = client.post('/books', json=payload)
    assert response.status_code == 422
    assert "errors" in response.json

def test_get_all_books_pagination(client):
    for i in range(3):
        client.post('/books', json={
            "title": f"Book {i}",
            "author": "Author",
            "description": "Description",
            "year": 2000,
            "status": "available"
        })
    
    response = client.get('/books?limit=2&offset=0')
    assert response.status_code == 200
    data = response.json
    assert len(data["items"]) == 2
    assert data["total"] == 3

def test_get_book_by_id_success(client):
    res = client.post('/books', json={
        "title": "Test",
        "author": "Author",
        "description": "Desc",
        "year": 2020,
        "status": "available"
    })
    book_id = res.json["id"]
    
    response = client.get(f'/books/{book_id}')
    assert response.status_code == 200
    assert response.json["id"] == book_id

def test_get_book_by_id_not_found(client):
    fake_id = str(uuid.uuid4())
    response = client.get(f'/books/{fake_id}')
    assert response.status_code == 404

def test_delete_book(client):
    res = client.post('/books', json={
        "title": "To Delete",
        "author": "Author",
        "description": "Desc",
        "year": 2020,
        "status": "available"
    })
    book_id = res.json["id"]
    
    delete_res = client.delete(f'/books/{book_id}')
    assert delete_res.status_code == 200
    
    get_res = client.get(f'/books/{book_id}')
    assert get_res.status_code == 404