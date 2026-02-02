# /backend/app/models/conversation.py

from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import Optional

# The art of conversing, it's much more than just what I say and you say.
class Conversation(SQLModel, table=True):
    """
    Stores chat messages between user and souls
    """
    __tablename__ = "conversations"
    
    # Defining the ID of each field
    msg_id: int = Field(default=None, primary_key=True)
    user_id: str = Field(max_length=12)
    soul_id: str = Field(max_length=50)
    
    # Role of the roll...
    role: str = Field(max_length=10)  # "user" or "assistant"
    content: str
    
    # Optional metadata (tokens used, etc.)
    meta_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Important things we gots to know!
    created_at: datetime = Field(default_factory=datetime.utcnow)