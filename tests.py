import pytest
from httpx import ASGITransport, AsyncClient
from main import app

# Налаштування для тестування асинхронних функцій
@pytest.mark.asyncio
async def test_library_api():
    # ASGITransport дозволяє тестувати FastAPI без реального запуску сервера на порту
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        # --- 1. ТЕСТ СТВОРЕННЯ КНИГИ (POST) ---
        new_book = {
            "title": "The Call of Cthulhu",
            "author": "H.P. Lovecraft",
            "description": "A classic horror story",
            "year": 1928,
            "status": "наявна"
        }
        response = await ac.post("/books/", json=new_book)
        assert response.status_code == 201
        book_data = response.json()
        assert book_data["title"] == new_book["title"]
        assert "id" in book_data
        book_id = book_data["id"]

        # --- 2. ТЕСТ ОТРИМАННЯ ВСІХ КНИГ (GET) ---
        response = await ac.get("/books/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

        # --- 3. ТЕСТ ОТРИМАННЯ ПО ID (GET) ---
        response = await ac.get(f"/books/{book_id}")
        assert response.status_code == 200
        assert response.json()["id"] == book_id

        # --- 4. ТЕСТ ФІЛЬТРАЦІЇ ТА СОРТУВАННЯ ---
        response = await ac.get("/books/", params={"author": "Lovecraft", "sort_by": "year"})
        assert response.status_code == 200
        assert all("Lovecraft" in b["author"] for b in response.json())

        # --- 5. ТЕСТ ВИДАЛЕННЯ (DELETE) ---
        response = await ac.delete(f"/books/{book_id}")
        assert response.status_code == 204

        # --- 6. ТЕСТ ІДЕМПОТЕНТНОСТІ DELETE ---
        # Повторне видалення того ж ID має повертати 204, а не помилку
        response = await ac.delete(f"/books/{book_id}")
        assert response.status_code == 204