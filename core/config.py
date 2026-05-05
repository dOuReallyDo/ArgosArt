"""ArgosArt Core Configuration.

Extended settings for art/creative domain features.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings with env-var binding."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Environment ──────────────────────────────────────
    env: Literal["development", "production", "test"] = "development"

    # ── Project identity ─────────────────────────────────
    project_name: str = "ArgosArt"
    project_version: str = "0.1.0"

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    # ── Database ─────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./data/argosart.db"

    # ── Vector Database (Qdrant) ─────────────────────────
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "argosart_portfolio"

    # ── Redis ────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Object Storage ───────────────────────────────────
    storage_backend: Literal["local", "s3", "minio"] = "local"
    storage_path: str = "./data/portfolio"

    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "argosart-portfolio"
    s3_region: str = "us-east-1"

    # ── Encryption ───────────────────────────────────────
    encryption_enabled: bool = True
    encryption_key: str = ""

    # ── Auth / JWT ───────────────────────────────────────
    jwt_secret_key: str = "change-me-in-production-64-chars-min"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # ── Embedding Models ─────────────────────────────────
    text_embedding_model: str = "intfloat/multilingual-e5-large"
    image_embedding_model: str = "openai/clip-vit-large-patch14"
    embedding_device: Literal["cpu", "cuda", "mps"] = "cpu"

    # ── Art-specific features ────────────────────────────
    color_analysis_enabled: bool = True
    style_tagging_enabled: bool = True
    max_image_resolution: int = 4096  # Max side for art images
    supported_art_styles: list[str] = [
        "contemporary", "modern", "abstract", "figurative",
        "digital", "photography", "sculpture", "installation",
        "performance", "mixed_media", "illustration", "graphic_design",
    ]

    # ── GLM-OCR ──────────────────────────────────────────
    glm_ocr_enabled: bool = False
    glm_ocr_model_path: str = "./models/glm-ocr"

    # ── Whisper ──────────────────────────────────────────
    whisper_model: str = "base"
    whisper_device: Literal["cpu", "cuda", "mps"] = "cpu"

    # ── Limits ───────────────────────────────────────────
    max_upload_size_mb: int = 500
    max_video_duration_seconds: int = 1800
    max_audio_duration_seconds: int = 3600
    max_pdf_pages: int = 500

    # ── API ──────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # ── UI ───────────────────────────────────────────────
    frontend_url: str = "http://localhost:5173"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:8000",
    ]


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings singleton."""
    return Settings()
