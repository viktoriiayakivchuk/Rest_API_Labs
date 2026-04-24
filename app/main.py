import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from app.api import router
from app.models import MONGO_URL, MONGO_DB_NAME

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(MONGO_URL)
    app.mongodb_db = app.mongodb_client[MONGO_DB_NAME]
    
    logging.info(f"Connected to MongoDB: {MONGO_DB_NAME}")
    
    yield
    
    app.mongodb_client.close()
    logging.info("Disconnected from MongoDB")

app = FastAPI(
    title="Book Management REST API",
    description="A FastAPI-based REST API for managing books with MongoDB (Lab 4-5)",
    version="0.5.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Виникла внутрішня помилка сервера."},
    )

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)