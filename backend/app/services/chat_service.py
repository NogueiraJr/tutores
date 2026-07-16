import uuid
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.models.tutor import Tutor
from app.models.conversation import Conversation, Message
from app.agent import get_tutor_agent

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_conversation(self, tutor_id: int, session_id: Optional[str] = None) -> Conversation:
        if session_id:
            conv = self.db.query(Conversation).filter(
                Conversation.session_id == session_id,
                Conversation.tutor_id == tutor_id
            ).first()
            if conv:
                return conv
        
        # Create new conversation
        session_id = session_id or str(uuid.uuid4())
        conv = Conversation(tutor_id=tutor_id, session_id=session_id)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def _get_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).limit(20).all()
        
        return [{"role": msg.role, "content": msg.content} for msg in messages]

    async def chat(self, tutor_id: int, message: str, session_id: Optional[str] = None) -> Dict:
        # Get tutor
        tutor = self.db.query(Tutor).filter(Tutor.id == tutor_id, Tutor.status == True).first()
        if not tutor:
            raise ValueError("Tutor not found or inactive")

        # Get or create conversation
        conv = self._get_or_create_conversation(tutor_id, session_id)
        
        # Save user message
        user_msg = Message(
            conversation_id=conv.id,
            role="user",
            content=message
        )
        self.db.add(user_msg)
        self.db.commit()

        # Get history
        history = self._get_conversation_history(conv.id)
        
        # Get agent response
        tutor_data = {
            "name": tutor.name,
            "description": tutor.description,
            "instructions": tutor.instructions,
            "knowledge_source": tutor.knowledge_source
        }
        
        agent = get_tutor_agent(tutor_data)
        response = await agent.chat(message, history[:-1])  # Exclude current message
        
        # Save assistant message
        assistant_msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content=response
        )
        self.db.add(assistant_msg)
        self.db.commit()

        return {
            "response": response,
            "session_id": conv.session_id,
            "tutor_id": tutor_id
        }
