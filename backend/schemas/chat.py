# schemas/chat.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# --- CHAT ROOM SCHEMAS ---
class ChatRoomBase(BaseModel):
    listing_id: int
    buyer_id: int

class ChatRoomCreate(ChatRoomBase):
    pass  # This is what the router was looking for!

class ChatRoomResponse(ChatRoomBase):
    id: int
    seller_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- MESSAGE SCHEMAS ---
class MessageBase(BaseModel):
    content: str
    room_id: int

class MessageCreate(MessageBase):
    receiver_id: int # Used to help the WebSocket route the message

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)