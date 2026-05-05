"""
PLC management routes — test connection, read data, live monitor.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from server.auth import get_current_user, require_role
from server.plc_client import get_plc

router = APIRouter(prefix="/api/plc", tags=["plc"])


class PlcTestResult(BaseModel):
    ok: bool
    host: str
    message: str
    cpu: Optional[str] = None
    mock_fallback: bool = False

class PlcStatus(BaseModel):
    connected: bool
    mock_mode: bool
    host: str
    rack: int
    slot: int
    poll_interval: float
    last_data_age: float

class PlcDataModel(BaseModel):
    m_bits: Dict[str, bool]
    i_bits: Dict[str, bool]
    q_bits: Dict[str, bool]
    m_words: Dict[str, int]
    db_values: Dict[str, Any]
    timestamp: float


@router.post("/test")
async def test_plc_connection(user: dict = Depends(require_role("engineer"))):
    plc = get_plc()
    result = plc.test_connection()
    return PlcTestResult(**result)


@router.get("/status")
async def plc_status(user: dict = Depends(get_current_user)):
    plc = get_plc()
    data = plc.last_data
    return PlcStatus(
        connected=plc.connected,
        mock_mode=plc.is_mock,
        host=plc.config.host,
        rack=plc.config.rack,
        slot=plc.config.slot,
        poll_interval=1.0,
        last_data_age=0.0 if data.timestamp == 0 else plc.last_data.timestamp,
    )


@router.get("/data")
async def read_plc_data(user: dict = Depends(get_current_user)):
    plc = get_plc()
    data = plc.read_all()
    return PlcDataModel(
        m_bits=data.m_bits,
        i_bits=data.i_bits,
        q_bits=data.q_bits,
        m_words=data.m_words,
        db_values=data.db_values,
        timestamp=data.timestamp,
    )
