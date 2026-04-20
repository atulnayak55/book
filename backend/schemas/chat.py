from datetime import datetime

from pydantic import BaseModel


class ChatMessageBase(BaseModel):
    sender_id: int
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageRead(ChatMessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
