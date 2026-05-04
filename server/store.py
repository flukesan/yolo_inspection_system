"""Inspection store: PostgreSQL when available, in-memory fallback otherwise."""
from __future__ import annotations
import asyncio
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Optional


@dataclass
class Inspection:
    id: int
    part_id: str
    result: str
    defect_class: Optional[str]
    station: str
    confidence: float
    error_code: Optional[str]
    image_id: Optional[int]
    timestamp: datetime

    def to_dict(self) -> dict:
        d = asdict(self)
        d["timestamp"] = self.timestamp.astimezone(timezone.utc).isoformat()
        return d


class InspectionStore:
    """Persistence layer with graceful fallback when Postgres is unavailable."""

    def __init__(self) -> None:
        self._mem: list[Inspection] = []
        self._next_id = 1
        self._lock = asyncio.Lock()
        self._pool = None  # asyncpg pool when available

    def attach_pool(self, pool) -> None:
        self._pool = pool

    @property
    def using_db(self) -> bool:
        return self._pool is not None

    async def create(
        self,
        *,
        part_id: str,
        result: str,
        defect_class: Optional[str] = None,
        station: str = "Station-1",
        confidence: float = 0.0,
        error_code: Optional[str] = None,
        image_id: Optional[int] = None,
    ) -> Inspection:
        ts = datetime.now(timezone.utc)
        if self.using_db:
            row = await self._pool.fetchrow(
                """
                INSERT INTO inspections
                  (part_id, result, defect_class, station, confidence, error_code, image_id, timestamp)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                RETURNING id, timestamp
                """,
                part_id, result, defect_class, station, float(confidence),
                error_code, image_id, ts,
            )
            return Inspection(
                id=row["id"], part_id=part_id, result=result, defect_class=defect_class,
                station=station, confidence=float(confidence), error_code=error_code,
                image_id=image_id, timestamp=row["timestamp"],
            )
        async with self._lock:
            insp = Inspection(
                id=self._next_id, part_id=part_id, result=result, defect_class=defect_class,
                station=station, confidence=float(confidence), error_code=error_code,
                image_id=image_id, timestamp=ts,
            )
            self._next_id += 1
            self._mem.append(insp)
            return insp

    async def get(self, inspection_id: int) -> Optional[Inspection]:
        if self.using_db:
            row = await self._pool.fetchrow(
                "SELECT * FROM inspections WHERE id=$1", inspection_id
            )
            return _row_to_inspection(row) if row else None
        return next((i for i in self._mem if i.id == inspection_id), None)

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        result: Optional[str] = None,
        station: Optional[str] = None,
        part_id: Optional[str] = None,
    ) -> tuple[list[Inspection], int]:
        page = max(1, page)
        limit = max(1, min(100, limit))
        offset = (page - 1) * limit

        if self.using_db:
            where, args = [], []
            if result:
                args.append(result); where.append(f"result = ${len(args)}")
            if station:
                args.append(station); where.append(f"station = ${len(args)}")
            if part_id:
                args.append(f"%{part_id}%"); where.append(f"part_id ILIKE ${len(args)}")
            wsql = ("WHERE " + " AND ".join(where)) if where else ""
            total = await self._pool.fetchval(f"SELECT COUNT(*) FROM inspections {wsql}", *args)
            rows = await self._pool.fetch(
                f"SELECT * FROM inspections {wsql} ORDER BY timestamp DESC LIMIT {limit} OFFSET {offset}",
                *args,
            )
            return [_row_to_inspection(r) for r in rows], int(total or 0)

        items = self._mem
        if result:
            items = [i for i in items if i.result == result]
        if station:
            items = [i for i in items if i.station == station]
        if part_id:
            items = [i for i in items if part_id.lower() in i.part_id.lower()]
        items = sorted(items, key=lambda x: x.timestamp, reverse=True)
        return items[offset:offset + limit], len(items)

    async def stats(self, hours: int = 24) -> dict:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        if self.using_db:
            row = await self._pool.fetchrow(
                """
                SELECT COUNT(*) AS total,
                       COUNT(*) FILTER (WHERE result='OK') AS ok,
                       COUNT(*) FILTER (WHERE result='NG') AS ng
                FROM inspections WHERE timestamp >= $1
                """,
                cutoff,
            )
            total, ok, ng = int(row["total"]), int(row["ok"]), int(row["ng"])
        else:
            window = [i for i in self._mem if i.timestamp >= cutoff]
            total = len(window)
            ok = sum(1 for i in window if i.result == "OK")
            ng = sum(1 for i in window if i.result == "NG")
        rate = (ok / total * 100.0) if total else 100.0
        return {"total": total, "ok": ok, "ng": ng, "rate": round(rate, 2), "period_hours": hours}

    async def trend(self, hours: int = 24) -> list[dict]:
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        buckets: dict[datetime, dict] = {
            now - timedelta(hours=hours - 1 - h): {"ok": 0, "ng": 0}
            for h in range(hours)
        }
        if self.using_db:
            rows = await self._pool.fetch(
                """
                SELECT date_trunc('hour', timestamp) AS bucket,
                       result, COUNT(*) AS c
                FROM inspections WHERE timestamp >= $1
                GROUP BY bucket, result
                """,
                now - timedelta(hours=hours - 1),
            )
            for r in rows:
                b = r["bucket"]
                if b in buckets:
                    buckets[b][r["result"].lower()] = int(r["c"])
        else:
            cutoff = now - timedelta(hours=hours - 1)
            for i in self._mem:
                if i.timestamp < cutoff:
                    continue
                b = i.timestamp.replace(minute=0, second=0, microsecond=0)
                if b in buckets and i.result in ("OK", "NG"):
                    buckets[b][i.result.lower()] += 1

        out = []
        for ts in sorted(buckets):
            ok, ng = buckets[ts]["ok"], buckets[ts]["ng"]
            tot = ok + ng
            rate = (ok / tot * 100.0) if tot else 100.0
            out.append({
                "hour": ts.strftime("%H:%M"),
                "total": tot, "ok": ok, "ng": ng,
                "ok_rate": round(rate, 2),
            })
        return out

    async def defect_breakdown(self, hours: int = 24) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        if self.using_db:
            rows = await self._pool.fetch(
                """
                SELECT COALESCE(defect_class,'Other') AS name, COUNT(*) AS c
                FROM inspections
                WHERE result='NG' AND timestamp >= $1
                GROUP BY name ORDER BY c DESC
                """,
                cutoff,
            )
            return [{"name": r["name"], "value": int(r["c"])} for r in rows]
        counts: dict[str, int] = defaultdict(int)
        for i in self._mem:
            if i.result == "NG" and i.timestamp >= cutoff:
                counts[i.defect_class or "Other"] += 1
        return [{"name": n, "value": v} for n, v in sorted(counts.items(), key=lambda x: -x[1])]


def _row_to_inspection(row) -> Inspection:
    return Inspection(
        id=row["id"], part_id=row["part_id"], result=row["result"],
        defect_class=row["defect_class"], station=row["station"],
        confidence=float(row["confidence"] or 0.0),
        error_code=row["error_code"], image_id=row["image_id"],
        timestamp=row["timestamp"],
    )


store = InspectionStore()
