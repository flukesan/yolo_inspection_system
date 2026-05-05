"""Edge inference entry point.

Connects to the configured PLC, polls for triggers, runs (mock) inference,
writes the result back to the PLC, and reports events + heartbeats to the
backend API. Falls back gracefully when snap7 / camera / API are unavailable.
"""
from __future__ import annotations

import asyncio
import os
import random
import time
from typing import Optional

from edge.plc_agent import S7PLCAgent
from edge.plc_enums import ErrorCode, InspectionResult, PLCState
from edge.model_manager import get_model_manager
from aiohttp import web


async def handle_reload(request: web.Request) -> web.Response:
    """POST /reload — reload current or specified model."""
    try:
        body = await request.json()
        model_name = body.get("model", "")
    except Exception:
        model_name = ""

    runtime = request.app["runtime"]
    if model_name:
        ok = runtime.model_manager.load(model_name)
    else:
        # Just reopen current model
        current = runtime.model_manager.current_model
        if current:
            ok = runtime.model_manager.load(current.name)
        else:
            ok = False

    return web.json_response({
        "ok": ok,
        "model": runtime.model_manager.current_model.name if runtime.model_manager.current_model else None,
    })


async def handle_models(request: web.Request) -> web.Response:
    """GET /models — list available models."""
    runtime = request.app["runtime"]
    models = runtime.model_manager.list_models()
    return web.json_response({
        "models": [m.to_dict() for m in models],
        "current": runtime.model_manager.current_model.name if runtime.model_manager.current_model else None,
    })

API_BASE = os.environ.get("API_BASE", "http://api-server:8000")
API_USERNAME = os.environ.get("EDGE_USERNAME", os.environ.get("OPERATOR_USERNAME", "operator"))
API_PASSWORD = os.environ.get("EDGE_PASSWORD", os.environ.get("OPERATOR_PASSWORD", "operator123"))
HEARTBEAT_INTERVAL = float(os.environ.get("HEARTBEAT_INTERVAL", "3.0"))
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "0.05"))
PLC_HOST = os.environ.get("PLC_HOST", "192.168.1.10")
PLC_RACK = int(os.environ.get("PLC_RACK", "0"))
PLC_SLOT = int(os.environ.get("PLC_SLOT", "2"))


class APIClient:
    """Lightweight HTTP client. Tolerates network failures without crashing."""

    def __init__(self, base: str, username: str, password: str) -> None:
        self.base = base.rstrip("/")
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self._session = None

    async def _ensure_session(self):
        if self._session is None:
            try:
                import httpx
            except Exception:
                return None
            self._session = httpx.AsyncClient(base_url=self.base, timeout=5.0)
        return self._session

    async def login(self) -> bool:
        s = await self._ensure_session()
        if s is None:
            return False
        try:
            r = await s.post(
                "/api/auth/login",
                json={"username": self.username, "password": self.password},
            )
            if r.status_code == 200:
                self.token = r.json().get("access_token")
                return bool(self.token)
        except Exception:
            pass
        return False

    async def _post(self, path: str, payload: dict) -> bool:
        s = await self._ensure_session()
        if s is None:
            return False
        if not self.token and not await self.login():
            return False
        try:
            r = await s.post(path, json=payload, headers={"Authorization": f"Bearer {self.token}"})
            if r.status_code == 401:
                if await self.login():
                    r = await s.post(path, json=payload, headers={"Authorization": f"Bearer {self.token}"})
            return 200 <= r.status_code < 300
        except Exception:
            return False

    async def report_inspection(self, payload: dict) -> bool:
        return await self._post("/api/inspection", payload)

    async def heartbeat(self, payload: dict) -> bool:
        return await self._post("/api/plc/heartbeat", payload)

    async def close(self) -> None:
        if self._session is not None:
            try:
                await self._session.aclose()
            except Exception:
                pass


class MockInference:
    """Pluggable inference. Replace with ONNX runtime when a model is loaded."""

    DEFECTS = ["Scratch", "Dent", "Misalign", "Missing", "Color"]

    def __init__(self, ok_rate: float = 0.93) -> None:
        self.ok_rate = ok_rate

    async def predict(self, frame: Optional[bytes] = None) -> dict:
        await asyncio.sleep(random.uniform(0.015, 0.035))
        ok = random.random() < self.ok_rate
        return {
            "result": "OK" if ok else "NG",
            "confidence": round(random.uniform(0.65, 0.99), 4),
            "defect_class": None if ok else random.choice(self.DEFECTS),
        }


