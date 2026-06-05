# Healthcare Management Platform MVP Backend

FastAPI starter backend for the multi-hospital MVP. It includes:

- JWT login with role claims.
- Tenant-aware APIs using `hospital_id`.
- SQLAlchemy 2.0 models for the core MVP schema.
- Seed data for one hospital, admin, doctor, patient, appointment, bill, and bed.
- Versioned REST API under `/api/v1`.

## Local Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
copy backend\.env.example backend\.env
docker compose up -d db
set PYTHONPATH=backend
python -m app.seed
uvicorn app.main:app --reload --app-dir backend
```

Open:

```text
http://127.0.0.1:8000/docs
```

Demo users:

```text
superadmin@example.com / ChangeMe123!
admin@hospital-a.example / ChangeMe123!
doctor@hospital-a.example / ChangeMe123!
```

For tenant-scoped APIs, normal hospital users are automatically restricted to their hospital. `SUPER_ADMIN` users must pass `X-Hospital-ID`.

