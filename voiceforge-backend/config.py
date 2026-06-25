"""VoiceForge configuration from environment variables."""

import os
# Disable Objective-C fork safety checks on macOS to prevent crashes in multi-threaded child forks (e.g. PyTorch/MPS + Celery)
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

import secrets
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    SECRET_KEY: str = secrets.token_hex(32)

    # Database
    DATABASE_URL: str = "sqlite:///./voiceforge.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery
    CELERY_WORKERS: int = 4
    MAX_CONCURRENT_DOWNLOADS: int = 3

    # Storage
    BASE_DIR: Path = Path(__file__).parent
    OUTPUT_DIR: Path = BASE_DIR / "static" / "outputs"
    TEMP_DIR: Path = BASE_DIR / "tmp"
    MAX_OUTPUT_SIZE_GB: float = 50.0
    RETENTION_DAYS: int = 7

    # HuggingFace
    HF_TOKEN: str = ""

    # ML Models
    DEMUCS_MODEL: str = "htdemucs_ft"
    WHISPER_MODEL: str = "large-v3"
    PYANNOTE_MODEL: str = "pyannote/speaker-diarization-3.1"
    USE_GPU: str = "auto"  # auto | cuda | cpu | mps

    # Processing Defaults
    DEFAULT_SAMPLE_RATE: int = 22050
    DEFAULT_BIT_DEPTH: int = 16
    DEFAULT_MIN_CLIP_S: float = 1.5
    DEFAULT_MAX_CLIP_S: float = 25.0
    DEFAULT_MIN_SNR_DB: float = 15.0
    DEFAULT_QUALITY_THRESHOLD: int = 60

    # Rate Limiting
    ANIDB_DELAY_S: float = 2.5
    YOUTUBE_MAX_RESULTS: int = 50
    BILIBILI_MAX_RESULTS: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    def ensure_dirs(self) -> None:
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
