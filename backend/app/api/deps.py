from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models import Role, User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
DbSession = Annotated[Session, Depends(get_db)]
Token = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(db: DbSession, token: Token) -> User:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: Role):
    def dependency(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return dependency


def tenant_hospital_id(current_user: CurrentUser, request: Request) -> int:
    if current_user.role == Role.SUPER_ADMIN:
        header_value = request.headers.get("X-Hospital-ID")
        if not header_value:
            raise HTTPException(status_code=400, detail="X-Hospital-ID is required for SUPER_ADMIN tenant-scoped APIs")
        return int(header_value)
    if current_user.hospital_id is None:
        raise HTTPException(status_code=400, detail="User is not assigned to a hospital")
    return current_user.hospital_id


TenantHospitalId = Annotated[int, Depends(tenant_hospital_id)]


def ensure_entity_in_tenant(db: Session, model, entity_id: int, hospital_id: int):
    entity = db.scalar(select(model).where(model.id == entity_id, model.hospital_id == hospital_id))
    if not entity:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found in tenant")
    return entity

