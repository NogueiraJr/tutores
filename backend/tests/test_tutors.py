import pytest
from app.services.tutor_service import TutorService
from app.schemas.tutor import TutorCreate, TutorUpdate
from app.core.database import SessionLocal

def test_create_tutor():
    db = SessionLocal()
    service = TutorService(db)
    
    data = TutorCreate(
        name="Test Tutor",
        description="A test tutor",
        instructions="Be helpful",
        knowledge_source="https://example.com/knowledge.txt"
    )
    
    tutor = service.create(data)
    assert tutor.id is not None
    assert tutor.name == "Test Tutor"
    assert tutor.status == True
    
    db.delete(tutor)
    db.commit()

def test_get_tutor():
    db = SessionLocal()
    service = TutorService(db)
    
    data = TutorCreate(
        name="Test Get Tutor",
        instructions="Test instructions"
    )
    tutor = service.create(data)
    
    found = service.get(tutor.id)
    assert found is not None
    assert found.name == "Test Get Tutor"
    
    db.delete(tutor)
    db.commit()
