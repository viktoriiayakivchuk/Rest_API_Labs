from app.models import db

async def get_db():
    yield db