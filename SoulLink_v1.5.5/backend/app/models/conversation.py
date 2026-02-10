# /backend/app/models/conversation.py

from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Index

# The art of conversing, it's much more than just what I say and you say.
class Conversation(SQLModel, table=True):
    """
    Stores chat messages between user and souls
    """
    __tablename__ = "conversations"
    __table_args__ = (
        Index("ix_conversation_user_soul_created", "user_id", "soul_id", "created_at"),
    )
    
    # Defining the ID of each field
    msg_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        primary_key=True,
        max_length=36
    )
    user_id: str = Field(max_length=36, index=True)
    soul_id: str = Field(max_length=50, index=True)
    
    # Role of the roll...
    role: str = Field(max_length=10)  # "user" or "assistant"
    content: str
    
    # Optional metadata (tokens used, etc.)
    meta_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Important things we gots to know!
    created_at: datetime = Field(default_factory=datetime.utcnow)