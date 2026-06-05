from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import DbSession, TenantHospitalId, ensure_entity_in_tenant
from app.models import Bill, Patient
from app.schemas import BillCreate, BillRead


router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/bills", response_model=list[BillRead])
def list_bills(db: DbSession, hospital_id: TenantHospitalId) -> list[Bill]:
    return list(db.scalars(select(Bill).where(Bill.hospital_id == hospital_id).order_by(Bill.created_at.desc()).limit(100)))


@router.post("/bills", response_model=BillRead)
def create_bill(payload: BillCreate, db: DbSession, hospital_id: TenantHospitalId) -> Bill:
    ensure_entity_in_tenant(db, Patient, payload.patient_id, hospital_id)
    bill = Bill(hospital_id=hospital_id, **payload.model_dump())
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill

