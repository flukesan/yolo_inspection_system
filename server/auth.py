"""JWT Authentication + OAuth2."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from server.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

USERS = {
    "engineer": {"username": "engineer", "password": "engineer123", "role": "engineer"},
    "operator": {"username": "operator", "password": "operator123", "role": "operator"},
}

def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + expires_delta})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)

def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None

def authenticate(username: str, password: str) -> Optional[dict]:
    user = USERS.get(username)
    if user and user["password"] == password:
        return user
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    user = USERS.get(username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
