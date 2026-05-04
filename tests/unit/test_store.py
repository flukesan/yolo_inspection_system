"""Unit tests for the inspection store (in-memory mode)."""
import asyncio
import pytest
from server.store import InspectionStore


@pytest.fixture
def store():
    return InspectionStore()


@pytest.mark.asyncio
async def test_create_and_get(store):
    insp = await store.create(part_id="P1", result="OK", confidence=0.91)
    assert insp.id == 1 and insp.result == "OK"
    fetched = await store.get(insp.id)
    assert fetched is not None and fetched.part_id == "P1"


@pytest.mark.asyncio
async def test_list_filters(store):
    await store.create(part_id="A1", result="OK", station="Station-1")
    await store.create(part_id="A2", result="NG", defect_class="Scratch", station="Station-2")
    await store.create(part_id="B1", result="NG", defect_class="Dent", station="Station-1")

    items, total = await store.list(result="NG")
    assert total == 2 and all(i.result == "NG" for i in items)

    items, total = await store.list(station="Station-1")
    assert total == 2

    items, total = await store.list(part_id="A")
    assert total == 2


@pytest.mark.asyncio
async def test_pagination(store):
    for i in range(25):
        await store.create(part_id=f"P{i}", result="OK")
    items, total = await store.list(page=2, limit=10)
    assert total == 25 and len(items) == 10


@pytest.mark.asyncio
async def test_stats_and_breakdown(store):
    await store.create(part_id="A", result="OK")
    await store.create(part_id="B", result="OK")
    await store.create(part_id="C", result="NG", defect_class="Scratch")
    s = await store.stats()
    assert s["total"] == 3 and s["ok"] == 2 and s["ng"] == 1
    assert 0 < s["rate"] < 100
    breakdown = await store.defect_breakdown()
    assert breakdown == [{"name": "Scratch", "value": 1}]


@pytest.mark.asyncio
async def test_trend_has_24_buckets(store):
    out = await store.trend()
    assert len(out) == 24 and all("hour" in b for b in out)
