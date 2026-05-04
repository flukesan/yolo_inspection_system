"""Auth routes."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from server.auth import authenticate, create_token, get_current_user, verify_token, USERS
from server.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def _issue_tokens(user: dict) -> dict:
    access = create_token(
        {"sub": user["username"], "role": user["role"]},
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh = create_token(
        {"sub": user["username"], "type": "refresh"},
        timedelta(days=settings.refresh_token_expire_days),
    )
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "user": {"username": user["username"], "role": user["role"]},
    }


@router.post("/login")
async def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return _issue_tokens(user)


@router.post("/refresh")
async def refresh(req: RefreshRequest):
    payload = verify_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = USERS.get(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return _issue_tokens(user)


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"username": user["username"], "role": user["role"]}
