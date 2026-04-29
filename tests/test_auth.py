from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    # 1. Реєстрація
    user_data = {"username": "testuser", "password": "testpassword"}
    reg_res = client.post("/api/auth/register", json=user_data)
    assert reg_res.status_code == 201
    
    # 2. Логін
    login_data = {"username": "testuser", "password": "testpassword"}
    login_res = client.post("/api/auth/login", data=login_data) # OAuth2 використовує form-data
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

def test_refresh_token():
    # Спочатку отримаємо токен
    user_data = {"username": "refresh_user", "password": "password"}
    client.post("/api/auth/register", json=user_data)
    login_res = client.post("/api/auth/login", data=user_data)
    refresh_token = login_res.json()["refresh_token"]
    
    # Оновлення
    refresh_res = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()