from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class DatasetPartitionInfo(BaseModel):
    """
    Metadata representation for a single data lake partition file.
    Does not hold dataset record payloads in memory.
    """
    model_config = ConfigDict(frozen=True)

    partition_path: str = Field(..., description="Absolute or relative path to the partition file.")
    source_id: str = Field(..., description="The dataset source identifier (e.g. 'hackaprompt').")
    format: str = Field(..., description="File format ('jsonl', 'jsonl.gz', or 'parquet').")
    size_bytes: int = Field(..., ge=0, description="Size of the partition file in bytes.")
    record_count: int = Field(default=0, ge=0, description="Estimated or verified record count.")
    compression: Optional[str] = Field(default=None, description="Compression algorithm used ('gzip', 'snappy', None).")
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last modification timestamp.")

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        valid_formats = {"jsonl", "jsonl.gz", "parquet", "json"}
        if v.lower() not in valid_formats:
            raise ValueError(f"Invalid format '{v}'. Allowed formats: {valid_formats}")
        return v.lower()


class DatasetInfo(BaseModel):
    """
    Aggregated summary information for an installed dataset within the corpus.
    """
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(..., description="Unique dataset source identifier.")
    partition_count: int = Field(..., ge=0, description="Total number of physical partition files.")
    total_size_bytes: int = Field(..., ge=0, description="Total size across all partition files in bytes.")
    formats: List[str] = Field(default_factory=list, description="Unique formats present for this dataset.")
    partitions: List[DatasetPartitionInfo] = Field(default_factory=list, description="List of physical partitions.")


class CorpusSummary(BaseModel):
    """
    High-level aggregate status of the entire AegisSwarm Corpus.
    """
    model_config = ConfigDict(frozen=True)

    total_datasets: int = Field(..., ge=0, description="Total number of unique datasets registered.")
    total_partitions: int = Field(..., ge=0, description="Total physical partition files across all datasets.")
    total_size_bytes: int = Field(..., ge=0, description="Total storage footprint of the corpus in bytes.")
    dataset_ids: List[str] = Field(default_factory=list, description="List of all registered dataset IDs.")


class CorpusManifest(BaseModel):
    """
    Reproducible snapshot manifest of the entire AegisSwarm Corpus state.
    """
    model_config = ConfigDict(frozen=True)

    manifest_version: str = Field(default="1.0.0", description="Semantic version of the manifest format.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of snapshot creation.")
    summary: CorpusSummary = Field(..., description="Global corpus aggregate summary.")
    datasets: List[DatasetInfo] = Field(default_factory=list, description="Detailed dataset inventory entries.")
