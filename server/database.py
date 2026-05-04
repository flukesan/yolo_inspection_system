"""Async PostgreSQL database pool."""
import asyncio
from server.config import settings

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            import asyncpg
            self.pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
                min_size=1, max_size=10
            )
        except Exception:
            print("WARN: PostgreSQL unavailable, using fallback")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def fetch(self, query: str, *args):
        if not self.pool:
            return []
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def execute(self, query: str, *args):
        if not self.pool:
            return None
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

db = Database()
