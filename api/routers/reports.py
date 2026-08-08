import os
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from api.dependencies import get_corpus_manager
from api.schemas.corpus import ReportsListResponse, ReportMetadataItem, ReportGenerateResponse
from corpus.manager import CorpusManager
from corpus.reporter import CorpusReporter

router = APIRouter(prefix="/reports", tags=["Reports Engine"])

@router.get(
    "",
    response_model=ReportsListResponse,
    summary="Get generated report metadata list",
    description="Returns metadata for existing publication Markdown and JSON reports."
)
async def list_reports() -> ReportsListResponse:
    """
    Returns metadata strictly for existing report files on disk in outputs/.
    """
    reports: List[ReportMetadataItem] = []
    
    md_path = "outputs/corpus_report.md"
    json_path = "outputs/corpus_report.json"

    if os.path.exists(md_path):
        stat = os.stat(md_path)
        reports.append(
            ReportMetadataItem(
                filename="corpus_report.md",
                format="markdown",
                file_path=md_path,
                size_bytes=stat.st_size,
                generated_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc)
            )
        )

    if os.path.exists(json_path):
        stat = os.stat(json_path)
        reports.append(
            ReportMetadataItem(
                filename="corpus_report.json",
                format="json",
                file_path=json_path,
                size_bytes=stat.st_size,
                generated_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc)
            )
        )

    return ReportsListResponse(
        total_reports=len(reports),
        reports=reports
    )


@router.post(
    "/generate",
    response_model=ReportGenerateResponse,
    summary="Generate publication research reports",
    description="Executes CorpusReporter to aggregate metrics and generate corpus_report.md and corpus_report.json."
)
async def generate_reports(
    manager: CorpusManager = Depends(get_corpus_manager)
) -> ReportGenerateResponse:
    """
    Triggers publication report generation via CorpusReporter.export().
    """
    reporter = CorpusReporter()
    report_files = reporter.export("outputs")

    md_path = report_files.get("markdown", "outputs/corpus_report.md")
    json_path = report_files.get("json", "outputs/corpus_report.json")

    return ReportGenerateResponse(
        markdown_path=md_path,
        json_path=json_path,
        message="Corpus publication research reports generated successfully."
    )
