"""
CampaignWorker and CampaignWorkerPool module for AegisSwarm Distributed Campaign Engine.
Manages worker state, heartbeats, and provider attack execution.
"""

import logging
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any

from execution.models import ExecutionRequest, ExecutionResult
from execution.executor import AttackExecutor
from campaign.models import CampaignWorker, CampaignTarget
from campaign.exceptions import WorkerError

logger = logging.getLogger(__name__)


class CampaignWorkerPool:
    """
    Worker pool managing distributed CampaignWorker instances across multiple targets.
    Workers execute AttackExecutor without embedding planning logic.
    """

    def __init__(self, campaign_id: UUID, executor: Optional[AttackExecutor] = None):
        self.campaign_id = campaign_id
        self.executor = executor or AttackExecutor()
        self._workers: Dict[UUID, CampaignWorker] = {}

    def initialize_pool(self, targets: List[CampaignTarget]) -> List[CampaignWorker]:
        """
        Instantiates worker instances for each target according to concurrency settings.
        
        Args:
            targets (List[CampaignTarget]): Provider target specifications.
            
        Returns:
            List[CampaignWorker]: Initialized worker pool.
        """
        self._workers.clear()
        for target in targets:
            for _ in range(target.max_concurrency):
                worker = CampaignWorker(
                    worker_id=uuid4(),
                    provider=target.provider,
                    model=target.model or "default",
                    status="idle",
                    current_campaign=str(self.campaign_id)
                )
                self._workers[worker.worker_id] = worker

        logger.info(f"Initialized worker pool with {len(self._workers)} workers for campaign '{self.campaign_id}'")
        return list(self._workers.values())

    def get_idle_worker(self, provider: Optional[str] = None) -> Optional[CampaignWorker]:
        """
        Retrieves an idle worker, optionally filtered by provider.
        """
        for worker in self._workers.values():
            if worker.status == "idle":
                if provider is None or worker.provider.lower() == provider.lower():
                    return worker
        return None

    def execute_worker_task(self, worker_id: UUID, request: ExecutionRequest) -> ExecutionResult:
        """
        Assigns an execution task to a worker node, executes via AttackExecutor, and updates heartbeat.
        """
        if worker_id not in self._workers:
            raise WorkerError(str(worker_id), str(self.campaign_id), "Worker ID not found in pool.")

        worker = self._workers[worker_id]
        worker.status = "busy"
        worker.current_attack = str(request.attack_record.sample_id)
        worker.last_heartbeat = datetime.now(timezone.utc).isoformat()

        try:
            result = self.executor.execute(request)
            worker.status = "idle"
            worker.current_attack = None
            worker.last_heartbeat = datetime.now(timezone.utc).isoformat()
            return result

        except Exception as err:
            worker.status = "error"
            worker.last_heartbeat = datetime.now(timezone.utc).isoformat()
            logger.error(f"Worker '{worker_id}' failed execution: {err}")
            raise WorkerError(str(worker_id), str(self.campaign_id), str(err)) from err

    def list_workers(self) -> List[CampaignWorker]:
        """Returns snapshot of current worker states."""
        return list(self._workers.values())
