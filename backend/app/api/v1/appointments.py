from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import DbSession, TenantHospitalId, ensure_entity_in_tenant
from app.models import Appointment, Doctor, Patient
from app.schemas import AppointmentCreate, AppointmentRead


router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentRead])
def list_appointments(db: DbSession, hospital_id: TenantHospitalId) -> list[Appointment]:
    return list(
        db.scalars(
            select(Appointment)
            .where(Appointment.hospital_id == hospital_id)
            .order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
            .limit(100)
        )
    )


@router.post("", response_model=AppointmentRead)
def book_appointment(payload: AppointmentCreate, db: DbSession, hospital_id: TenantHospitalId) -> Appointment:
    ensure_entity_in_tenant(db, Patient, payload.patient_id, hospital_id)
    ensure_entity_in_tenant(db, Doctor, payload.doctor_id, hospital_id)
    appointment = Appointment(hospital_id=hospital_id, **payload.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment

