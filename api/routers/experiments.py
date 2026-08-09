"""
FastAPI Router for Experiments & Benchmark Wizard (Epic 2).
Provides endpoints to configure and launch benchmark experiments via ResearchBenchmarkHarness.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException

from research.models import BenchmarkRequest, BenchmarkReport
from research.harness import ResearchBenchmarkHarness
from api.dependencies import get_research_harness

experiments_router = APIRouter(prefix="/experiments", tags=["Benchmark Wizard & Experiments"])


@experiments_router.post("/benchmark/launch", response_model=BenchmarkReport)
def launch_benchmark_wizard(
    request: Optional[BenchmarkRequest] = None,
    harness: ResearchBenchmarkHarness = Depends(get_research_harness)
):
    """
    Launches an end-to-end benchmark experiment from the Studio Benchmark Wizard.
    """
    req = request or BenchmarkRequest(
        objective="Studio Benchmark Wizard Experiment Launch",
        max_attacks_per_dataset=5,
        parallelism=4
    )
    return harness.run_benchmark(req)
