from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class APISettings(BaseSettings):
    """
    Application settings for the AegisSwarm FastAPI Service Layer.
    Loads configuration from environment variables or defaults.
    """
    model_config = SettingsConfigDict(
        env_prefix="AEGIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    host: str = Field(default="0.0.0.0", description="API server bind host.")
    port: int = Field(default=8000, description="API server bind port.")
    debug: bool = Field(default=False, description="Debug mode flag.")
    app_title: str = Field(default="AegisSwarm AI Security Platform API", description="OpenAPI title.")
    app_description: str = Field(default="Universal AI Attack Ontology (AUAO v1.0) & Data Lake API Engine.", description="OpenAPI description.")
    app_version: str = Field(default="2.0.0", description="Application version.")
    api_prefix: str = Field(default="/api/v1", description="API route prefix.")
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins list.")


settings = APISettings()
