"""
SwarmOrchestrator module for AegisSwarm.
Orchestrates multi-agent swarm campaigns against target AI providers.
"""

import time
import logging
from typing import Optional, List
from datetime import datetime, timezone
from uuid import UUID

from execution.executor import AttackExecutor
from evaluation.evaluator import EvaluationEngine
from evaluation.models import EvaluationRequest
from swarm.models import SwarmRequest, SwarmResult, SwarmAgentResult
from swarm.base import BaseSwarmAgent
from swarm.planner import BasePlanner, SequentialPlanner
from swarm.scheduler import SwarmScheduler
from swarm.factory import SwarmFactory
from swarm.memory import SwarmMemory
from swarm.metrics import SwarmMetrics
from swarm.persistence import SwarmPersistence

logger = logging.getLogger(__name__)


class SwarmOrchestrator:
    """
    Core orchestration engine coordinating planners, schedulers, attacker agents,
    the AttackExecutor, EvaluationEngine, shared memory, and persistence.
    """

    def __init__(
        self,
        planner: Optional[BasePlanner] = None,
        scheduler: Optional[SwarmScheduler] = None,
        executor: Optional[AttackExecutor] = None,
        evaluator_engine: Optional[EvaluationEngine] = None,
        memory: Optional[SwarmMemory] = None,
        metrics: Optional[SwarmMetrics] = None,
        persistence: Optional[SwarmPersistence] = None
    ):
        self.planner = planner or SequentialPlanner()
        self.scheduler = scheduler or SwarmScheduler()
        self.executor = executor or AttackExecutor()
        self.evaluator_engine = evaluator_engine or EvaluationEngine()
        self.memory = memory or SwarmMemory()
        self.metrics = metrics or SwarmMetrics()
        self.persistence = persistence or SwarmPersistence()

    def run_swarm(self, request: SwarmRequest) -> SwarmResult:
        """
        Runs a complete swarm attack campaign described by SwarmRequest.
        
        Args:
            request (SwarmRequest): Input swarm request payload.
            
        Returns:
            SwarmResult: Standardized swarm execution summary model.
        """
        start_wall_time = datetime.now(timezone.utc).isoformat()
        start_perf = time.perf_counter()
        swarm_id = request.swarm_id

        logger.info(f"Starting SwarmOrchestrator run (swarm_id={swarm_id}, provider='{request.target_provider}')")

        # Step 1: Planner creates agent attack plan
        plan = self.planner.plan(request)

        # Step 2: Scheduler builds execution queue
        queue = self.scheduler.schedule(plan)

        completed_agents = 0
        failed_agents = 0
        execution_ids: List[UUID] = []
        evaluation_ids: List[UUID] = []
        agent_results: List[SwarmAgentResult] = []

        context = {
            "swarm_id": str(swarm_id),
            "target_provider": request.target_provider,
            "target_model": request.target_model
        }

        # Step 3: Iterate through scheduled agent tasks
        for agent_name, record in queue:
            agent_start = time.perf_counter()
            try:
                # Instantiate agent using SwarmFactory
                agent: BaseSwarmAgent = SwarmFactory.create(agent_name)
                
                # Agent prepares ExecutionRequest
                exec_req = agent.prepare(record, context=context)
                
                # Execute attack via AttackExecutor
                exec_res = agent.execute(self.executor, exec_req)
                execution_ids.append(exec_res.execution_id)

                # Evaluate attack via EvaluationEngine
                eval_req = EvaluationRequest(execution_result=exec_res, attack_record=record)
                eval_res = self.evaluator_engine.evaluate(eval_req)
                evaluation_ids.append(eval_res.evaluation_id)

                agent_time_ms = (time.perf_counter() - agent_start) * 1000.0

                agent_result = SwarmAgentResult(
                    agent_name=agent_name,
                    execution_id=exec_res.execution_id,
                    evaluation_id=eval_res.evaluation_id,
                    attack_success=eval_res.attack_success,
                    confidence=eval_res.confidence,
                    severity=eval_res.severity_score,
                    provider=exec_res.provider,
                    model=exec_res.model,
                    execution_time_ms=round(agent_time_ms, 2)
                )

                agent_results.append(agent_result)

                # Update shared memory
                if eval_res.attack_success:
                    self.memory.append_to_list("completed_attacks", str(record.sample_id))
                else:
                    self.memory.append_to_list("failed_attacks", str(record.sample_id))

                if eval_res.prompt_leak_detected:
                    self.memory.append_to_list("discovered_leakage", eval_res.evaluation_reason)

                self.memory.append_to_list("evaluator_findings", eval_res.model_dump())
                self.metrics.record(agent_result, cost=exec_res.estimated_cost)
                completed_agents += 1

            except Exception as err:
                logger.error(f"Error executing swarm agent '{agent_name}': {err}")
                failed_agents += 1

        end_wall_time = datetime.now(timezone.utc).isoformat()
        total_duration_ms = (time.perf_counter() - start_perf) * 1000.0

        total_attacks = len(agent_results)
        successful_attacks = sum(1 for r in agent_results if r.attack_success)
        avg_confidence = (sum(r.confidence for r in agent_results) / total_attacks) if total_attacks > 0 else 0.0
        avg_severity = (sum(r.severity for r in agent_results) / total_attacks) if total_attacks > 0 else 0.0
        total_cost = sum(m.total_cost for m in [self.metrics])

        status = "completed" if failed_agents == 0 else ("partially_completed" if completed_agents > 0 else "failed")

        result = SwarmResult(
            swarm_id=swarm_id,
            started_at=start_wall_time,
            completed_at=end_wall_time,
            status=status,
            total_agents=len(queue),
            completed_agents=completed_agents,
            failed_agents=failed_agents,
            total_attacks=total_attacks,
            successful_attacks=successful_attacks,
            execution_ids=execution_ids,
            evaluation_ids=evaluation_ids,
            agent_results=agent_results,
            average_confidence=round(avg_confidence, 2),
            average_severity=round(avg_severity, 2),
            total_cost=round(total_cost, 6),
            latency_ms=round(total_duration_ms, 2)
        )

        # Step 4: Persist swarm campaign manifest
        self.persistence.save_swarm_result(request, result)

        logger.info(
            f"Finished SwarmOrchestrator run (swarm_id={swarm_id}, completed={completed_agents}, "
            f"failed={failed_agents}, success_rate={(successful_attacks/total_attacks if total_attacks>0 else 0)*100:.1f}%)"
        )

        return result
