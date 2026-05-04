"""Redis client for Streams + Pub/Sub. Optional — falls back to no-op."""
import json
from server.config import settings


class RedisClient:
    def __init__(self) -> None:
        self.conn = None
        self.available = False
        self.last_error: str | None = None

    async def connect(self) -> bool:
        try:
            import redis.asyncio as aioredis
            self.conn = aioredis.Redis(
                host=settings.redis_host, port=settings.redis_port,
                decode_responses=True, socket_timeout=3,
            )
            await self.conn.ping()
            self.available = True
            return True
        except Exception as exc:
            self.last_error = str(exc)
            self.conn = None
            self.available = False
            print(f"WARN: Redis unavailable ({exc!s})")
            return False

    async def disconnect(self) -> None:
        if self.conn:
            try:
                await self.conn.close()
            except Exception:
                pass
            self.conn = None
            self.available = False

    async def ping(self) -> bool:
        if not (self.available and self.conn):
            return False
        try:
            return bool(await self.conn.ping())
        except Exception:
            return False

    async def publish(self, channel: str, data: dict) -> None:
        if self.available and self.conn:
            try:
                await self.conn.publish(channel, json.dumps(data, default=str))
            except Exception:
                pass

    async def xadd(self, stream: str, data: dict) -> None:
        if self.available and self.conn:
            try:
                payload = {k: json.dumps(v, default=str) if not isinstance(v, (str, int, float, bytes)) else v for k, v in data.items()}
                await self.conn.xadd(stream, payload)
            except Exception:
                pass


redis_client = RedisClient()
