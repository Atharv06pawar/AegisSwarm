"""
OrchestratorScheduler scheduling mission tasks with provider, budget, and parallelism awareness.
"""

from typing import List, Dict, Any
from orchestrator.models import MissionRequest
from orchestrator.exceptions import SchedulerError


class OrchestratorScheduler:
    """
    Schedules attack executions across providers considering parallel workers and budget limits.
    """

    def schedule_mission(self, request: MissionRequest, plan_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Creates an ordered sequence of executable task specifications.
        """
        if request.budget_usd <= 0.0:
            raise SchedulerError("Cannot schedule mission with zero or negative budget.")

        tasks: List[Dict[str, Any]] = []
        cost_per_attack = min(0.10, request.budget_usd / request.max_attacks)

        for i in range(request.max_attacks):
            task_id = f"task-{request.mission_id}-{i+1}"
            tasks.append({
                "task_id": task_id,
                "mission_id": str(request.mission_id),
                "sequence_index": i + 1,
                "provider": request.target_provider,
                "model": request.target_model,
                "estimated_cost": cost_per_attack,
                "parallel_group": i % request.parallelism
            })

        return tasks
