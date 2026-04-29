import pytest
from app.core.security import get_password_hash, verify_password, create_access_token

@pytest.mark.asyncio
async def test_password_hashing():
    password = "vika_secret_pass"
    hashed = await get_password_hash(password)
    assert hashed != password
    assert await verify_password(password, hashed) is True
    assert await verify_password("wrong_pass", hashed) is False

def test_create_jwt():
    token = create_access_token(data={"sub": "test_id"})
    assert isinstance(token, str)
    assert len(token) > 10