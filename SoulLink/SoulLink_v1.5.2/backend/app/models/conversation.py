# /backend/app/models/conversation.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    soul_id: str = Field(index=True)
    
    role: str # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)