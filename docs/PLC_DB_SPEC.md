# S7-300 PLC Data Block Specification

## DB1 — Trigger
| Addr | Type | Name |
|------|------|------|
| DBX0.0 | BOOL | Trigger |
| DBW2 | WORD | SeqNum |
| DBW4 | WORD | StationID |

## DB2 — Result
| Addr | Type | Name |
|------|------|------|
| DBX0.0 | BOOL | OK |
| DBX0.1 | BOOL | NG |
| DBW2 | WORD | ErrorCode |
| DBW4 | WORD | DefectClass |

## DB3 — Heartbeat
| Addr | Type | Name |
|------|------|------|
| DBX0.0 | BOOL | EdgePing |
| DBX1.0 | BOOL | PLCPong |
| DBW2 | WORD | PLCTimestamp |

## Interlocking (PLC SCL)
```
IF "DB1".Trigger AND NOT edge_old THEN edge_old := "DB1".Trigger; END_IF;
IF "DB2".NG THEN Conveyor_Stop := TRUE; Reject := TRUE; END_IF;
"DB3".PLCPong := "DB3".EdgePing;
```

## Error Codes
0x0000=OK, 0x0001=NG, 0xE001=CameraTimeout, 0xE002=PLCCommError, 0xE003=InferenceError, 0xE004=HeartbeatTimeout, 0xE005=BufferFull

## Timing
Poll=10ms, Heartbeat=3s (timeout 9s), Reject delay=50ms
