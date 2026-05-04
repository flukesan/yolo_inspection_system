"""In-process pub/sub broker for WebSocket fanout."""
import asyncio
import json
from typing import Any


class Broker:
    def __init__(self) -> None:
        self._subs: set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=128)
        async with self._lock:
            self._subs.add(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue) -> None:
        async with self._lock:
            self._subs.discard(q)

    async def publish(self, event: dict[str, Any]) -> None:
        payload = json.dumps(event, default=str)
        async with self._lock:
            targets = list(self._subs)
        for q in targets:
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                # slow consumer: drop oldest, push newest
                try:
                    q.get_nowait()
                    q.put_nowait(payload)
                except Exception:
                    pass


broker = Broker()
