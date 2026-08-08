from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from api.dependencies import get_corpus_manager
from corpus.manager import CorpusManager
from corpus.models import CorpusSummary, DatasetInfo
from corpus.statistics import CorpusStatisticsCalculator, CorpusStatisticsReport
from corpus.coverage import OntologyCoverageAnalyzer, OntologyCoverageReport
from corpus.quality import CorpusQualityAuditor, QualityAuditReport
from corpus.verifier import CorpusIntegrityVerifier, VerificationReport

router = APIRouter(prefix="/corpus", tags=["Corpus Subsystem"])

@router.get(
    "",
    response_model=CorpusSummary,
    summary="Get Data Lake corpus summary",
    description="Returns high-level metadata summary of installed dataset partitions across outputs/lake/."
)
async def get_corpus_summary(
    manager: CorpusManager = Depends(get_corpus_manager)
) -> CorpusSummary:
    return manager.get_status()


@router.get(
    "/datasets",
    response_model=List[DatasetInfo],
    summary="List installed datasets in corpus",
    description="Returns detailed partition info for each discovered dataset in outputs/lake/."
)
async def list_corpus_datasets(
    manager: CorpusManager = Depends(get_corpus_manager)
) -> List[DatasetInfo]:
    return manager.list_datasets()


@router.get(
    "/statistics",
    response_model=CorpusStatisticsReport,
    summary="Compute streaming corpus statistics",
    description="Calculates record counts, turn averages, character lengths, and taxonomy distributions."
)
async def get_corpus_statistics() -> CorpusStatisticsReport:
    calc = CorpusStatisticsCalculator()
    return calc.compute_statistics()


@router.get(
    "/coverage",
    response_model=OntologyCoverageReport,
    summary="Analyze AUAO ontology coverage",
    description="Evaluates representation of AUAO v1.0 taxonomy nodes and root classes across data lake partitions."
)
async def get_corpus_coverage() -> OntologyCoverageReport:
    analyzer = OntologyCoverageAnalyzer()
    return analyzer.analyze()


@router.get(
    "/quality",
    response_model=QualityAuditReport,
    summary="Audit corpus data quality",
    description="Audits schema compliance, duplicate sample IDs, prompt semantic deduplication, and confidence scores."
)
async def get_corpus_quality() -> QualityAuditReport:
    auditor = CorpusQualityAuditor()
    return auditor.audit()


@router.get(
    "/verification",
    response_model=VerificationReport,
    summary="Verify Data Lake cryptographic integrity",
    description="Performs SHA256 checksum verification across all Hive partition files against lineage manifests."
)
async def get_corpus_verification() -> VerificationReport:
    verifier = CorpusIntegrityVerifier()
    return verifier.verify()
