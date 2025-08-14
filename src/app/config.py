"""
Configuration module for PDF Summary AI application.
"""

from pathlib import Path
from pydantic.v1 import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    openai_api_key: str

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False

    max_file_size: int = 52428800  # 50MB
    max_pages: int = 100
    upload_dir: str = "./uploads"
    data_dir: str = "./data"

    log_level: str = "INFO"

    allowed_extensions: set = {".pdf"}

    attempt = 0
    max_retries = 3
    delay = 2.0
    timeout = 300.0
    temperature = 0.2

    @classmethod
    @validator("openai_api_key")
    def validata_openai_api_key(cls, key: str) -> str:
        """Validates OpenAI API key is provided."""
        if not key:
            raise ValueError("OpenAI API key must be provided")
        return key

    @classmethod
    @validator("upload_dir", "data_dir")
    def create_directories(cls, dir_name: str) -> str:
        """Ensure directories exist."""
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        return dir_name

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()


def get_settings() -> Settings:
    """Gets application settings."""
    return settings
