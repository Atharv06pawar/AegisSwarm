from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from corpus.models import DatasetInfo, CorpusSummary

class DashboardResponse(BaseModel):
    """
    Response schema for GET /api/v1/dashboard.
    """
    model_config = ConfigDict(frozen=True)

    total_records: int = Field(default=0, ge=0, description="Total AttackRecord count in corpus.")
    total_datasets: int = Field(default=0, ge=0, description="Total unique datasets registered.")
    total_partitions: int = Field(default=0, ge=0, description="Total physical data lake partitions.")
    total_size_bytes: int = Field(default=0, ge=0, description="Total storage footprint in bytes.")
    ontology_coverage: float = Field(default=0.0, ge=0.0, le=100.0, description="AUAO taxonomy node coverage %.")
    verification_status: str = Field(default="VERIFIED", description="Data lake integrity status.")
    verification_percentage: float = Field(default=100.0, ge=0.0, le=100.0, description="Verified partition percentage.")
    active_plugins: List[str] = Field(default_factory=list, description="List of active plugin source IDs.")
    root_class_distribution: Dict[str, int] = Field(default_factory=dict, description="AUAO Root Class record counts.")
    taxonomy_distribution: Dict[str, int] = Field(default_factory=dict, description="Detailed taxonomy node counts.")
    target_models: List[str] = Field(default_factory=list, description="Target AI models present in corpus.")


class SearchQuery(BaseModel):
    """
    Request model for POST /api/v1/search.
    """
    model_config = ConfigDict(frozen=True)

    query: Optional[str] = Field(default=None, description="Free text keyword search prompt.")
    taxonomy_node: Optional[str] = Field(default=None, description="Filter by exact AUAO taxonomy node.")
    dataset: Optional[str] = Field(default=None, description="Filter by dataset ID.")
    target_model: Optional[str] = Field(default=None, description="Filter by target AI model.")
    attack_success: Optional[bool] = Field(default=None, description="Filter by attack evaluation result.")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum search results to return.")
    offset: int = Field(default=0, ge=0, description="Result offset.")


class SearchResultItem(BaseModel):
    """
    Single record search result match.
    """
    model_config = ConfigDict(frozen=True)

    sample_id: str = Field(..., description="Unique AttackRecord UUID string.")
    dataset: str = Field(..., description="Dataset source ID.")
    taxonomy_node: str = Field(..., description="AUAO taxonomy node ID.")
    difficulty_level: str = Field(default="medium", description="Attack difficulty level.")
    prompt_sample: str = Field(..., description="Prompt payload preview text.")
    target_model: Optional[str] = Field(default=None, description="Target AI model.")
    attack_success: Optional[bool] = Field(default=None, description="Attack evaluation outcome.")


class SearchResultResponse(BaseModel):
    """
    Response schema for POST /api/v1/search.
    """
    model_config = ConfigDict(frozen=True)

    total_matches: int = Field(..., ge=0, description="Total matching records found.")
    execution_time_ms: float = Field(..., ge=0.0, description="Query execution time in ms.")
    results: List[SearchResultItem] = Field(default_factory=list, description="Page of matching AttackRecord items.")


class ReportMetadataItem(BaseModel):
    """
    Metadata describing a generated publication report file.
    """
    model_config = ConfigDict(frozen=True)

    filename: str = Field(..., description="Report filename (e.g. 'corpus_report.md').")
    format: str = Field(..., description="Format specification ('markdown' or 'json').")
    file_path: str = Field(..., description="Relative or absolute file path.")
    size_bytes: int = Field(..., ge=0, description="File size in bytes.")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp.")


class ReportsListResponse(BaseModel):
    """
    Response schema for GET /api/v1/reports.
    """
    model_config = ConfigDict(frozen=True)

    total_reports: int = Field(..., ge=0, description="Total generated report files.")
    reports: List[ReportMetadataItem] = Field(default_factory=list, description="Array of report metadata items.")


class ReportGenerateResponse(BaseModel):
    """
    Response schema for POST /api/v1/reports/generate.
    """
    model_config = ConfigDict(frozen=True)

    markdown_path: str = Field(..., description="Generated Markdown whitepaper file path.")
    json_path: str = Field(..., description="Generated JSON metadata report file path.")
    message: str = Field(default="Corpus publication reports generated successfully.", description="Status message.")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp.")
