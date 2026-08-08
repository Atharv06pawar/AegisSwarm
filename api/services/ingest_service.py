import time
import uuid
import threading
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import BackgroundTasks

from core.orchestrator import PipelineOrchestrator
from core.registry import PluginRegistry
from storage.data_lake import StorageBackend, JSONLBackend
from api.schemas.ingest import (
    IngestRequest, IngestResponse, JobStatusResponse, JobListResponse
)
from api.services.plugin_service import PluginService
from api.exceptions import AegisSwarmAPIException
from logging import get_ingestion_logger, get_error_logger

ingestion_logger = get_ingestion_logger()
error_logger = get_error_logger()

class JobManager:
    """
    Thread-safe in-memory state store tracking background ingestion jobs.
    Designed for future seamless abstraction to Redis/Celery result backends.
    """

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_job(self, job_id: str, datasets: List[str]) -> Dict[str, Any]:
        with self._lock:
            now = datetime.now(timezone.utc)
            job_state = {
                "job_id": job_id,
                "status": "queued",
                "current_stage": "queued",
                "progress_percentage": 0.0,
                "records_processed": 0,
                "batches_written": 0,
                "start_time": time.perf_counter(),
                "elapsed_seconds": 0.0,
                "estimated_remaining_seconds": None,
                "current_dataset": datasets[0] if datasets else None,
                "requested_datasets": datasets,
                "errors": [],
                "created_at": now,
                "completed_at": None
            }
            self._jobs[job_id] = job_state
            return job_state

    def update_job(self, job_id: str, **kwargs) -> None:
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(kwargs)
                start_t = self._jobs[job_id].get("start_time")
                if start_t:
                    self._jobs[job_id]["elapsed_seconds"] = round(time.perf_counter() - start_t, 2)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                start_t = job.get("start_time")
                if start_t and job["status"] in ("queued", "running"):
                    job["elapsed_seconds"] = round(time.perf_counter() - start_t, 2)
                return dict(job)
            return None

    def list_jobs(self) -> List[Dict[str, Any]]:
        with self._lock:
            results = []
            for job in self._jobs.values():
                start_t = job.get("start_time")
                if start_t and job["status"] in ("queued", "running"):
                    job["elapsed_seconds"] = round(time.perf_counter() - start_t, 2)
                results.append(dict(job))
            return results


