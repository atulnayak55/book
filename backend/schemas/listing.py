# schemas/listing.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .user import UserPublicResponse

# We create a tiny schema for images to nest inside the listing
class ListingImageResponse(BaseModel):
    id: int
    image_url: str
    
    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------
# LISTING SCHEMAS
# ---------------------------------------------------------
class ListingBase(BaseModel):
    title: str
    price: float
    condition: str
    description: Optional[str] = None
    subject_id: Optional[int] = None

class ListingCreate(ListingBase):
    # When creating a listing, we only need the basic info and the subject it belongs to.
    # We do NOT include seller_id here, because we will get that securely from the logged-in user's session later.
    pass

class ListingResponse(ListingBase):
    id: int
    created_at: datetime
    seller_id: int
    
    # We can nest the seller info and images so the frontend has everything it needs in one request
    seller: UserPublicResponse
    images: List[ListingImageResponse] = []

    model_config = ConfigDict(from_attributes=True)
