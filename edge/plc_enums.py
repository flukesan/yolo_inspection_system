"""Inspection Result and Error Code Enums."""
from enum import IntEnum, auto

class InspectionResult(IntEnum):
    OK = 0
    NG = 1
    TIMEOUT = 2
    ERROR = 3

class ErrorCode(IntEnum):
    OK = 0x0000
    NG = 0x0001
    NG_RECOVERABLE = 0x0002
    CAMERA_TIMEOUT = 0xE001
    PLC_COMM_ERROR = 0xE002
    INFERENCE_ERROR = 0xE003
    HEARTBEAT_TIMEOUT = 0xE004
    BUFFER_FULL = 0xE005

class PLCState(IntEnum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    IDLE = auto()
    READY = auto()
    INSPECTING = auto()
    RESULT = auto()
    ERROR = auto()

class TriggerMode(IntEnum):
    MANUAL = 0
    AUTO = 1
    SEQUENCE = 2
