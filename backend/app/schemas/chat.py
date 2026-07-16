from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    tutor_id: int
    session_id: Optional[str] = None

class MessageResponse(BaseModel):
    role: str
    content: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tutor_id: int
    messages: Optional[List[MessageResponse]] = None
