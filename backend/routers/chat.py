from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/history/{room_id}")
def get_chat_history(room_id: int) -> dict[str, int]:
    return {"room_id": room_id}
