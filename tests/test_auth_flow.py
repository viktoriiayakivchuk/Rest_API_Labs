import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from jose import jwt
from app.core.config import settings
import uuid

# Дозволяємо pytest обробляти асинхронні тести
@pytest.mark.anyio
async def test_token_full_cycle():
    # Використовуємо AsyncClient для асинхронних запитів
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        
        # 1. Реєструємо унікального користувача
        unique_user = f"user_{uuid.uuid4().hex[:6]}"
        register_payload = {
            "username": unique_user,
            "email": f"{unique_user}@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
        reg_response = await ac.post("/api/auth/register", json=register_payload)
        assert reg_response.status_code == 201

        # 2. Логінимося (важливо: OAuth2PasswordRequestForm очікує data, а не json)
        login_data = {"username": unique_user, "password": "password123"}
        login_response = await ac.post("/api/auth/login", data=login_data)
        
        assert login_response.status_code == 200
        data = login_response.json()
        token = data["access_token"]
        
        # 3. Перевірка JWT
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] is not None
        print(f"\n✅ Успіх! User ID в токені: {payload['sub']}")