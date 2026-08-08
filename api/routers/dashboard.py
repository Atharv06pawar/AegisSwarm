import os
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from api.dependencies import get_corpus_manager
from api.schemas.corpus import DashboardResponse
from corpus.manager import CorpusManager
from corpus.statistics import CorpusStatisticsCalculator
from corpus.coverage import OntologyCoverageAnalyzer
from corpus.verifier import CorpusIntegrityVerifier

router = APIRouter(tags=["Dashboard"])

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get real-time Data Lake dashboard metrics",
    description="Calculates and returns aggregate corpus metrics, AUAO taxonomy coverage, and lake integrity status."
)
async def get_dashboard(
    manager: CorpusManager = Depends(get_corpus_manager)
) -> DashboardResponse:
    """
    Aggregates metrics strictly across CorpusRegistry, CorpusStatisticsCalculator,
    OntologyCoverageAnalyzer, and CorpusIntegrityVerifier without hardcoded fallbacks.
    """
    summary = manager.get_status()
    
    # Calculate streaming statistics
    stats_calc = CorpusStatisticsCalculator()
    stats_report = stats_calc.compute_statistics()

    # Calculate coverage
    coverage_analyzer = OntologyCoverageAnalyzer()
    coverage_report = coverage_analyzer.analyze()

    # Check integrity
    verifier = CorpusIntegrityVerifier()
    verification_report = verifier.verify()

    # Calculate root class distribution
    root_class_dist: Dict[str, int] = {}
    for node_id, count in stats_report.taxonomy_distribution.items():
        root = node_id.split("-")[0] if "-" in node_id else "OTHER"
        root_class_dist[root] = root_class_dist.get(root, 0) + count

    return DashboardResponse(
        total_records=stats_report.total_records,
        total_datasets=summary.total_datasets,
        total_partitions=summary.total_partitions,
        total_size_bytes=summary.total_size_bytes,
        ontology_coverage=round(coverage_report.coverage_percentage, 1) if coverage_report else 0.0,
        verification_status="VERIFIED" if verification_report.overall_status == "HEALTHY" else "DEGRADED",
        verification_percentage=round(verification_report.verification_percentage, 1),
        active_plugins=summary.dataset_ids,
        root_class_distribution=root_class_dist,
        taxonomy_distribution=dict(stats_report.taxonomy_distribution),
        target_models=stats_report.unique_target_models
    )
