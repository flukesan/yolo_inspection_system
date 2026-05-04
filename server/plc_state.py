"""Shared PLC state. Edge agent posts heartbeats; API and WebSocket clients read it."""
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PLCState:
    connected: bool = False
    heartbeat_ok: bool = False
    state: str = "DISCONNECTED"
    last_error: Optional[str] = None
    last_heartbeat: float = 0.0
    started_at: float = field(default_factory=time.time)

    def update(
        self,
        *,
        connected: bool,
        state: str,
        last_error: Optional[str] = None,
    ) -> None:
        self.connected = connected
        self.state = state
        self.last_error = last_error
        self.last_heartbeat = time.time()
        self.heartbeat_ok = connected

    def snapshot(self) -> dict:
        # Heartbeat considered stale after 10s.
        stale = (time.time() - self.last_heartbeat) > 10 if self.last_heartbeat else True
        hb_ok = self.heartbeat_ok and not stale
        uptime = int(time.time() - self.started_at) if self.connected else 0
        return {
            "connected": self.connected and not stale,
            "heartbeat_ok": hb_ok,
            "state": self.state if not stale else "DISCONNECTED",
            "uptime": uptime,
            "last_error": self.last_error,
        }


plc_state = PLCState()
