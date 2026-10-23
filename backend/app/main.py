from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.engine import create_db_and_tables
from app.services.firebase_auth import initialize_firebase
from app.models import User, Book, BookCopy, Transaction, Fine, GateLog
from app.api.endpoints import router as api_router
from app.core.config import settings

app = FastAPI(title="Smart Library API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.on_event("startup")
def on_startup():
    initialize_firebase()
    create_db_and_tables()

@app.get("/")
def root():
    # We return a specific message to prove connection works
    return {"message": "Smart Library System is Online", "status": "active"}

app.include_router(api_router, prefix="/api/v1")