"""FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.database import db
from server.minio_client import minio_client
from server.redis_client import redis_client
from server.routes.auth import router as auth_router
from server.routes.images import router as images_router
from server.routes.inspection import router as inspection_router
from server.routes.websocket import router as ws_router
from server.store import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting...")
    await db.connect()
    if db.available:
        store.attach_pool(db.pool)
    await redis_client.connect()
    await minio_client.connect()
    print(
        f"Subsystems — postgres={db.available} redis={redis_client.available} "
        f"minio={minio_client.available}"
    )
    try:
        yield
    finally:
        print("Server shutting down...")
        await db.disconnect()
        await redis_client.disconnect()


app = FastAPI(title="YOLO Inspection API", version="2.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(inspection_router)
app.include_router(images_router)
app.include_router(ws_router)


@app.get("/api/health")
async def health():
    pg = await db.ping()
    rd = await redis_client.ping()
    mn = await minio_client.ping()
    overall = "healthy" if (pg or not db.pool) else "degraded"
    return {
        "status": overall,
        "postgres": "healthy" if pg else "unavailable",
        "redis": "healthy" if rd else "unavailable",
        "minio": "healthy" if mn else "unavailable",
        "store": "postgres" if store.using_db else "in-memory",
    }


@app.get("/")
async def root():
    return {"service": "YOLO Inspection API v2.0.0", "docs": "/docs"}
