"""Image routes."""
from fastapi import APIRouter, UploadFile, File, Depends
from server.auth import get_current_user
from server.minio_client import minio_client

router = APIRouter(prefix="/api/images", tags=["images"])

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    data = await file.read()
    name = await minio_client.upload(file.filename, data)
    return {"name": name, "size": len(data)}

@router.get("/{name}")
async def get_image(name: str, user: dict = Depends(get_current_user)):
    return {"name": name, "url": minio_client.get_url(name)}

@router.get("/{name}/url")
async def get_image_url(name: str, user: dict = Depends(get_current_user)):
    return {"url": minio_client.get_url(name)}
