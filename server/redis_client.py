"""Redis client for Streams + Pub/Sub."""
import asyncio
import json

class RedisClient:
    def __init__(self):
        self.conn = None
        self.available = False

    async def connect(self):
        try:
            import redis.asyncio as aioredis
            self.conn = aioredis.Redis(host="localhost", port=6379, decode_responses=True)
            await self.conn.ping()
            self.available = True
        except Exception:
            print("WARN: Redis unavailable, using fallback")

    async def disconnect(self):
        if self.conn:
            await self.conn.close()

    async def publish(self, channel: str, data: dict):
        if self.available and self.conn:
            await self.conn.publish(channel, json.dumps(data))

    async def xadd(self, stream: str, data: dict):
        if self.available and self.conn:
            await self.conn.xadd(stream, data)

redis_client = RedisClient()
