from datetime import date

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import DbSession, TenantHospitalId
from app.models import Appointment, Bed, Bill, Patient
from app.schemas import DashboardMetrics


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def metrics(db: DbSession, hospital_id: TenantHospitalId) -> DashboardMetrics:
    today = date.today()
    total_patients = db.scalar(select(func.count()).select_from(Patient).where(Patient.hospital_id == hospital_id)) or 0
    today_appointments = db.scalar(
        select(func.count()).select_from(Appointment).where(Appointment.hospital_id == hospital_id, Appointment.appointment_date == today)
    ) or 0
    opd = db.scalar(
        select(func.count()).select_from(Appointment).where(Appointment.hospital_id == hospital_id, Appointment.appointment_type == "OPD")
    ) or 0
    ipd = db.scalar(
        select(func.count()).select_from(Appointment).where(Appointment.hospital_id == hospital_id, Appointment.appointment_type == "IPD")
    ) or 0
    revenue = db.scalar(select(func.coalesce(func.sum(Bill.net_amount), 0)).where(Bill.hospital_id == hospital_id)) or 0
    occupied_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.hospital_id == hospital_id, Bed.status == "OCCUPIED")) or 0
    available_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.hospital_id == hospital_id, Bed.status == "AVAILABLE")) or 0

    return DashboardMetrics(
        hospital_id=hospital_id,
        total_patients=total_patients,
        today_appointments=today_appointments,
        opd_appointments=opd,
        ipd_appointments=ipd,
        revenue_total=float(revenue),
        occupied_beds=occupied_beds,
        available_beds=available_beds,
    )

