"""Configuration management using Pydantic settings."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_RELOAD: bool = False
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Model Configuration - Whisper (ASR)
    WHISPER_MODEL: str = "large-v3"
    WHISPER_DEVICE: str = "cuda"
    WHISPER_COMPUTE_TYPE: Literal["float16", "int8", "int8_float16"] = "float16"

    # Model Configuration - Translation (NMT)
    NMT_MODEL: str = "facebook/nllb-200-distilled-600M"
    NMT_DEVICE: str = "cuda"
    NMT_MAX_LENGTH: int = 512

    # Model Configuration - TTS
    TTS_MODEL: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    TTS_DEVICE: str = "cuda"

    # Paths
    MODELS_DIR: Path = Field(default_factory=lambda: Path("./models"))
    CACHE_DIR: Path = Field(default_factory=lambda: Path("./cache"))
    DATA_DIR: Path = Field(default_factory=lambda: Path("./data"))

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "onewhat"
    POSTGRES_USER: str = "onewhat"
    POSTGRES_PASSWORD: str = "changeme"

    # Monitoring
    PROMETHEUS_PORT: int = 9090
    METRICS_ENABLED: bool = True

    # Logging
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    # Performance
    MAX_CONCURRENT_SESSIONS: int = 100
    AUDIO_CHUNK_SIZE: int = 1024
    STREAM_BUFFER_SIZE: int = 4096

    # Security
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Feature Flags
    ENABLE_GPU: bool = True
    ENABLE_STREAMING: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_METRICS: bool = True

    @property
    def redis_url(self) -> str:
        """Redis connection URL."""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def postgres_url(self) -> str:
        """PostgreSQL connection URL."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_postgres_url(self) -> str:
        """Async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def model_post_init(self, __context) -> None:
        """Create directories if they don't exist."""
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
