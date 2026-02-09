"""
Application configuration management.

This module provides configuration loading with environment variable
support using Pydantic settings management.
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables:
        APP_NAME: Application name (default: "Local Task Manager")
        APP_VERSION: Application version (default: "1.0.0")
        APP_DESCRIPTION: Application description (default: "A local task management system")
        HOST: Server host (default: "0.0.0.0")
        PORT: Server port (default: 8000)
        DEBUG: Enable debug mode (default: False)
        ALLOWED_ORIGINS: Comma-separated list of allowed CORS origins (default: "*")
        STORAGE_DIR: Directory for data storage (default: "./data")
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application settings
    APP_NAME: str = Field(default="Local Task Manager")
    APP_VERSION: str = Field(default="1.0.0")
    APP_DESCRIPTION: str = Field(default="A local task management system")

    # Server settings
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=False)

    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])

    # Storage settings
    STORAGE_DIR: str = Field(default="./data")

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.DEBUG

    @property
    def docs_url(self) -> Optional[str]:
        """Get the docs URL based on debug mode."""
        return "/docs" if self.DEBUG else None

    @property
    def openapi_url(self) -> Optional[str]:
        """Get the OpenAPI URL based on debug mode."""
        return "/openapi.json" if self.DEBUG else None


# Global settings instance
settings = Settings()
