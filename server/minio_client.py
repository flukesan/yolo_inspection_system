"""MinIO client for defect image storage. Falls back to local /tmp on failure."""
import io
import os
import uuid
from pathlib import Path
from typing import Optional
from server.config import settings


LOCAL_FALLBACK_DIR = Path(os.environ.get("LOCAL_IMAGE_DIR", "/tmp/yolo_images"))


class MinioClient:
    def __init__(self) -> None:
        self.client = None
        self.available = False
        self.last_error: str | None = None
        LOCAL_FALLBACK_DIR.mkdir(parents=True, exist_ok=True)

    async def connect(self) -> bool:
        try:
            from minio import Minio
            self.client = Minio(
                f"{settings.minio_host}:{settings.minio_port}",
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=False,
            )
            if not self.client.bucket_exists(settings.minio_bucket):
                self.client.make_bucket(settings.minio_bucket)
            self.available = True
            return True
        except Exception as exc:
            self.last_error = str(exc)
            self.client = None
            self.available = False
            print(f"WARN: MinIO unavailable ({exc!s}); using local fallback at {LOCAL_FALLBACK_DIR}")
            return False

    async def ping(self) -> bool:
        if not self.available or not self.client:
            return False
        try:
            self.client.bucket_exists(settings.minio_bucket)
            return True
        except Exception:
            return False

    async def upload(self, name: str, data: bytes, content_type: str = "image/jpeg") -> str:
        # Always assign a unique key to avoid collisions.
        ext = Path(name).suffix or ".jpg"
        key = f"{uuid.uuid4().hex}{ext}"
        if self.available and self.client:
            self.client.put_object(
                settings.minio_bucket, key, io.BytesIO(data), len(data),
                content_type=content_type,
            )
            return key
        path = LOCAL_FALLBACK_DIR / key
        path.write_bytes(data)
        return key

    def get_url(self, name: str) -> str:
        if self.available and self.client:
            try:
                return self.client.presigned_get_object(settings.minio_bucket, name)
            except Exception:
                pass
        return f"/api/images/{name}/data"

    def fetch(self, name: str) -> Optional[tuple[bytes, str]]:
        """Return (bytes, content_type) or None."""
        if self.available and self.client:
            try:
                resp = self.client.get_object(settings.minio_bucket, name)
                try:
                    data = resp.read()
                    ct = resp.headers.get("Content-Type", "application/octet-stream")
                finally:
                    resp.close(); resp.release_conn()
                return data, ct
            except Exception:
                return None
        path = LOCAL_FALLBACK_DIR / name
        if path.exists():
            return path.read_bytes(), "image/jpeg"
        return None


minio_client = MinioClient()
