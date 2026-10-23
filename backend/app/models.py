from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class SearchLog(SQLModel, table=True):
    __tablename__ = "search_logs"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    search_query: str
    target_unity_location_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# --- INVENTORY MODELS ---

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    firebase_uid: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    role: str = Field(default="student")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="user")
    fines: List["Fine"] = Relationship(back_populates="user")

class Book(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    author: str
    isbn: str = Field(unique=True)
    category: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    unity_location_id: Optional[str] = None 
    
    copies: List["BookCopy"] = Relationship(back_populates="book")

class BookCopy(SQLModel, table=True):
    __tablename__ = "book_copies"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    book_id: uuid.UUID = Field(foreign_key="book.id")
    rfid_tag: Optional[str] = Field(unique=True, default=None)
    status: str = Field(default="available") # 'available', 'issued', 'lost'
    condition: str = Field(default="good")
    
    book: Book = Relationship(back_populates="copies")

# --- LOGIC MODELS (NEW) ---

class Transaction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    copy_id: uuid.UUID = Field(foreign_key="book_copies.id")
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str = Field(default="active") # 'active', 'completed', 'overdue'

    user: User = Relationship(back_populates="transactions")

class Fine(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    amount: float
    reason: str # 'late_return', 'damage'
    is_paid: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="fines")

class GateLog(SQLModel, table=True):
    __tablename__ = "gate_logs"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    access_type: str # 'entry', 'exit'
    status: str # 'granted', 'denied'
    denial_reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)