"""Image routes."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from server.auth import get_current_user
from server.minio_client import minio_client

router = APIRouter(prefix="/api/images", tags=["images"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/upload")
async def upload_image(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported media type: {content_type}")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty upload")
    name = await minio_client.upload(file.filename or "upload.jpg", data, content_type)
    return {"name": name, "size": len(data), "url": minio_client.get_url(name)}


@router.get("/{name}")
async def get_image(name: str, user: dict = Depends(get_current_user)):
    return {"name": name, "url": minio_client.get_url(name)}


@router.get("/{name}/url")
async def get_image_url(name: str, user: dict = Depends(get_current_user)):
    return {"url": minio_client.get_url(name)}


@router.get("/{name}/data")
async def get_image_data(name: str, user: dict = Depends(get_current_user)):
    item = minio_client.fetch(name)
    if not item:
        raise HTTPException(status_code=404, detail="Image not found")
    data, content_type = item
    return Response(content=data, media_type=content_type)
