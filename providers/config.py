"""
Configuration settings for the AegisSwarm Provider Abstraction Layer.
Loads API keys, hosts, timeouts, and retry policies from environment variables.
"""

from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSettings(BaseSettings):
    """
    Settings for language model provider adapters.
    Reads environment variables OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY,
    OPENROUTER_API_KEY, and OLLAMA_HOST safely without hardcoding secrets.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    openai_api_key: Optional[SecretStr] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[SecretStr] = Field(default=None, alias="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[SecretStr] = Field(default=None, alias="GEMINI_API_KEY")
    openrouter_api_key: Optional[SecretStr] = Field(default=None, alias="OPENROUTER_API_KEY")
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    
    default_timeout: float = Field(default=30.0, ge=1.0, description="Default API timeout in seconds.")
    max_retries: int = Field(default=3, ge=0, description="Default max retry attempts.")
    backoff_factor: float = Field(default=1.5, ge=1.0, description="Exponential backoff factor.")


def get_provider_settings() -> ProviderSettings:
    """
    Returns singleton settings instance.
    """
    return ProviderSettings()
