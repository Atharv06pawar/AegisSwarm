from fastapi import APIRouter, Depends, BackgroundTasks, status
from api.dependencies import get_ingest_service
from api.services.ingest_service import IngestService
from api.schemas.ingest import (
    IngestRequest, IngestResponse, JobStatusResponse, JobListResponse
)
from api.exceptions import AegisSwarmAPIException

router = APIRouter(tags=["Pipeline Ingestion"])

@router.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit background ingestion job",
    description="Submits a non-blocking background task to run pipeline ingestion over specified dataset IDs."
)
async def submit_ingest_job(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    service: IngestService = Depends(get_ingest_service)
) -> IngestResponse:
    """
    Submits background ingestion job and returns HTTP 202 Accepted immediately with job ID.
    """
    return service.submit_ingest_job(request, background_tasks)


@router.get(
    "/jobs",
    response_model=JobListResponse,
    summary="List all active and completed ingestion jobs",
    description="Returns status summaries for all queued, running, completed, and failed jobs."
)
async def list_jobs(
    service: IngestService = Depends(get_ingest_service)
) -> JobListResponse:
    """
    Returns list of all active and historical ingestion jobs.
    """
    return service.list_jobs()


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get status details for a specific ingestion job",
    description="Returns detailed execution status, stage, progress percentage, records processed, and elapsed time."
)
async def get_job_status(
    job_id: str,
    service: IngestService = Depends(get_ingest_service)
) -> JobStatusResponse:
    """
    Retrieves status details for a specific job ID or raises 404 error if job not found.
    """
    job_status = service.get_job_status(job_id)
    if not job_status:
        raise AegisSwarmAPIException(
            detail=f"Ingestion job '{job_id}' was not found.",
            code="JOB_NOT_FOUND",
            status_code=404
        )
    return job_status
