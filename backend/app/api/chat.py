from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        service = ChatService(db)
        result = await service.chat(
            tutor_id=request.tutor_id,
            message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            tutor_id=result["tutor_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
