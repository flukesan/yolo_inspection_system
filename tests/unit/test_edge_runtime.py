"""Tests for edge inference runtime: inspection cycle wiring."""
import asyncio
import pytest

from edge.main import EdgeRuntime
from edge.plc_enums import InspectionResult, PLCState


class FakeAPI:
    def __init__(self) -> None:
        self.inspections = []
        self.heartbeats = []

    async def login(self):
        return True

    async def report_inspection(self, payload):
        self.inspections.append(payload)
        return True

    async def heartbeat(self, payload):
        self.heartbeats.append(payload)
        return True

    async def close(self):
        pass


class FakeInference:
    def __init__(self, result="OK"):
        self.result = result

    async def predict(self, frame=None):
        return {"result": self.result, "confidence": 0.88, "defect_class": None if self.result == "OK" else "Scratch"}


@pytest.mark.asyncio
async def test_cycle_ok_writes_plc_and_reports():
    rt = EdgeRuntime()
    rt.api = FakeAPI()
    rt.inference = FakeInference("OK")
    await rt.plc.connect()
    await rt._run_one_cycle()
    assert rt.plc._mock_db["result"] == InspectionResult.OK
    assert len(rt.api.inspections) == 1
    assert rt.api.inspections[0]["result"] == "OK"


@pytest.mark.asyncio
async def test_cycle_ng_writes_plc_and_reports_defect():
    rt = EdgeRuntime()
    rt.api = FakeAPI()
    rt.inference = FakeInference("NG")
    await rt.plc.connect()
    await rt._run_one_cycle()
    assert rt.plc._mock_db["result"] == InspectionResult.NG
    payload = rt.api.inspections[0]
    assert payload["result"] == "NG" and payload["defect_class"] == "Scratch"
    assert payload["error_code"] is not None


@pytest.mark.asyncio
async def test_inspection_loop_stops_on_event():
    rt = EdgeRuntime()
    rt.api = FakeAPI()
    rt.inference = FakeInference("OK")
    await rt.plc.connect()
    rt.plc.simulate_trigger(True)
    task = asyncio.create_task(rt.inspection_loop())
    # let the loop pick up the trigger and process at least one cycle
    for _ in range(20):
        await asyncio.sleep(0.05)
        if rt.api.inspections:
            break
    rt.stop()
    await asyncio.wait_for(task, timeout=2.0)
    assert len(rt.api.inspections) >= 1
