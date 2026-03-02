"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # GCP Configuration
    gcp_project_id: Optional[str] = None
    gcp_location: str = "us-central1"
    vertex_ai_model: str = "gemini-1.5-flash"

    # Feature Flags
    enable_ai_validation: bool = False
    enable_text_optimization: bool = False

    # API Configuration
    api_title: str = "PenLife Risk Profiler API"
    api_version: str = "1.0.0"
    api_description: str = "API for processing risk profiling PDFs"

    # Logging
    log_level: str = "INFO"

    # Application
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
