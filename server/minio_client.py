"""MinIO client for defect image storage."""
import io
from typing import Optional
from server.config import settings

class MinioClient:
    def __init__(self):
        self.client = None
        self.available = False

    async def connect(self):
        try:
            from minio import Minio
            self.client = Minio(
                f"{settings.minio_host}:{settings.minio_port}",
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=False
            )
            if not self.client.bucket_exists(settings.minio_bucket):
                self.client.make_bucket(settings.minio_bucket)
            self.available = True
        except Exception:
            print("WARN: MinIO unavailable, images stored locally")

    async def upload(self, name: str, data: bytes, content_type: str = "image/jpeg") -> Optional[str]:
        if not self.available:
            return f"/tmp/{name}"
        self.client.put_object(settings.minio_bucket, name, io.BytesIO(data), len(data), content_type=content_type)
        return name

    def get_url(self, name: str) -> str:
        if not self.available:
            return f"/tmp/{name}"
        return self.client.presigned_get_object(settings.minio_bucket, name)

minio_client = MinioClient()
