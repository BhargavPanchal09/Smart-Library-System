# backend/app/db/engine.py
from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings

# We use standard psycopg2 for synchronous checks, but for high-scale 
# production, we would use async. For this phase, sync is safer/easier.
connection_string = settings.DATABASE_URL

# echo=True prints SQL queries to the terminal (Great for debugging)
engine = create_engine(connection_string, echo=False, pool_pre_ping=True, pool_recycle=300)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)