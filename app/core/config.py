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

    # Authentication Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)

    # Argon Parameters
    ARGON2_TIME_COST: int = os.getenv("ARGON2_TIME_COST", 2)
    ARGON2_MEMORY_COST: int = os.getenv("ARGON2_MEMORY_COST", 102400)
    ARGON2_PARALLELISM: int = os.getenv("ARGON2_PARALLELISM", 8)
    ARGON2_HASH_LEN: int = os.getenv("ARGON2_HASH_LEN", 32)
    ARGON2_SALT_LEN: int = os.getenv("ARGON2_SALT_LEN", 16)