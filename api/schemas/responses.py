from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class HealthResponse(BaseModel):
    """
    Response model for the GET /health endpoint.
    """
    model_config = ConfigDict(frozen=True)

    status: str = Field(default="healthy", description="System health status indicator.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Current UTC timestamp.")
    version: str = Field(..., description="Application version.")


class VersionResponse(BaseModel):
    """
    Response model for the GET /version endpoint.
    """
    model_config = ConfigDict(frozen=True)

    name: str = Field(default="AegisSwarm AI Security Engine", description="System application name.")
    version: str = Field(..., description="Core platform semantic version.")
    ontology_version: str = Field(default="1.0.0", description="AUAO ontology specification version.")
    environment: str = Field(default="production", description="Active execution environment.")


class PluginMetadataResponse(BaseModel):
    """
    Response model representing metadata for an AegisSwarm dataset plugin.
    """
    model_config = ConfigDict(frozen=True)

    dataset_id: str = Field(..., description="Unique dataset identifier (e.g. 'hackaprompt').")
    description: str = Field(..., description="Plugin and dataset description.")
    license_name: str = Field(..., description="License classification (e.g. 'MIT', 'Apache-2.0').")
    license_url: Optional[str] = Field(None, description="URL pointing to license text.")
    parser_version: str = Field(default="1.0.0", description="Plugin parser code version.")


class PluginListResponse(BaseModel):
    """
    Response model for the GET /plugins endpoint.
    """
    model_config = ConfigDict(frozen=True)

    total_count: int = Field(..., ge=0, description="Total number of discovered dataset plugins.")
    plugins: List[PluginMetadataResponse] = Field(default_factory=list, description="List of plugin metadata entries.")


class ErrorResponse(BaseModel):
    """
    Structured response model for custom API exception handling.
    """
    model_config = ConfigDict(frozen=True)

    detail: str = Field(..., description="Detailed human-readable error description.")
    code: str = Field(..., description="Machine-readable application error code.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of error occurrence.")
    path: Optional[str] = Field(None, description="Request URL path where error occurred.")
