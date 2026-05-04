"""Unit tests for PLC Agent."""
import pytest, asyncio
from edge.plc_agent import S7PLCAgent
from edge.plc_enums import PLCState, InspectionResult, ErrorCode

class TestPLCAgent:
    def setup_method(self):
        self.agent = S7PLCAgent(host="127.0.0.1")

    @pytest.mark.asyncio
    async def test_connect(self):
        result = await self.agent.connect()
        assert result is True
        assert self.agent.connected
        assert self.agent.state == PLCState.IDLE

    @pytest.mark.asyncio
    async def test_disconnect(self):
        await self.agent.connect()
        await self.agent.disconnect()
        assert not self.agent.connected
        assert self.agent.state == PLCState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_heartbeat_ok(self):
        await self.agent.connect()
        result = await self.agent.heartbeat()
        assert result is True

    @pytest.mark.asyncio
    async def test_heartbeat_fail_when_disconnected(self):
        result = await self.agent.heartbeat()
        assert result is False

    @pytest.mark.asyncio
    async def test_read_trigger_false(self):
        await self.agent.connect()
        result = await self.agent.read_trigger()
        assert result is False

    @pytest.mark.asyncio
    async def test_read_trigger_true(self):
        await self.agent.connect()
        self.agent.simulate_trigger(True)
        result = await self.agent.read_trigger()
        assert result is True

    @pytest.mark.asyncio
    async def test_write_result_ok(self):
        await self.agent.connect()
        await self.agent.write_result(InspectionResult.OK)
        assert self.agent._mock_db["result"] == InspectionResult.OK

    @pytest.mark.asyncio
    async def test_write_result_ng(self):
        await self.agent.connect()
        await self.agent.write_result(InspectionResult.NG, ErrorCode.NG)
        assert self.agent._mock_db["result"] == InspectionResult.NG
        assert self.agent._mock_db["error_code"] == ErrorCode.NG

    @pytest.mark.asyncio
    async def test_reconnect_success(self):
        result = await self.agent.reconnect()
        assert result is True
        assert self.agent.connected