class EdgeRuntime:
    def __init__(self) -> None:
        self.plc = S7PLCAgent(host=PLC_HOST, rack=PLC_RACK, slot=PLC_SLOT)
        self.api = APIClient(API_BASE, API_USERNAME, API_PASSWORD)
        self.model_manager = get_model_manager(
            os.environ.get("MODEL_PATH", "/models")
        )
        if not self.model_manager.loaded:
            print("[edge] WARNING: No ONNX model found — using mock fallback")
            self.inference = MockInference()
        else:
            self.inference = self.model_manager  # ModelManager.predict()
        self.station = os.environ.get("STATION", "Station-1")
        self.part_counter = 0
        self._stop = asyncio.Event()

    async def heartbeat_loop(self) -> None:
        while not self._stop.is_set():
            await self.plc.heartbeat()
            await self.api.heartbeat({
                "connected": self.plc.connected,
                "state": self.plc.state.name,
                "last_error": self.plc.last_error,
            })
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=HEARTBEAT_INTERVAL)
            except asyncio.TimeoutError:
                pass

    async def inspection_loop(self) -> None:
        while not self._stop.is_set():
            if not self.plc.connected:
                await self.plc.reconnect()
                if not self.plc.connected:
                    await asyncio.sleep(1.0)
                    continue
            try:
                triggered = await self.plc.read_trigger()
            except Exception as exc:
                self.plc.last_error = str(exc)
                await asyncio.sleep(0.5)
                continue
            if triggered:
                await self._run_one_cycle()
                # Clear simulated trigger to avoid retriggering on the same edge.
                self.plc.simulate_trigger(False)
            await asyncio.sleep(POLL_INTERVAL)

    async def _run_one_cycle(self) -> None:
        self.part_counter += 1
        part_id = f"{self.station}-{int(time.time())}-{self.part_counter:04d}"
        prev_state = self.plc.state
        self.plc.state = PLCState.INSPECTING
        try:
            if self.inference is self.model_manager:
                # ONNX inference — synchronous, run in thread
                import numpy as np
                loop = asyncio.get_running_loop()
                info = self.model_manager.current_model
                if info is None:
                    raise RuntimeError("No model loaded")
                # Create dummy frame matching input shape (batch=1)
                shape = (1,) + info.input_shape[1:]
                dummy = np.random.randn(*shape).astype(np.float32)
                outputs = await loop.run_in_executor(None, self.model_manager.predict, dummy)
                # Mock: treat max confidence as detection
                conf = float(outputs.max()) if outputs.size > 0 else 0.5
                ok = conf < 0.5
                prediction = {
                    "result": "OK" if ok else "NG",
                    "confidence": round(conf, 4),
                    "defect_class": None if ok else "Defect",
                }
            else:
                prediction = await self.inference.predict()
        except Exception as exc:
            self.plc.last_error = f"inference: {exc!s}"
            await self.plc.write_result(InspectionResult.ERROR, ErrorCode.INFERENCE_ERROR)
            self.plc.state = prev_state
            return

        result_enum = InspectionResult.OK if prediction["result"] == "OK" else InspectionResult.NG
        error_enum = ErrorCode.OK if prediction["result"] == "OK" else ErrorCode.NG
        await self.plc.write_result(result_enum, error_enum)
        self.plc.state = PLCState.RESULT

        await self.api.report_inspection({
            "part_id": part_id,
            "result": prediction["result"],
            "defect_class": prediction["defect_class"],
            "station": self.station,
            "confidence": prediction["confidence"],
            "error_code": f"0x{int(error_enum):04X}" if error_enum != ErrorCode.OK else None,
        })
        self.plc.state = PLCState.IDLE

    async def run(self) -> None:
        print(f"Edge runtime starting. PLC={PLC_HOST} API={API_BASE}")
        await self.plc.connect()
        await self.api.login()
        try:
            await asyncio.gather(self.heartbeat_loop(), self.inspection_loop())
        finally:
            await self.plc.disconnect()
            await self.api.close()

    def stop(self) -> None:
        self._stop.set()


async def main() -> None:
    runtime = EdgeRuntime()

    # Start mini HTTP server for reload commands
    app = web.Application()
    app["runtime"] = runtime
    app.router.add_post("/reload", handle_reload)
    app.router.add_get("/models", handle_models)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8001)
    await site.start()
    print(f"[edge] Reload API listening on port 8001")

    try:
        await runtime.run()
    except KeyboardInterrupt:
        runtime.stop()
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
