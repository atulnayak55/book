# routers/listings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database.database import get_db
from schemas import listing as listing_schemas
from database import models
from crud import crud_listing
from routers.auth import get_current_user # Import our bouncer!

router = APIRouter(prefix="/listings", tags=["Marketplace Listings"])

@router.post("/", response_model=listing_schemas.ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    listing: listing_schemas.ListingCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Requires user to be logged in!
):
    """Post a new book for sale."""
    # We pass the current_user.id directly to the CRUD function. 
    # This guarantees the listing is tied to the person who is logged in.
    return crud_listing.create_listing(db=db, listing=listing, seller_id=current_user.id)

@router.get("/", response_model=List[listing_schemas.ListingResponse])
def read_listings(
    skip: int = 0, 
    limit: int = 50, 
    subject_id: Optional[int] = None, 
    db: Session = Depends(get_db)
):
    """View the marketplace. Optional: Filter by a specific Unipd subject."""
    return crud_listing.get_listings(db, skip=skip, limit=limit, subject_id=subject_id)

@router.get("/{listing_id}", response_model=listing_schemas.ListingResponse)
def read_listing(listing_id: int, db: Session = Depends(get_db)):
    """View a single listing's details."""
    db_listing = crud_listing.get_listing(db, listing_id=listing_id)
    if db_listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return db_listing