from fastapi.testclient import TestClient
from app.main import app

# Використовуємо with, щоб гарантовано виконався блок lifespan (створення таблиць)
def test_final_registration_check():
    with TestClient(app) as client:
        response = client.post(
            "/api/auth/register",
            json={"username": "test_viki_success", "password": "securepassword123"}
        )
        
        # Перевіряємо успішне створення (201 Created)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "test_viki_success"
        assert "id" in data