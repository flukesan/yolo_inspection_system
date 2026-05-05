"""Auth routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from server.auth import authenticate, create_token, get_current_user
from datetime import timedelta
from server.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_token({"sub": user["username"], "role": user["role"]}, timedelta(minutes=settings.access_token_expire_minutes))
    refresh = create_token({"sub": user["username"], "type": "refresh"}, timedelta(days=settings.refresh_token_expire_days))
    return {"access_token": access, "refresh_token": refresh, "user": {"username": user["username"], "role": user["role"]}}

@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return {"username": user["username"], "role": user["role"]}

@router.get("/debug-config")
async def debug_config():
    """Debug: show auth config source without exposing passwords."""
    import os, hashlib
    return {
        "admin_username": settings.admin_username,
        "operator_username": settings.operator_username,
        "admin_pw_len": len(settings.admin_password),
        "admin_pw_md5": hashlib.md5(settings.admin_password.encode()).hexdigest()[:8],
        "operator_pw_md5": hashlib.md5(settings.operator_password.encode()).hexdigest()[:8],
        "env_ADMIN_PASSWORD": "SET" if os.environ.get("ADMIN_PASSWORD") else "NOT SET",
        "env_OPERATOR_PASSWORD": "SET" if os.environ.get("OPERATOR_PASSWORD") else "NOT SET",
    }
