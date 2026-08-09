"""
Pydantic data models for Research Integrity, Reproducibility & Publication Validation (Sprint 16.3).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DatasetBenchmarkMetric(BaseModel):
    """Metrics for an individual dataset benchmark."""
    dataset_id: str
    records: int = 0
    executed: int = 0
    success_count: int = 0
    failed_count: int = 0
    success_rate: float = 0.0
    average_score: float = 0.0
    average_latency_ms: float = 0.0
    provider: str = "openai"


class ProviderBenchmarkMetric(BaseModel):
    """Metrics for an individual target provider benchmark."""
    provider_id: str
    attacks: int = 0
    successful_attacks: int = 0
    failed_attacks: int = 0
    success_rate: float = 0.0
    refusal_rate: float = 0.0
    average_latency_ms: float = 0.0
    cost_usd: float = 0.0
    evaluation_score: float = 0.0
    rank: int = 1


class StrategyBenchmarkMetric(BaseModel):
    """Metrics for an attack strategy mutation family benchmark."""
    strategy_family: str
    attacks: int = 0
    success_count: int = 0
    success_rate: float = 0.0
    average_confidence: float = 0.0
    average_score: float = 0.0
    average_latency_ms: float = 0.0
    rank: int = 1


class SwarmAgentBenchmarkMetric(BaseModel):
    """Metrics for an autonomous swarm attacker agent benchmark."""
    agent_name: str
    attacks: int = 0
    success_count: int = 0
    failures: int = 0
    success_rate: float = 0.0
    average_score: float = 0.0
    average_cost_usd: float = 0.0
    average_latency_ms: float = 0.0
    rank: int = 1


class LearningBenchmarkMetric(BaseModel):
    """Metrics for the Adaptive Autonomous Learning engine benchmark."""
    memory_growth: int = 0
    strategy_updates: int = 0
    graph_growth: int = 0
    optimizer_changes: int = 0
    new_strategies_discovered: int = 0
    q_score_change: float = 0.0


class TelemetryBenchmarkMetric(BaseModel):
    """Metrics for the Telemetry & Observability platform benchmark."""
    events_emitted: int = 0
    spans_created: int = 0
    logs_written: int = 0
    api_requests: int = 0
    throughput_rps: float = 0.0
    peak_queue: int = 0
    worker_utilization: float = 0.0


class BenchmarkRequest(BaseModel):
    """Request configuration payload to initiate a research benchmark run."""
    objective: str = "AegisSwarm Production Research Benchmark Harness Validation Run"
    max_attacks_per_dataset: int = Field(default=5, ge=1, le=500)
    datasets: Optional[List[str]] = None
    providers: Optional[List[str]] = None
    parallelism: int = Field(default=4, ge=1, le=32)
    enable_learning: bool = True
    enable_telemetry: bool = True
    random_seed: int = 42


class ProvenanceRecord(BaseModel):
    """Complete provenance record for scientific benchmark execution."""
    benchmark_uuid: str
    mission_uuids: List[str] = Field(default_factory=list)
    dataset_versions: Dict[str, str] = Field(default_factory=dict)
    dataset_checksums: Dict[str, str] = Field(default_factory=dict)
    dataset_record_counts: Dict[str, int] = Field(default_factory=dict)
    provider: str = "openai"
    model: str = "gpt-4o"
    mutation_families: List[str] = Field(default_factory=list)
    swarm_agents: List[str] = Field(default_factory=list)
    orchestrator_version: str = "2.0.0"
    git_commit_hash: str = "unknown"
    python_version: str = ""
    os_info: str = ""
    dependency_versions: Dict[str, str] = Field(default_factory=dict)
    execution_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    random_seed: int = 42
    configuration_snapshot: Dict[str, Any] = Field(default_factory=dict)


class ReproducibilityManifest(BaseModel):
    """Deterministic reproducibility manifest for scientific benchmark audits."""
    manifest_id: str
    benchmark_configuration: Dict[str, Any] = Field(default_factory=dict)
    runtime_environment: Dict[str, str] = Field(default_factory=dict)
    datasets: List[Dict[str, Any]] = Field(default_factory=list)
    providers: List[str] = Field(default_factory=list)
    random_seeds: List[int] = Field(default_factory=list)
    dataset_hashes: Dict[str, str] = Field(default_factory=dict)
    report_hashes: Dict[str, str] = Field(default_factory=dict)
    artifact_hashes: Dict[str, str] = Field(default_factory=dict)


class DatasetValidationMetric(BaseModel):
    """Integrity and compliance metric for individual dataset."""
    dataset_id: str
    checksum_sha256: str
    duplicate_count: int = 0
    malformed_records: int = 0
    schema_valid: bool = True
    ontology_compliant: bool = True
    attack_records_valid: bool = True


class DatasetValidationReport(BaseModel):
    """Comprehensive dataset integrity validation report."""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_datasets: int = 7
    all_valid: bool = True
    datasets: List[DatasetValidationMetric] = Field(default_factory=list)


class StatisticalSummary(BaseModel):
    """Statistical distribution metrics computed over benchmark measurements."""
    mean: float = 0.0
    median: float = 0.0
    std_dev: float = 0.0
    variance: float = 0.0
    p50: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    ci_95_lower: float = 0.0
    ci_95_upper: float = 0.0


class BenchmarkStatistics(BaseModel):
    """Statistical validation distributions across core operational metrics."""
    latency_ms: StatisticalSummary = Field(default_factory=StatisticalSummary)
    score: StatisticalSummary = Field(default_factory=StatisticalSummary)
    confidence: StatisticalSummary = Field(default_factory=StatisticalSummary)
    cost_usd: StatisticalSummary = Field(default_factory=StatisticalSummary)


class RepeatabilityReport(BaseModel):
    """Repeatability assessment across N benchmark execution runs."""
    total_runs: int = 1
    score_variance: float = 0.0
    latency_variance: float = 0.0
    ranking_stability: float = 1.0
    provider_stability: float = 1.0
    strategy_stability: float = 1.0
    is_repeatable: bool = True


class PublicationChecklist(BaseModel):
    """Quality gate and verification checklist for research publication readiness."""
    datasets_available: bool = True
    reports_generated: bool = True
    tests_passing: bool = True
    coverage_threshold_met: bool = True
    benchmark_completed: bool = True
    provenance_generated: bool = True
    reproducibility_generated: bool = True
    integrity_verified: bool = True
    publication_ready: bool = True
    reasons: List[str] = Field(default_factory=list)


class BenchmarkReport(BaseModel):
    """Comprehensive aggregate report model for research benchmark harness run."""
    benchmark_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "COMPLETED"
    overall_health: str = "PASS"  # PASS, DEGRADED, FAIL
    total_execution_time_sec: float = 0.0
    attacks_executed: int = 0
    successful_attacks: int = 0
    failed_attacks: int = 0
    refusal_rate: float = 0.0
    leakage_detections: int = 0
    jailbreak_detections: int = 0
    average_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    provider_utilization: Dict[str, int] = Field(default_factory=dict)
    evaluation_score: float = 0.0
    retries: int = 0
    estimated_cost_usd: float = 0.0
    average_confidence: float = 0.0
    campaign_duration_sec: float = 0.0
    datasets: List[DatasetBenchmarkMetric] = Field(default_factory=list)
    providers: List[ProviderBenchmarkMetric] = Field(default_factory=list)
    strategies: List[StrategyBenchmarkMetric] = Field(default_factory=list)
    swarm_agents: List[SwarmAgentBenchmarkMetric] = Field(default_factory=list)
    learning: LearningBenchmarkMetric = Field(default_factory=LearningBenchmarkMetric)
    telemetry: TelemetryBenchmarkMetric = Field(default_factory=TelemetryBenchmarkMetric)
    provenance: Optional[ProvenanceRecord] = None
    manifest: Optional[ReproducibilityManifest] = None
    statistics: Optional[BenchmarkStatistics] = None
    dataset_validation: Optional[DatasetValidationReport] = None
    repeatability: Optional[RepeatabilityReport] = None
    checklist: Optional[PublicationChecklist] = None
    artifact_hashes: Dict[str, str] = Field(default_factory=dict)
