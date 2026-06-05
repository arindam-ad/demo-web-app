from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user
from app.core.security import create_access_token, verify_password
from app.models import Hospital, User
from app.schemas import LoginRequest, Token, UserRead


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: DbSession) -> Token:
    query = select(User).where(User.email == payload.email)
    if payload.hospital_code:
        query = query.join(Hospital).where(Hospital.hospital_code == payload.hospital_code)
    user = db.scalar(query)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email, password, or hospital")

    token = create_access_token(
        subject=str(user.id),
        claims={"role": user.role.value, "hospital_id": user.hospital_id},
    )
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

