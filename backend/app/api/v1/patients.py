from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import DbSession, TenantHospitalId
from app.models import Patient
from app.schemas import PatientCreate, PatientRead


router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientRead])
def list_patients(db: DbSession, hospital_id: TenantHospitalId, q: str | None = None) -> list[Patient]:
    statement = select(Patient).where(Patient.hospital_id == hospital_id).order_by(Patient.created_at.desc())
    if q:
        statement = statement.where(Patient.full_name.ilike(f"%{q}%"))
    return list(db.scalars(statement.limit(100)))


@router.post("", response_model=PatientRead)
def create_patient(payload: PatientCreate, db: DbSession, hospital_id: TenantHospitalId) -> Patient:
    patient = Patient(hospital_id=hospital_id, **payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

