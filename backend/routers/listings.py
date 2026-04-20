from fastapi import APIRouter

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/{listing_id}")
def get_listing(listing_id: int) -> dict[str, int]:
    return {"listing_id": listing_id}
