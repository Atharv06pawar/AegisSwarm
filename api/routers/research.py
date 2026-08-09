"""
FastAPI Router for Production Research Validation, Provenance, Reproducibility & Benchmark Harness endpoints (Sprint 16.3).
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException

from research.models import (
    BenchmarkRequest,
    BenchmarkReport,
    DatasetBenchmarkMetric,
    ProviderBenchmarkMetric,
    StrategyBenchmarkMetric,
    SwarmAgentBenchmarkMetric,
    LearningBenchmarkMetric,
    TelemetryBenchmarkMetric,
    ProvenanceRecord,
    ReproducibilityManifest,
    BenchmarkStatistics,
    DatasetValidationReport,
    RepeatabilityReport,
    PublicationChecklist,
)
from research.harness import ResearchBenchmarkHarness
from api.dependencies import get_research_harness

research_router = APIRouter(prefix="/research", tags=["Research Benchmark Harness & Scientific Validation"])


@research_router.get("", response_model=BenchmarkReport)
def get_research_status(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves aggregate status and latest benchmark report."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        return harness.run_benchmark()
    return latest


@research_router.post("/run", response_model=BenchmarkReport)
def run_research_benchmark(
    request: Optional[BenchmarkRequest] = None,
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Executes full end-to-end research benchmark harness run."""
    return harness.run_benchmark(request or BenchmarkRequest())


@research_router.get("/provenance", response_model=ProvenanceRecord)
def get_research_provenance(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves scientific provenance record for the latest benchmark execution."""
    latest = harness.persistence.get_latest_report()
    if not latest or not latest.provenance:
        latest = harness.run_benchmark()
    if not latest.provenance:
        raise HTTPException(status_code=404, detail="Provenance record not found")
    return latest.provenance


@research_router.get("/reproducibility", response_model=ReproducibilityManifest)
def get_research_reproducibility(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves deterministic reproducibility manifest."""
    latest = harness.persistence.get_latest_report()
    if not latest or not latest.manifest:
        latest = harness.run_benchmark()
    if not latest.manifest:
        raise HTTPException(status_code=404, detail="Reproducibility manifest not found")
    return latest.manifest


@research_router.get("/integrity", response_model=DatasetValidationReport)
def get_research_integrity(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves dataset and benchmark integrity quality gate validation results."""
    latest = harness.persistence.get_latest_report()
    if not latest or not latest.dataset_validation:
        latest = harness.run_benchmark()
    if not latest.dataset_validation:
        raise HTTPException(status_code=404, detail="Integrity validation report not found")
    return latest.dataset_validation


@research_router.get("/statistics", response_model=BenchmarkStatistics)
def get_research_statistics(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves statistical validation distributions across core operational metrics."""
    latest = harness.persistence.get_latest_report()
    if not latest or not latest.statistics:
        latest = harness.run_benchmark()
    if not latest.statistics:
        raise HTTPException(status_code=404, detail="Statistical distribution report not found")
    return latest.statistics


@research_router.get("/repeatability", response_model=RepeatabilityReport)
def get_research_repeatability(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves repeatability assessment and variance metrics across benchmark runs."""
    latest = harness.persistence.get_latest_report()
    if not latest or not latest.repeatability:
        latest = harness.run_benchmark()
    if not latest.repeatability:
        raise HTTPException(status_code=404, detail="Repeatability report not found")
    return latest.repeatability


@research_router.get("/artifacts")
def get_research_artifacts(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves SHA256 artifact hash signatures for all generated outputs."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        latest = harness.run_benchmark()
    return {
        "benchmark_id": latest.benchmark_id,
        "artifact_count": len(latest.artifact_hashes),
        "artifact_hashes": latest.artifact_hashes
    }


@research_router.get("/checklist", response_model=PublicationChecklist)
def get_publication_checklist(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves 8-gate scientific publication readiness checklist."""
    latest = harness.persistence.get_latest_report()
    if not latest or not latest.checklist:
        latest = harness.run_benchmark()
    if not latest.checklist:
        raise HTTPException(status_code=404, detail="Publication checklist not found")
    return latest.checklist


@research_router.get("/datasets", response_model=List[DatasetBenchmarkMetric])
def get_research_datasets(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves research dataset benchmark leaderboard metrics."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        latest = harness.run_benchmark()
    return latest.datasets


@research_router.get("/providers", response_model=List[ProviderBenchmarkMetric])
def get_research_providers(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves target LLM provider benchmark rankings."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        latest = harness.run_benchmark()
    return latest.providers


@research_router.get("/strategies", response_model=List[StrategyBenchmarkMetric])
def get_research_strategies(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves mutation strategy family benchmark rankings."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        latest = harness.run_benchmark()
    return latest.strategies


@research_router.get("/swarm", response_model=List[SwarmAgentBenchmarkMetric])
def get_research_swarm(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves autonomous swarm agent benchmark rankings."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        latest = harness.run_benchmark()
    return latest.swarm_agents


@research_router.get("/learning", response_model=LearningBenchmarkMetric)
def get_research_learning(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves autonomous learning engine benchmark metrics."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        latest = harness.run_benchmark()
    return latest.learning


@research_router.get("/telemetry", response_model=TelemetryBenchmarkMetric)
def get_research_telemetry(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves telemetry platform throughput and observability metrics."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        latest = harness.run_benchmark()
    return latest.telemetry


@research_router.get("/reports")
def get_research_reports(
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """Retrieves directory listing and contents of generated research report artifacts."""
    latest = harness.persistence.get_latest_report()
    if not latest:
        latest = harness.run_benchmark()

    output_dir = "outputs/reports"
    files = {}
    if os.path.exists(output_dir):
        for fname in os.listdir(output_dir):
            fpath = os.path.join(output_dir, fname)
            if os.path.isfile(fpath):
                files[fname] = fpath

    return {
        "status": "success",
        "benchmark_id": latest.benchmark_id,
        "reports_count": len(files),
        "reports": files
    }
