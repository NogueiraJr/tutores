from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.tutor import Tutor
from app.schemas.tutor import TutorCreate, TutorUpdate

class TutorService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: TutorCreate) -> Tutor:
        tutor = Tutor(**data.model_dump())
        self.db.add(tutor)
        self.db.commit()
        self.db.refresh(tutor)
        return tutor

    def get(self, tutor_id: int) -> Optional[Tutor]:
        return self.db.query(Tutor).filter(Tutor.id == tutor_id).first()

    def get_all(self, include_inactive: bool = False) -> List[Tutor]:
        query = self.db.query(Tutor)
        if not include_inactive:
            query = query.filter(Tutor.status == True)
        return query.all()

    def update(self, tutor_id: int, data: TutorUpdate) -> Optional[Tutor]:
        tutor = self.get(tutor_id)
        if not tutor:
            return None
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tutor, key, value)
        
        self.db.commit()
        self.db.refresh(tutor)
        return tutor

    def delete(self, tutor_id: int) -> bool:
        tutor = self.get(tutor_id)
        if not tutor:
            return False
        tutor.status = False
        self.db.commit()
        return True
