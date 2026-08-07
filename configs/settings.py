import os
import yaml
import json
from typing import List, Optional
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class PathSettings(BaseModel):
    """Configuration for directory paths used by the pipeline."""
    raw_dir: str = Field(default="raw", description="Directory for raw downloaded data.")
    processed_dir: str = Field(default="processed", description="Directory for processed intermediate data.")
    lake_dir: str = Field(default="outputs/lake", description="Root directory for the partitioned data lake.")
    manifest_dir: str = Field(default="metadata/manifests", description="Directory for lineage tracking manifests.")
    checkpoint_dir: str = Field(default="outputs/checkpoints", description="Directory for execution state checkpoints.")
    log_dir: str = Field(default="logs", description="Directory for application logs.")

class StorageSettings(BaseModel):
    """Configuration for the Data Lake backend and batching mechanics."""
    backend: str = Field(default="parquet", description="Storage backend to use: 'parquet' or 'jsonl'.")
    compression: str = Field(default="snappy", description="Compression algorithm (e.g., 'snappy', 'gzip').")
    batch_size: int = Field(default=10000, ge=1, description="Number of records to accumulate before writing a partition chunk.")
    checkpoint_interval: int = Field(default=50000, ge=1, description="Number of records processed before forcing a state checkpoint.")

class ExecutionSettings(BaseModel):
    """Configuration for orchestrator execution and concurrency."""
    worker_count: int = Field(default=4, ge=1, description="Number of parallel workers for multi-processing execution.")
    log_level: str = Field(default="INFO", description="Global logging level (e.g., DEBUG, INFO, WARNING).")

class PluginSettings(BaseModel):
    """Configuration for plugin discovery and execution scope."""
    package_path: str = Field(default="plugins.datasets", description="Python import path to dynamically discover dataset plugins.")
    exclude_datasets: List[str] = Field(default_factory=list, description="List of dataset_ids to skip during a run_all execution.")

class AegisSettings(BaseSettings):
    """
    Core Configuration for the AegisSwarm Pipeline.
    Supports seamless overrides via Environment Variables, .env files, and YAML.
    """
    model_config = SettingsConfigDict(
        env_prefix="AEGIS_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore"
    )

    paths: PathSettings = Field(default_factory=PathSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    execution: ExecutionSettings = Field(default_factory=ExecutionSettings)
    plugins: PluginSettings = Field(default_factory=PluginSettings)

    @classmethod
    def from_yaml(cls, yaml_path: str = "configs/settings.yaml") -> "AegisSettings":
        """
        Loads configuration from a YAML file, falling back to defaults if the file does not exist.
        
        Args:
            yaml_path: Path to the YAML configuration override file.
            
        Returns:
            AegisSettings: Validated configuration object.
        """
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            # Validates and constructs nested Pydantic models from dict
            return cls.model_validate(data)
        
        return cls()

    def export_json_schema(self, output_path: str = "configs/settings_schema.json") -> str:
        """
        Generates and saves the JSON Schema for the settings.
        Useful for providing IDE autocompletion and validation for the YAML files.
        """
        schema = self.model_json_schema()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=4)
            
        return output_path
