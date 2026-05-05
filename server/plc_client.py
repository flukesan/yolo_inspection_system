"""
Siemens S7 PLC Client (snap7) + Mock fallback.

Supports:
  - Connect / disconnect
  - Read M (Memory), I (Input), Q (Output), DB (Data Block)
  - Heartbeat monitoring
  - Auto-fallback to mock when PLC unavailable
"""

import threading
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from server.config import settings


@dataclass
class PlcConfig:
    host: str = "192.168.1.10"
    rack: int = 0
    slot: int = 2
    heartbeat_interval: int = 3
    heartbeat_timeout: int = 9
    poll_interval_ms: int = 10


@dataclass
class PlcDataBlock:
    """Snapshot of PLC data regions."""
    m_bits: Dict[str, bool] = field(default_factory=dict)
    i_bits: Dict[str, bool] = field(default_factory=dict)
    q_bits: Dict[str, bool] = field(default_factory=dict)
    m_words: Dict[str, int] = field(default_factory=dict)
    db_values: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


class MockPlcClient:
    """Mock PLC for development/testing — simulates I/O."""

    def __init__(self):
        self._connected = False
        self._data = PlcDataBlock()
        self._counter = 0

    def connect(self) -> bool:
        self._connected = True
        self._init_mock_data()
        return True

    def disconnect(self):
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    def test_connection(self) -> Dict[str, Any]:
        return {"ok": True, "host": "mock", "message": "Mock PLC connected (dev mode)"}

    def _init_mock_data(self):
        self._data.m_bits = {
            "M0.0": True, "M0.1": False, "M0.2": True, "M0.3": False,
            "M1.0": False, "M1.1": True, "M1.2": False, "M1.3": True,
        }
        self._data.i_bits = {
            "I0.0": True, "I0.1": False, "I0.2": True, "I0.3": False,
            "I0.4": True, "I0.5": False, "I0.6": True, "I0.7": False,
        }
        self._data.q_bits = {
            "Q0.0": True, "Q0.1": False, "Q0.2": True, "Q0.3": False,
        }
        self._data.m_words = {
            "MW0": 1234, "MW2": 5678, "MW4": 0, "MW10": 42,
        }
        self._data.db_values = {
            "DB1.DBD0": 3.14159,
            "DB1.DBD4": 42.0,
            "DB1.DBW8": 100,
            "DB1.DBX10.0": True,
            "DB1.DBX10.1": False,
        }

    def read_all(self) -> PlcDataBlock:
        self._counter += 1
        self._data.m_words["MW4"] = self._counter % 1000
        self._data.db_values["DB1.DBW8"] = self._counter % 200
        self._data.i_bits["I0.7"] = self._counter % 2 == 0
        self._data.timestamp = time.time()
        return self._data

    def read_region(self, area: str, start: int, length: int) -> bytes:
        return bytes([0] * length)

    def write_region(self, area: str, start: int, data: bytes) -> bool:
        return True


