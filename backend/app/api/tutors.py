from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.tutor_service import TutorService
from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse
from app.core.config import settings

router = APIRouter(prefix="/tutors", tags=["tutors"])

def verify_admin(admin_api_key: str = Header(...)):
    if admin_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin API key")
    return True

@router.post("/", response_model=TutorResponse)
def create_tutor(
    tutor: TutorCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    service = TutorService(db)
    return service.create(tutor)

@router.get("/", response_model=List[TutorResponse])
def list_tutors(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    service = TutorService(db)
    return service.get_all(include_inactive=include_inactive)

@router.get("/{tutor_id}", response_model=TutorResponse)
def get_tutor(
    tutor_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    service = TutorService(db)
    tutor = service.get(tutor_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return tutor

@router.put("/{tutor_id}", response_model=TutorResponse)
def update_tutor(
    tutor_id: int,
    tutor: TutorUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    service = TutorService(db)
    updated = service.update(tutor_id, tutor)
    if not updated:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return updated

@router.delete("/{tutor_id}")
def delete_tutor(
    tutor_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin)
):
    service = TutorService(db)
    if not service.delete(tutor_id):
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {"message": "Tutor deactivated successfully"}
