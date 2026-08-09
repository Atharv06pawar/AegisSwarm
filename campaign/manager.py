"""
CampaignManager module serving as the public entry point for distributed campaign executions.
"""

import json
import logging
from uuid import UUID
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.schema import AttackRecord
from campaign.models import (
    CampaignConfig,
    CampaignStatus,
    CampaignResult,
    CampaignProgress,
    CampaignMetrics,
    CampaignSummary,
    CampaignCheckpoint
)
from campaign.exceptions import CampaignError, CampaignNotFound, CampaignStateError
from campaign.scheduler import CampaignScheduler
from campaign.worker import CampaignWorkerPool
from campaign.dispatcher import CampaignDispatcher
from campaign.budget import CampaignBudgetController
from campaign.metrics import CampaignMetricsCollector
from campaign.checkpoint import CampaignCheckpointManager
from campaign.persistence import CampaignPersistence
from campaign.reporter import CampaignReportGenerator

logger = logging.getLogger(__name__)


class CampaignManager:
    """
    Public entry point orchestrating campaign lifecycles, parallel execution,
    checkpointing, persistence, metrics reporting, and controls.
    """

    def __init__(
        self,
        scheduler: Optional[CampaignScheduler] = None,
        budget_controller: Optional[CampaignBudgetController] = None,
        checkpoint_manager: Optional[CampaignCheckpointManager] = None,
        persistence: Optional[CampaignPersistence] = None
    ):
        self.scheduler = scheduler or CampaignScheduler()
        self.budget_controller = budget_controller or CampaignBudgetController()
        self.checkpoint_manager = checkpoint_manager or CampaignCheckpointManager()
        self.persistence = persistence or CampaignPersistence()
        
        self._active_campaigns: Dict[UUID, CampaignConfig] = {}
        self._campaign_statuses: Dict[UUID, CampaignStatus] = {}
        self._campaign_metrics: Dict[UUID, CampaignMetricsCollector] = {}

    def create_campaign(self, config: CampaignConfig) -> CampaignConfig:
        """Creates and registers a new campaign specification."""
        self._active_campaigns[config.campaign_id] = config
        self._campaign_statuses[config.campaign_id] = CampaignStatus.CREATED
        self._campaign_metrics[config.campaign_id] = CampaignMetricsCollector()

        self.persistence.save_campaign_manifest(config)
        logger.info(f"Created campaign '{config.name}' (id={config.campaign_id})")
        return config

    def start_campaign(self, campaign_id: UUID, records: List[AttackRecord]) -> CampaignResult:
        """Starts execution of a created or paused campaign."""
        if campaign_id not in self._active_campaigns:
            try:
                config = self.persistence.load_campaign_manifest(campaign_id)
                self._active_campaigns[campaign_id] = config
                self._campaign_statuses[campaign_id] = CampaignStatus.CREATED
                self._campaign_metrics[campaign_id] = CampaignMetricsCollector()
            except Exception:
                raise CampaignNotFound(str(campaign_id))

        config = self._active_campaigns[campaign_id]
        status = self._campaign_statuses[campaign_id]

        if status not in [CampaignStatus.CREATED, CampaignStatus.PAUSED]:
            raise CampaignStateError(str(campaign_id), status.value, "start")

        self._campaign_statuses[campaign_id] = CampaignStatus.RUNNING
        start_time = datetime.now(timezone.utc).isoformat()

        # Step 1: Scheduler builds execution queue
        queue = self.scheduler.build_execution_queue(config, records)
        self.persistence.save_queue(campaign_id, [{"provider": p, "sample_id": str(r.sample_id)} for p, r in queue])

        # Step 2: Worker pool initialization
        worker_pool = CampaignWorkerPool(campaign_id=campaign_id)
        workers = worker_pool.initialize_pool(config.targets)
        self.persistence.save_workers(campaign_id, [json.loads(w.model_dump_json()) for w in workers])

        # Step 3: Dispatcher execution
        metrics_collector = self._campaign_metrics[campaign_id]
        dispatcher = CampaignDispatcher(
            worker_pool=worker_pool,
            budget_controller=self.budget_controller,
            metrics_collector=metrics_collector,
            checkpoint_manager=self.checkpoint_manager,
            persistence=self.persistence
        )

        completed_count = 0
        failed_count = 0

        for provider, record in queue:
            # Respect pause/cancel state toggles
            if self._campaign_statuses[campaign_id] == CampaignStatus.PAUSED:
                logger.info(f"Campaign '{campaign_id}' paused during execution.")
                break
            if self._campaign_statuses[campaign_id] == CampaignStatus.CANCELLED:
                logger.info(f"Campaign '{campaign_id}' cancelled during execution.")
                break

            try:
                exec_res, eval_res = dispatcher.dispatch_task(config, provider, record)
                if eval_res.attack_success:
                    completed_count += 1
                else:
                    failed_count += 1
            except Exception as err:
                logger.error(f"Execution failed for record '{record.sample_id}': {err}")
                failed_count += 1

        end_time = datetime.now(timezone.utc).isoformat()
        final_status = self._campaign_statuses[campaign_id]

        if final_status == CampaignStatus.RUNNING:
            final_status = CampaignStatus.COMPLETED
            self._campaign_statuses[campaign_id] = final_status

        metrics = metrics_collector.compute_metrics()
        self.persistence.save_metrics(campaign_id, metrics)
        self.persistence.save_budget(campaign_id, config.budget)

        # Create progress model
        total_q = len(queue)
        progress = CampaignProgress(
            total_attacks=total_q,
            completed_attacks=completed_count,
            failed_attacks=failed_count,
            running_attacks=0,
            queued_attacks=max(0, total_q - (completed_count + failed_count)),
            percentage=round(((completed_count + failed_count) / max(total_q, 1)) * 100.0, 2)
        )

        result = CampaignResult(
            campaign_id=campaign_id,
            started_at=start_time,
            completed_at=end_time,
            status=final_status,
            progress=progress,
            metrics=metrics,
            budget=config.budget
        )

        self.persistence.save_results(campaign_id, json.loads(result.model_dump_json()))
        return result

    def pause_campaign(self, campaign_id: UUID) -> CampaignConfig:
        """Pauses a running campaign."""
        if campaign_id not in self._active_campaigns:
            raise CampaignNotFound(str(campaign_id))

        self._campaign_statuses[campaign_id] = CampaignStatus.PAUSED
        logger.info(f"Paused campaign '{campaign_id}'")
        return self._active_campaigns[campaign_id]

    def resume_campaign(self, campaign_id: UUID) -> CampaignConfig:
        """Resumes a paused campaign."""
        if campaign_id not in self._active_campaigns:
            raise CampaignNotFound(str(campaign_id))

        self._campaign_statuses[campaign_id] = CampaignStatus.RUNNING
        logger.info(f"Resumed campaign '{campaign_id}'")
        return self._active_campaigns[campaign_id]

    def cancel_campaign(self, campaign_id: UUID) -> CampaignConfig:
        """Cancels a campaign."""
        if campaign_id not in self._active_campaigns:
            raise CampaignNotFound(str(campaign_id))

        self._campaign_statuses[campaign_id] = CampaignStatus.CANCELLED
        logger.info(f"Cancelled campaign '{campaign_id}'")
        return self._active_campaigns[campaign_id]

    def load_campaign(self, campaign_id: UUID) -> CampaignConfig:
        """Loads a campaign manifest from disk."""
        return self.persistence.load_campaign_manifest(campaign_id)

    def list_campaigns(self) -> List[CampaignConfig]:
        """Lists all campaigns on disk."""
        manifests = self.persistence.list_all_campaigns()
        return [CampaignConfig.model_validate(m) for m in manifests]

    def get_metrics(self, campaign_id: UUID) -> CampaignMetrics:
        """Retrieves metrics for a campaign."""
        if campaign_id in self._campaign_metrics:
            return self._campaign_metrics[campaign_id].compute_metrics()
        return CampaignMetrics()

    def get_report(self, campaign_id: UUID, format_type: str = "markdown") -> str:
        """Generates an audit report in markdown, json, or csv."""
        config = self.load_campaign(campaign_id) if campaign_id not in self._active_campaigns else self._active_campaigns[campaign_id]
        metrics = self.get_metrics(campaign_id)

        fmt = format_type.lower()
        if fmt == "json":
            return CampaignReportGenerator.generate_json(config, metrics)
        elif fmt == "csv":
            return CampaignReportGenerator.generate_csv(config, metrics)
        else:
            return CampaignReportGenerator.generate_markdown(config, metrics)
