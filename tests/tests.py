import pytest
import os
import pymongo
import time
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models import MONGO_URL

TEST_DB_NAME = "library_test"

sync_client = pymongo.MongoClient(MONGO_URL)
sync_collection = sync_client[TEST_DB_NAME]["books"]

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    os.environ["MONGO_DB_NAME"] = TEST_DB_NAME
    yield

@pytest.fixture
def client():
    sync_collection.delete_many({})
    
    with TestClient(app) as c:
        c.post("/books/", json={
            "title": "Кобзар",
            "author": "Тарас Шевченко",
            "year": 1840,
            "status": "наявна",
            "description": "Збірка творів"
        })
        
        yield c
    
    sync_collection.delete_many({})

def test_get_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json()["total_count"] >= 1

def test_get_book(client):
    books = client.get("/books/").json()["items"]
    target_book = next((b for b in books if b["title"] == "Кобзар"), None)
    
    assert target_book is not None, f"Кобзар не знайдено серед: {[b['title'] for b in books]}"
    book_id = target_book["id"]
    
    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Кобзар"

def test_get_book_not_found(client):
    response = client.get("/books/5f50c31e1c9d440000d1c000")
    assert response.status_code == 404

def test_create_book(client):
    new_book = {
        "title": "Захар Беркут",
        "author": "Іван Франко",
        "year": 1883,
        "status": "наявна",
        "description": "Повість"
    }
    response = client.post("/books/", json=new_book)
    assert response.status_code == 201
    assert response.json()["title"] == "Захар Беркут"

def test_delete_book(client):
    books = client.get("/books/").json()["items"]
    if not books:
        pytest.skip("Немає книг для видалення")
    book_id = books[0]["id"]
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

def test_get_books_pagination(client):
    response = client.get("/books/?limit=1")
    assert len(response.json()["items"]) <= 1

def test_get_books_filter_by_author(client):
    response = client.get("/books/", params={"author": "Шевченко"})
    assert response.status_code == 200
    items = response.json()["items"]
    
    assert len(items) > 0, "Фільтр не повернув книг Шевченка"
    assert any("Шевченко" in b["author"] for b in items)

def test_get_books_sort_by_year(client):
    response = client.get("/books/", params={"sort_by": "year", "sort_order": "desc"})
    assert response.status_code == 200