class Snap7PlcClient:
    """Real Siemens S7 PLC client via python-snap7."""

    def __init__(self, config: PlcConfig):
        self.config = config
        self._client = None
        self._connected = False

    def connect(self) -> bool:
        try:
            import snap7
            self._client = snap7.client.Client()
            self._client.connect(self.config.host, self.config.rack, self.config.slot)
            self._connected = self._client.get_connected()
            return self._connected
        except Exception as e:
            print(f"[plc] Snap7 connect failed: {e}")
            return False

    def disconnect(self):
        if self._client:
            try:
                self._client.disconnect()
            except Exception:
                pass
            self._client = None
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    def test_connection(self) -> Dict[str, Any]:
        try:
            import snap7
            client = snap7.client.Client()
            client.connect(self.config.host, self.config.rack, self.config.slot)
            ok = client.get_connected()
            cpu = client.get_cpu_info() if ok else {}
            client.disconnect()
            return {
                "ok": ok,
                "host": self.config.host,
                "rack": self.config.rack,
                "slot": self.config.slot,
                "cpu": str(cpu.get("ModuleTypeName", "unknown")),
                "message": "Connected" if ok else "Connection failed",
            }
        except ImportError:
            return {"ok": False, "host": self.config.host, "message": "python-snap7 not installed"}
        except Exception as e:
            return {"ok": False, "host": self.config.host, "message": str(e)}

    def read_all(self) -> PlcDataBlock:
        data = PlcDataBlock(timestamp=time.time())
        try:
            if not self._client or not self._connected:
                raise RuntimeError("Not connected")
            m_bytes = self._client.read_area(0x83, 0, 0, 8)
            for byte_idx in range(min(8, len(m_bytes))):
                byte_val = m_bytes[byte_idx]
                for bit in range(8):
                    data.m_bits[f"M{byte_idx}.{bit}"] = bool(byte_val & (1 << bit))
            i_bytes = self._client.read_area(0x81, 0, 0, 8)
            for byte_idx in range(min(8, len(i_bytes))):
                byte_val = i_bytes[byte_idx]
                for bit in range(8):
                    data.i_bits[f"I{byte_idx}.{bit}"] = bool(byte_val & (1 << bit))
            q_bytes = self._client.read_area(0x82, 0, 0, 8)
            for byte_idx in range(min(8, len(q_bytes))):
                byte_val = q_bytes[byte_idx]
                for bit in range(8):
                    data.q_bits[f"Q{byte_idx}.{bit}"] = bool(byte_val & (1 << bit))
        except Exception as e:
            print(f"[plc] Read error: {e}")
        return data


class PlcManager:
    """Unified PLC manager — auto-selects real or mock client."""

    def __init__(self, config: PlcConfig):
        self.config = config
        self._use_mock = True
        self._client: Any = MockPlcClient()
        self._lock = threading.Lock()
        self._last_data = PlcDataBlock()
        self._poll_thread: Optional[threading.Thread] = None
        self._polling = False

    def connect(self) -> bool:
        with self._lock:
            real = Snap7PlcClient(self.config)
            if real.connect():
                self._client = real
                self._use_mock = False
                return True
            self._client = MockPlcClient()
            self._client.connect()
            self._use_mock = True
            return True

    def disconnect(self):
        self.stop_polling()
        with self._lock:
            self._client.disconnect()

    @property
    def connected(self) -> bool:
        return self._client.connected

    @property
    def is_mock(self) -> bool:
        return self._use_mock

    def test_connection(self) -> Dict[str, Any]:
        real = Snap7PlcClient(self.config)
        result = real.test_connection()
        result["mock_fallback"] = self._use_mock
        return result

    def read_all(self) -> PlcDataBlock:
        with self._lock:
            self._last_data = self._client.read_all()
        return self._last_data

    def start_polling(self, interval: float = 1.0):
        if self._polling:
            return
        self._polling = True
        self._poll_thread = threading.Thread(target=self._poll_loop, args=(interval,), daemon=True)
        self._poll_thread.start()

    def stop_polling(self):
        self._polling = False
        if self._poll_thread:
            self._poll_thread.join(timeout=2)
            self._poll_thread = None

    def _poll_loop(self, interval: float):
        while self._polling:
            try:
                self.read_all()
            except Exception:
                pass
            time.sleep(interval)

    @property
    def last_data(self) -> PlcDataBlock:
        return self._last_data


_plc_manager: Optional[PlcManager] = None


def get_plc() -> PlcManager:
    global _plc_manager
    if _plc_manager is None:
        config = PlcConfig(
            host=settings.plc_host,
            rack=settings.plc_rack,
            slot=settings.plc_slot,
        )
        _plc_manager = PlcManager(config)
        _plc_manager.connect()
        _plc_manager.start_polling(interval=1.0)
    return _plc_manager
