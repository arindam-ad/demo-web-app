from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import AppointmentStatus, PaymentStatus, Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    hospital_code: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hospital_id: int | None
    full_name: str
    email: EmailStr
    role: Role
    is_active: bool


class HospitalCreate(BaseModel):
    name: str
    hospital_code: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    license_number: str | None = None


class HospitalRead(HospitalCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime


class PatientCreate(BaseModel):
    patient_code: str
    full_name: str
    gender: str | None = None
    dob: date | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    blood_group: str | None = None
    emergency_contact: str | None = None


class PatientRead(PatientCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hospital_id: int
    created_at: datetime


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    appointment_type: str = "OPD"
    notes: str | None = None


class AppointmentRead(AppointmentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hospital_id: int
    status: AppointmentStatus
    created_at: datetime


class BillCreate(BaseModel):
    patient_id: int
    appointment_id: int | None = None
    bill_number: str
    gross_amount: float
    discount: float = 0
    tax: float = 0
    net_amount: float


class BillRead(BillCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hospital_id: int
    payment_status: PaymentStatus
    created_at: datetime


class DashboardMetrics(BaseModel):
    hospital_id: int | None
    total_patients: int
    today_appointments: int
    opd_appointments: int
    ipd_appointments: int
    revenue_total: float
    occupied_beds: int
    available_beds: int

