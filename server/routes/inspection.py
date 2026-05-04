"""Inspection routes."""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from datetime import datetime
from server.auth import get_current_user

router = APIRouter(prefix="/api", tags=["inspection"])

class InspectionCreate(BaseModel):
    part_id: str
    result: str
    defect_class: Optional[str] = None
    station: str = "Station-1"
    confidence: float = 0.0
    image_id: Optional[int] = None

@router.post("/inspection")
async def create_inspection(data: InspectionCreate, user: dict = Depends(get_current_user)):
    return {"id": 1, "timestamp": datetime.now().isoformat(), **data.dict()}

@router.get("/inspections")
async def list_inspections(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    result: Optional[str] = None, station: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    return {"items": [], "total": 0, "page": page, "total_pages": 1}

@router.get("/stats")
async def get_stats(user: dict = Depends(get_current_user)):
    return {"total": 0, "ok": 0, "ng": 0, "rate": 100.0, "period_hours": 24}

@router.get("/stats/trend")
async def get_trend(user: dict = Depends(get_current_user)):
    return [{"hour": f"{h:02d}:00", "total": 0, "ok": 0, "ng": 0, "ok_rate": 100.0} for h in range(24)]

@router.get("/plc/status")
async def plc_status(user: dict = Depends(get_current_user)):
    return {"connected": False, "heartbeat_ok": False, "state": "IDLE", "uptime": 0, "last_error": None}
