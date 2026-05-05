"""FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server.routes.auth import router as auth_router
from server.routes.inspection import router as inspection_router
from server.routes.images import router as images_router
from server.routes.websocket import router as ws_router
from server.routes.camera import router as camera_router
from server.routes.plc import router as plc_router
from server.routes.model import router as model_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting...")
    yield
    print("Server shutting down...")

app = FastAPI(title="YOLO Inspection API", version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Register route modules
app.include_router(auth_router)
app.include_router(inspection_router)
app.include_router(images_router)
app.include_router(ws_router)
app.include_router(camera_router)
app.include_router(plc_router)
app.include_router(model_router)

@app.get("/api/health")
async def health():
    return {"status": "healthy", "postgres": "healthy", "redis": "healthy", "minio": "healthy"}

@app.get("/")
async def root():
    return {"service": "YOLO Inspection API v2.0.0", "docs": "/docs"}
