from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TutorBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: str
    knowledge_source: Optional[str] = None
    status: bool = True

class TutorCreate(TutorBase):
    pass

class TutorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    knowledge_source: Optional[str] = None
    status: Optional[bool] = None

class TutorResponse(TutorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
