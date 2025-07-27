import os
from enum import Enum
from pydantic_settings import BaseSettings

class StorageType(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"

class Settings(BaseSettings):
    # Default storage configuration
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "local").lower()

    # Database configurations
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "be4us$")
    DB_NAME: str = os.getenv("DB_NAME", "bugtracker")

    # DATABASE URL
    DATABASE_URL: str = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"