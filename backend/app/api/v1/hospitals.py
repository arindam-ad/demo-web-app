from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DbSession, require_roles
from app.models import Hospital, Role, User
from app.schemas import HospitalCreate, HospitalRead


router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.get("", response_model=list[HospitalRead])
def list_hospitals(
    db: DbSession,
    _: User = Depends(require_roles(Role.SUPER_ADMIN)),
) -> list[Hospital]:
    return list(db.scalars(select(Hospital).order_by(Hospital.name)))


@router.post("", response_model=HospitalRead)
def create_hospital(
    payload: HospitalCreate,
    db: DbSession,
    _: User = Depends(require_roles(Role.SUPER_ADMIN)),
) -> Hospital:
    hospital = Hospital(**payload.model_dump())
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital

