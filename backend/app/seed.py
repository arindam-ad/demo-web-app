from datetime import date, time

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models import Appointment, Bed, BedStatus, Bill, Doctor, Hospital, Patient, Role, User


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.scalar(select(Hospital).where(Hospital.hospital_code == "HOSP-A")):
            print("Seed data already exists.")
            return

        hospital = Hospital(
            name="Hospital A",
            hospital_code="HOSP-A",
            city="Bengaluru",
            state="Karnataka",
            phone="+91 98765 21000",
            email="admin@hospital-a.example",
            license_number="KA-HMP-001",
        )
        db.add(hospital)
        db.flush()

        super_admin = User(
            full_name="Platform Super Admin",
            email="superadmin@example.com",
            password_hash=hash_password("ChangeMe123!"),
            role=Role.SUPER_ADMIN,
            hospital_id=None,
        )
        hospital_admin = User(
            full_name="Hospital Admin",
            email="admin@hospital-a.example",
            password_hash=hash_password("ChangeMe123!"),
            role=Role.HOSPITAL_ADMIN,
            hospital_id=hospital.id,
        )
        doctor_user = User(
            full_name="Dr. Neha Sharma",
            email="doctor@hospital-a.example",
            password_hash=hash_password("ChangeMe123!"),
            role=Role.DOCTOR,
            hospital_id=hospital.id,
        )
        db.add_all([super_admin, hospital_admin, doctor_user])
        db.flush()

        doctor = Doctor(
            hospital_id=hospital.id,
            user_id=doctor_user.id,
            doctor_code="DOC-001",
            specialization="Cardiology",
            qualification="MD",
            experience_years=9,
            consultation_fee=800,
        )
        patient = Patient(
            hospital_id=hospital.id,
            patient_code="PAT-001",
            full_name="Amit Rao",
            gender="Male",
            dob=date(1985, 8, 15),
            phone="+91 98765 22001",
            blood_group="O+",
        )
        db.add_all([doctor, patient])
        db.flush()

        db.add(
            Appointment(
                hospital_id=hospital.id,
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_date=date.today(),
                appointment_time=time(10, 30),
                appointment_type="OPD",
            )
        )
        db.add(Bill(hospital_id=hospital.id, patient_id=patient.id, bill_number="BILL-001", gross_amount=800, tax=40, net_amount=840))
        db.add_all(
            [
                Bed(hospital_id=hospital.id, bed_number="ICU-01", ward="ICU", bed_type="ICU", status=BedStatus.OCCUPIED),
                Bed(hospital_id=hospital.id, bed_number="GEN-01", ward="General", bed_type="Standard", status=BedStatus.AVAILABLE),
            ]
        )
        db.commit()
        print("Seed data created.")
    finally:
        db.close()


if __name__ == "__main__":
    run()

