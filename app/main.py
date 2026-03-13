from fastapi import FastAPI
from api import router

app = FastAPI(title="Library API")
app.include_router(router)