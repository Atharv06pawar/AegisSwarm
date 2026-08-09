"""
CampaignDispatcher module for orchestrating work dispatch, worker assignment, and result routing.
"""

import logging
from typing import List, Tuple, Dict, Any, Optional
from uuid import UUID

from core.schema import AttackRecord
from execution.models import ExecutionRequest, ExecutionResult
from evaluation.evaluator import EvaluationEngine
from evaluation.models import EvaluationRequest, EvaluationResult
from swarm.memory import SwarmMemory
from swarm.advisor import StrategyAdvisor
from campaign.models import CampaignConfig, CampaignBudget, CampaignStatus, CampaignWorker
from campaign.worker import CampaignWorkerPool
from campaign.budget import CampaignBudgetController
from campaign.metrics import CampaignMetricsCollector
from campaign.checkpoint import CampaignCheckpointManager
from campaign.persistence import CampaignPersistence

logger = logging.getLogger(__name__)


class CampaignDispatcher:
    """
    Dispatcher assigning queue tasks to workers, executing attacks, invoking evaluation,
    recording telemetry metrics, managing checkpoints, and handling retries.
    """

    def __init__(
        self,
        worker_pool: CampaignWorkerPool,
        evaluator_engine: Optional[EvaluationEngine] = None,
        memory: Optional[SwarmMemory] = None,
        advisor: Optional[StrategyAdvisor] = None,
        budget_controller: Optional[CampaignBudgetController] = None,
        metrics_collector: Optional[CampaignMetricsCollector] = None,
        checkpoint_manager: Optional[CampaignCheckpointManager] = None,
        persistence: Optional[CampaignPersistence] = None
    ):
        self.worker_pool = worker_pool
        self.evaluator_engine = evaluator_engine or EvaluationEngine()
        self.memory = memory or SwarmMemory()
        self.advisor = advisor or StrategyAdvisor()
        self.budget_controller = budget_controller or CampaignBudgetController()
        self.metrics_collector = metrics_collector or CampaignMetricsCollector()
        self.checkpoint_manager = checkpoint_manager or CampaignCheckpointManager()
        self.persistence = persistence or CampaignPersistence()

    def dispatch_task(
        self,
        config: CampaignConfig,
        provider: str,
        record: AttackRecord,
        is_retry: bool = False,
        is_mutated: bool = False
    ) -> Tuple[ExecutionResult, EvaluationResult]:
        """
        Dispatches a single attack item: assigns an idle worker, executes attack,
        evaluates outcome, updates budget and metrics, and returns results.
        """
        # Find idle worker for target provider
        worker = self.worker_pool.get_idle_worker(provider)
        if not worker:
            # Fallback to any idle worker if available
            worker = self.worker_pool.get_idle_worker()

        if not worker:
            raise RuntimeError(f"No idle worker available in pool for provider '{provider}'")

        # Prepare ExecutionRequest
        context = {
            "campaign_id": str(config.campaign_id),
            "target_provider": provider,
            "target_model": worker.model
        }
        exec_req = ExecutionRequest(
            attack_record=record,
            provider=provider,
            model=worker.model,
            metadata={"campaign_id": str(config.campaign_id)}
        )

        # Execute via worker
        exec_res = self.worker_pool.execute_worker_task(worker.worker_id, exec_req)

        # Evaluate outcome
        eval_req = EvaluationRequest(execution_result=exec_res, attack_record=record)
        eval_res = self.evaluator_engine.evaluate(eval_req)

        # Record spend in budget controller
        tokens_used = exec_res.total_tokens or 500
        self.budget_controller.record_spend(config.budget, tokens_used=tokens_used, provider=provider)

        # Update telemetry metrics
        self.metrics_collector.record_attack(
            provider=provider,
            success=eval_res.attack_success,
            latency_ms=exec_res.latency_ms,
            tokens=tokens_used,
            cost=exec_res.estimated_cost,
            is_retry=is_retry,
            is_mutated=is_mutated
        )

        # Update SwarmMemory
        if eval_res.attack_success:
            self.memory.append_to_list("completed_attacks", str(record.sample_id))
        else:
            self.memory.append_to_list("failed_attacks", str(record.sample_id))

        if eval_res.prompt_leak_detected:
            self.memory.append_to_list("discovered_leakage", eval_res.evaluation_reason)

        return exec_res, eval_res
