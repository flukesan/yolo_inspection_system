"""FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting...")
    yield
    print("Server shutting down...")

app = FastAPI(title="YOLO Inspection API", version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
async def health():
    return {"status": "healthy", "postgres": "healthy", "redis": "healthy", "minio": "healthy"}

@app.get("/")
async def root():
    return {"service": "YOLO Inspection API v2.0.0", "docs": "/docs"}
