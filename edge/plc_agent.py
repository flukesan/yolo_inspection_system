"""S7Comm PLC Agent for Siemens S7-300."""
import time
import asyncio
from typing import Optional
from .plc_enums import InspectionResult, ErrorCode, PLCState, TriggerMode

class S7PLCAgent:
    def __init__(self, host: str, rack: int = 0, slot: int = 2, heartbeat_interval: float = 3.0):
        self.host = host
        self.rack = rack
        self.slot = slot
        self.heartbeat_interval = heartbeat_interval
        self.state = PLCState.DISCONNECTED
        self.connected = False
        self.heartbeat_ok = False
        self.uptime = 0
        self.last_error: Optional[str] = None
        self._mock_db = {}

    async def connect(self) -> bool:
        self.state = PLCState.CONNECTING
        await asyncio.sleep(0.01)
        self.connected = True
        self.state = PLCState.IDLE
        self.uptime = 0
        return True

    async def disconnect(self) -> None:
        self.connected = False
        self.state = PLCState.DISCONNECTED

    async def read_trigger(self) -> bool:
        await asyncio.sleep(0.001)
        return self._mock_db.get("trigger", False)

    async def write_result(self, result: InspectionResult, error_code: ErrorCode = ErrorCode.OK) -> None:
        self._mock_db["result"] = result
        self._mock_db["error_code"] = error_code

    async def heartbeat(self) -> bool:
        self.heartbeat_ok = self.connected
        return self.heartbeat_ok

    async def reconnect(self) -> bool:
        for attempt in range(5):
            await asyncio.sleep(min(0.1 * (2 ** attempt), 2.0))
            if await self.connect():
                return True
        return False

    def simulate_trigger(self, trigger: bool = True) -> None:
        self._mock_db["trigger"] = trigger
