from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ConversationBase(BaseModel):
    name: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    is_user: bool

class MessageCreate(MessageBase):
    sources: Optional[List[str]] = None


class Message(MessageBase):
    id: UUID
    conversation_id: UUID
    timestamp: datetime
    sources: Optional[List[str]] = None

    class Config:
        from_attributes = True
