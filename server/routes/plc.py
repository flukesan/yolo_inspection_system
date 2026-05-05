"""
PLC management routes — test connection, read data, live monitor, address config.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
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


# ── Address Config ────────────────────────────────────────────────

_watch_addresses: list[str] = []


@router.get("/addresses")
async def get_watch_addresses(user: dict = Depends(get_current_user)):
    plc = get_plc()
    data = plc.last_data
    result = {}
    for addr in _watch_addresses:
        val = _resolve_address(data, addr)
        result[addr] = {"value": val, "type": type(val).__name__}
    return {"addresses": _watch_addresses, "values": result}


@router.put("/addresses")
async def set_watch_addresses(
    addrs: list[str],
    user: dict = Depends(require_role("engineer")),
):
    global _watch_addresses
    _watch_addresses = [a.strip() for a in addrs if a.strip()]
    plc = get_plc()
    data = plc.read_all()
    result = {}
    for addr in _watch_addresses:
        val = _resolve_address(data, addr)
        result[addr] = val
    return {"addresses": _watch_addresses, "values": result}


@router.get("/read")
async def read_single_address(
    address: str = Query(...),
    user: dict = Depends(get_current_user),
):
    plc = get_plc()
    data = plc.read_all()
    val = _resolve_address(data, address.strip())
    return {"address": address.strip(), "value": val, "type": type(val).__name__}


def _resolve_address(data, addr: str):
    addr = addr.strip()
    if "." in addr:
        if addr.startswith("DB") and "DBX" in addr:
            return data.db_values.get(addr, False)
        if addr.startswith("M"):
            return data.m_bits.get(addr, False)
        if addr.startswith("I"):
            return data.i_bits.get(addr, False)
        if addr.startswith("Q"):
            return data.q_bits.get(addr, False)
    if addr.startswith("MW"):
        return data.m_words.get(addr, 0)
    if addr.startswith("DB"):
        return data.db_values.get(addr, 0)
    return None
