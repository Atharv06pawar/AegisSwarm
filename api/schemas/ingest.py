from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class IngestRequest(BaseModel):
    """
    Request model for POST /api/v1/ingest.
    """
    model_config = ConfigDict(frozen=True)

    datasets: List[str] = Field(..., min_length=1, description="List of dataset IDs to ingest (e.g. ['hackaprompt', 'garak']).")
    dry_run: bool = Field(default=False, description="Dry run mode without writing to Data Lake storage.")
    batch_size: Optional[int] = Field(default=1000, ge=100, le=50000, description="Streaming batch write size.")


class IngestResponse(BaseModel):
    """
    Response model returned immediately upon background job submission.
    """
    model_config = ConfigDict(frozen=True)

    job_id: str = Field(..., description="Unique background ingestion job identifier.")
    status: str = Field(default="queued", description="Initial job status ('queued').")
    requested_datasets: List[str] = Field(..., description="List of dataset IDs submitted for ingestion.")
    message: str = Field(default="Ingestion job submitted successfully.", description="Status message.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp.")


class JobStatusResponse(BaseModel):
    """
    Detailed job status response for GET /api/v1/jobs/{job_id}.
    """
    model_config = ConfigDict(frozen=True)

    job_id: str = Field(..., description="Unique job identifier.")
    status: str = Field(..., description="Current status ('queued', 'running', 'completed', 'failed').")
    current_stage: str = Field(default="queued", description="Current pipeline execution stage.")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Estimated completion percentage.")
    records_processed: int = Field(default=0, ge=0, description="Total records parsed & normalized.")
    batches_written: int = Field(default=0, ge=0, description="Total storage batches persisted.")
    elapsed_seconds: float = Field(default=0.0, ge=0.0, description="Total elapsed execution time in seconds.")
    estimated_remaining_seconds: Optional[float] = Field(default=None, description="Estimated remaining execution time in seconds.")
    current_dataset: Optional[str] = Field(default=None, description="Active dataset ID currently processing.")
    errors: List[str] = Field(default_factory=list, description="List of execution error messages encountered.")
    created_at: datetime = Field(..., description="UTC creation timestamp.")
    completed_at: Optional[datetime] = Field(default=None, description="UTC completion timestamp.")


class JobListResponse(BaseModel):
    """
    Response model for GET /api/v1/jobs listing all active and historical jobs.
    """
    model_config = ConfigDict(frozen=True)

    total_jobs: int = Field(..., ge=0, description="Total background jobs tracked.")
    jobs: List[JobStatusResponse] = Field(default_factory=list, description="List of job status objects.")
