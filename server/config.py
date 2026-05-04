"""Application configuration loader."""
import os
import yaml
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "yolo"
    postgres_password: str = "yolo"
    postgres_db: str = "yolo_inspection"
    redis_host: str = "localhost"
    redis_port: int = 6379
    minio_host: str = "localhost"
    minio_port: int = 9000
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "defect-images"
    plc_host: str = "192.168.1.10"
    plc_rack: int = 0
    plc_slot: int = 2
    model_config = {"env_file": ".env", "extra": "ignore"}

def load_config(config_path: str = "config/app_config.yaml") -> dict:
    path = Path(config_path)
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return {}

settings = Settings()
