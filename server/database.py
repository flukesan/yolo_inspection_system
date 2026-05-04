"""Async PostgreSQL database pool."""
from server.config import settings


class Database:
    def __init__(self) -> None:
        self.pool = None
        self.available = False
        self.last_error: str | None = None

    async def connect(self) -> bool:
        try:
            import asyncpg
            self.pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                user=settings.postgres_user,
                password=settings.postgres_password,
                database=settings.postgres_db,
                min_size=1, max_size=10,
                command_timeout=10,
            )
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            self.available = True
            return True
        except Exception as exc:
            self.last_error = str(exc)
            self.pool = None
            self.available = False
            print(f"WARN: PostgreSQL unavailable ({exc!s}); using in-memory fallback")
            return False

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None
            self.available = False

    async def ping(self) -> bool:
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False


db = Database()
