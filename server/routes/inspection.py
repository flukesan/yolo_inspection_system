"""Inspection + stats + PLC routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from server.auth import get_current_user, require_role
from server.broker import broker
from server.plc_state import plc_state
from server.redis_client import redis_client
from server.store import store

router = APIRouter(prefix="/api", tags=["inspection"])


class InspectionCreate(BaseModel):
    part_id: str = Field(..., min_length=1, max_length=100)
    result: str = Field(..., pattern="^(OK|NG)$")
    defect_class: Optional[str] = None
    station: str = "Station-1"
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    error_code: Optional[str] = None
    image_id: Optional[int] = None


@router.post("/inspection")
async def create_inspection(data: InspectionCreate, user: dict = Depends(get_current_user)):
    insp = await store.create(**data.model_dump())
    payload = insp.to_dict()
    # Fan out to dashboards via in-process broker + optional Redis stream/pubsub.
    await broker.publish({"type": "inspection", **payload})
    await redis_client.publish("inspection:events", payload)
    await redis_client.xadd("inspection:stream", payload)
    return payload


@router.get("/inspections")
async def list_inspections(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    result: Optional[str] = Query(None, pattern="^(OK|NG)$"),
    station: Optional[str] = None,
    part_id: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    items, total = await store.list(
        page=page, limit=limit, result=result, station=station, part_id=part_id,
    )
    total_pages = max(1, (total + limit - 1) // limit)
    return {
        "items": [i.to_dict() for i in items],
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


@router.get("/inspection/{inspection_id}")
async def get_inspection(inspection_id: int, user: dict = Depends(get_current_user)):
    insp = await store.get(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return insp.to_dict()


@router.get("/stats")
async def get_stats(hours: int = Query(24, ge=1, le=168), user: dict = Depends(get_current_user)):
    return await store.stats(hours)


@router.get("/stats/trend")
async def get_trend(hours: int = Query(24, ge=1, le=72), user: dict = Depends(get_current_user)):
    return await store.trend(hours)


@router.get("/stats/defects")
async def get_defects(hours: int = Query(24, ge=1, le=168), user: dict = Depends(get_current_user)):
    return await store.defect_breakdown(hours)


@router.get("/plc/status")
async def plc_status(user: dict = Depends(get_current_user)):
    return plc_state.snapshot()


class PLCHeartbeat(BaseModel):
    connected: bool
    state: str
    last_error: Optional[str] = None


@router.post("/plc/heartbeat")
async def plc_heartbeat(beat: PLCHeartbeat, user: dict = Depends(require_role("engineer", "operator"))):
    plc_state.update(connected=beat.connected, state=beat.state, last_error=beat.last_error)
    snapshot = plc_state.snapshot()
    await broker.publish({"type": "plc_status", **snapshot})
    return snapshot
