import pytest
import pymongo
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.main import app
from app.api import get_service
from app.services import BookService
from app.models import MONGO_URL

TEST_DB_NAME = "library_test"

# Синхронний клієнт для підготовки даних
sync_client = pymongo.MongoClient(MONGO_URL)
sync_collection = sync_client[TEST_DB_NAME]["books"]

class TestRepository:
    def __init__(self, collection):
        self.collection = collection

@pytest.fixture
def client():
    # 1. Очищуємо базу
    sync_collection.delete_many({})
    sync_collection.insert_one({
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "year": 1840,
        "status": "наявна",
        "description": "Збірка творів"
    })

    # 2. Перевизначаємо сервіс, щоб він створював новий клієнт всередині тесту
    async def override_get_service():
        test_client = AsyncIOMotorClient(MONGO_URL)
        service = BookService()
        # Примусово підміняємо колекцію на тестову
        service.repository.collection = test_client[TEST_DB_NAME]["books"]
        return service

    app.dependency_overrides[get_service] = override_get_service
    
    # 3. Ранимо тести
    with TestClient(app) as c:
        yield c
    
    # 4. Очищуємо за собою
    app.dependency_overrides.clear()
    sync_collection.delete_many({})

def test_get_books(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json()["total_count"] >= 1

def test_get_book(client):
    books = client.get("/books/").json()["items"]
    book_id = books[0]["id"]
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
    book_id = books[0]["id"]
    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

def test_get_books_pagination(client):
    response = client.get("/books/?limit=1")
    assert len(response.json()["items"]) == 1

def test_get_books_filter_by_author(client):
    response = client.get("/books/?author=Шевченко")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 1

def test_get_books_sort_by_year(client):
    response = client.get("/books/?sort_by=year&sort_order=desc")
    assert response.status_code == 200