from fastapi import APIRouter

from schemas.chat import ChatRequest

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"]
)


@router.post("/")
def chat(data: ChatRequest):
    return {
        "message": f"You said: {data.message}"
    }