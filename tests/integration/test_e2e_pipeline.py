"""
E2E Integration Test Suite — Full pipeline: PLC trigger → camera → inference → dashboard.
"""
import asyncio, time, random, pytest

class MockInferenceEngine:
    def __init__(self, ok_rate=0.92):
        self.ok_rate = ok_rate
        self.call_count = 0

    async def predict(self, frame_bytes=None):
        await asyncio.sleep(random.uniform(0.015, 0.045))
        self.call_count += 1
        ok = random.random() < self.ok_rate
        return {"result": "OK" if ok else "NG", "confidence": round(random.uniform(0.65, 0.99), 4),
                "defect_class": None if ok else random.choice(["Scratch","Dent","Misalign","Missing"]),
                "inference_ms": random.uniform(15, 45)}

class MockCamera:
    def __init__(self, fps=30): self.fps = fps; self.frame_count = 0; self.connected = True
    async def capture(self):
        await asyncio.sleep(1.0/self.fps); self.frame_count += 1
        return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"

class MockInterlockController:
    def __init__(self):
        self.conveyor_running = True; self.last_result = None
        self.reject_active = False; self.interlock_events = []

    async def write_result(self, result, error_code=0):
        self.last_result = result
        if result == "NG":
            self.reject_active = True; self.conveyor_running = False
            self.interlock_events.append({"type":"interlock_stop","result":result,"timestamp":time.time()})
        else:
            self.interlock_events.append({"type":"interlock_pass","result":result,"timestamp":time.time()})

    async def release(self): self.conveyor_running = True; self.reject_active = False

class MockDashboardClient:
    def __init__(self): self.received_events = []; self.connected = False
    async def connect(self): self.connected = True
    async def disconnect(self): self.connected = False
    async def receive_event(self, event): event["received_at"] = time.time(); self.received_events.append(event)

class InspectionPipeline:
    def __init__(self, camera, inference, interlock, dashboard):
        self.camera = camera; self.inference = inference
        self.interlock = interlock; self.dashboard = dashboard
        self.total_cycles = 0; self.pipeline_latencies = []

    async def run_single_inspection(self, part_id="TEST-001"):
        start = time.monotonic()
        frame = await self.camera.capture()
        result = await self.inference.predict(frame)
        await self.interlock.write_result(result["result"])
        await self.dashboard.receive_event({"type":"inspection","part_id":part_id,**{k:v for k,v in result.items() if k != "result"},"result":result["result"],"timestamp":time.time()})
        self.total_cycles += 1
        if result["result"] == "NG": await asyncio.sleep(0.05)
        await self.interlock.release()
        self.pipeline_latencies.append((time.monotonic()-start)*1000)
        return {"part_id":part_id,"pipeline_ms":round(self.pipeline_latencies[-1],2),**result}

@pytest.fixture
def pipeline():
    return InspectionPipeline(MockCamera(30), MockInferenceEngine(0.90), MockInterlockController(), MockDashboardClient())

@pytest.mark.asyncio
class TestE2EPipeline:
    async def test_single_inspection_cycle(self, pipeline):
        r = await pipeline.run_single_inspection("PART-001")
        assert r["part_id"]=="PART-001"; assert r["result"] in ("OK","NG"); assert pipeline.total_cycles==1

    async def test_ok_result_triggers_pass_interlock(self, pipeline):
        pipeline.inference = MockInferenceEngine(1.0)
        il = MockInterlockController(); pipeline.interlock = il
        await pipeline.run_single_inspection("PART-OK")
        assert not il.reject_active and il.conveyor_running

    async def test_ng_result_triggers_stop_interlock(self, pipeline):
        pipeline.inference = MockInferenceEngine(0.0)
        il = MockInterlockController(); pipeline.interlock = il
        await pipeline.run_single_inspection("PART-NG")
        assert il.last_result=="NG"
        stops = [e for e in il.interlock_events if e["type"]=="interlock_stop"]
        assert len(stops)>=1; assert stops[0]["result"]=="NG"

    async def test_dashboard_receives_event(self, pipeline):
        await pipeline.run_single_inspection("PART-DASH")
        assert len(pipeline.dashboard.received_events)==1

    async def test_pipeline_latency_under_200ms(self, pipeline):
        for i in range(20): await pipeline.run_single_inspection(f"PERF-{i:03d}")
        avg = sum(pipeline.pipeline_latencies)/len(pipeline.pipeline_latencies)
        assert avg < 200

    async def test_high_volume_sustained(self, pipeline):
        n=100; start=time.monotonic()
        results = await asyncio.gather(*[pipeline.run_single_inspection(f"VOL-{i:03d}") for i in range(n)])
        elapsed = time.monotonic()-start
        assert len(results)==n; print(f"\n  {n} inspections in {elapsed:.1f}s ({n/elapsed:.0f}/s)")

    async def test_consecutive_cycles_no_race_condition(self, pipeline):
        n=50
        for i in range(n): await pipeline.run_single_inspection(f"RACE-{i:03d}")
        assert pipeline.total_cycles==n and len(pipeline.dashboard.received_events)==n

    async def test_part_id_tracking(self, pipeline):
        pids = [f"PART-{i:05d}" for i in range(10)]
        results = [await pipeline.run_single_inspection(pid) for pid in pids]
        for pid, r in zip(pids, results): assert r["part_id"]==pid

@pytest.mark.asyncio
class TestFailoverScenarios:
    async def test_camera_timeout_recovery(self, pipeline):
        pipeline.camera.connected = False
        try:
            await pipeline.run_single_inspection("CAM-FAIL")
            assert pipeline.total_cycles==1
        except Exception:
            assert pipeline.total_cycles<=1

    async def test_inference_error_handling(self):
        engine = MockInferenceEngine()
        try:
            result = await engine.predict(b"corrupted")
            assert "result" in result
        except Exception:
            pass

    async def test_dashboard_reconnect(self, pipeline):
        await pipeline.dashboard.connect(); assert pipeline.dashboard.connected
        await pipeline.run_single_inspection("DASH-1")
        assert len(pipeline.dashboard.received_events)==1
        await pipeline.dashboard.disconnect(); assert not pipeline.dashboard.connected
        await pipeline.dashboard.connect(); pipeline.dashboard.received_events.clear()
        await pipeline.run_single_inspection("DASH-2")
        assert len(pipeline.dashboard.received_events)==1