class IngestService:
    """
    Service layer wrapping PipelineOrchestrator and JobManager.
    Manages non-blocking asynchronous ingestion jobs.
    """

    def __init__(
        self, 
        storage_backend: Optional[StorageBackend] = None,
        job_manager: Optional[JobManager] = None,
        plugin_service: Optional[PluginService] = None
    ):
        self.storage_backend = storage_backend or JSONLBackend(base_path="outputs/lake", compression="gzip")
        self.job_manager = job_manager or JobManager()
        self.plugin_service = plugin_service or PluginService()

    def submit_ingest_job(self, request: IngestRequest, background_tasks: BackgroundTasks) -> IngestResponse:
        """
        Validates dataset IDs and submits background ingestion task non-blockingly.
        """
        available_metadata = self.plugin_service.list_plugins()
        available_dataset_ids = [m.dataset_id for m in available_metadata]

        for ds_id in request.datasets:
            if ds_id not in available_dataset_ids:
                error_logger.error(f"Invalid dataset ID requested for ingestion: '{ds_id}'")
                raise AegisSwarmAPIException(
                    detail=f"Invalid dataset ID '{ds_id}'. Available dataset plugins: {available_dataset_ids}",
                    code="INVALID_DATASET_ID",
                    status_code=400
                )

        job_id = f"job_{uuid.uuid4().hex[:10]}"
        self.job_manager.create_job(job_id, request.datasets)

        ingestion_logger.info(f"Submitted background ingestion job '{job_id}' for datasets: {request.datasets}")

        # Launch background task
        background_tasks.add_task(self._execute_ingest_background, job_id, request)

        return IngestResponse(
            job_id=job_id,
            status="queued",
            requested_datasets=request.datasets,
            message=f"Ingestion job '{job_id}' submitted successfully."
        )

    def _execute_ingest_background(self, job_id: str, request: IngestRequest) -> None:
        """
        Background task executing PipelineOrchestrator over requested datasets.
        """
        self.job_manager.update_job(job_id, status="running", current_stage="parsing")
        total_ds = len(request.datasets)

        orchestrator = PipelineOrchestrator(
            storage_backend=self.storage_backend,
            plugin_registry=PluginRegistry,
            batch_size=request.batch_size or 1000
        )

        records_processed_accum = 0
        batches_written_accum = 0

        try:
            for idx, ds_id in enumerate(request.datasets):
                self.job_manager.update_job(
                    job_id,
                    current_dataset=ds_id,
                    current_stage=f"processing_{ds_id}",
                    progress_percentage=round((idx / total_ds) * 100.0, 1)
                )

                if not request.dry_run:
                    orchestrator.run_plugin(ds_id)
                    ds_stats = orchestrator.stats.get(ds_id, {})
                    records_processed_accum += ds_stats.get("records_processed", 0)
                    batches_written_accum += ds_stats.get("batches_written", 0)
                else:
                    records_processed_accum += 10
                    batches_written_accum += 1

                self.job_manager.update_job(
                    job_id,
                    records_processed=records_processed_accum,
                    batches_written=batches_written_accum,
                    progress_percentage=round(((idx + 1) / total_ds) * 100.0, 1)
                )

            # Flush lineage manifest
            if not request.dry_run:
                orchestrator.lineage_tracker.save_manifest()

            self.job_manager.update_job(
                job_id,
                status="completed",
                current_stage="completed",
                progress_percentage=100.0,
                completed_at=datetime.now(timezone.utc)
            )
            ingestion_logger.info(f"Ingestion job '{job_id}' completed successfully. Records: {records_processed_accum}")

        except Exception as e:
            error_logger.error(f"Ingestion job '{job_id}' failed with exception: {e}", exc_info=True)
            self.job_manager.update_job(
                job_id,
                status="failed",
                current_stage="failed",
                errors=[str(e)],
                completed_at=datetime.now(timezone.utc)
            )

    def get_job_status(self, job_id: str) -> Optional[JobStatusResponse]:
        """
        Retrieves status of a specific job by ID.
        """
        job = self.job_manager.get_job(job_id)
        if not job:
            return None

        return JobStatusResponse(
            job_id=job["job_id"],
            status=job["status"],
            current_stage=job["current_stage"],
            progress_percentage=job["progress_percentage"],
            records_processed=job["records_processed"],
            batches_written=job["batches_written"],
            elapsed_seconds=job["elapsed_seconds"],
            estimated_remaining_seconds=job.get("estimated_remaining_seconds"),
            current_dataset=job.get("current_dataset"),
            errors=job.get("errors", []),
            created_at=job["created_at"],
            completed_at=job.get("completed_at")
        )

    def list_jobs(self) -> JobListResponse:
        """
        Lists status objects for all active and completed jobs.
        """
        raw_jobs = self.job_manager.list_jobs()
        status_responses: List[JobStatusResponse] = []

        for job in raw_jobs:
            status_responses.append(
                JobStatusResponse(
                    job_id=job["job_id"],
                    status=job["status"],
                    current_stage=job["current_stage"],
                    progress_percentage=job["progress_percentage"],
                    records_processed=job["records_processed"],
                    batches_written=job["batches_written"],
                    elapsed_seconds=job["elapsed_seconds"],
                    estimated_remaining_seconds=job.get("estimated_remaining_seconds"),
                    current_dataset=job.get("current_dataset"),
                    errors=job.get("errors", []),
                    created_at=job["created_at"],
                    completed_at=job.get("completed_at")
                )
            )

        return JobListResponse(
            total_jobs=len(status_responses),
            jobs=status_responses
        )
