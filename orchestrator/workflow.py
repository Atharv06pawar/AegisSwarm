"""
OrchestratorWorkflow managing autonomous mission lifecycle workflow execution.
"""

from typing import Optional
from orchestrator.models import MissionRequest, MissionModel
from orchestrator.coordinator import MissionCoordinator
from learning.memory import LearningMemory


class OrchestratorWorkflow:
    """
    Workflow runner orchestrating mission initialization, planning, execution, and reporting.
    """

    def __init__(self, coordinator: Optional[MissionCoordinator] = None):
        self.coordinator = coordinator or MissionCoordinator()

    def run_mission_workflow(
        self,
        request: MissionRequest,
        learning_memory: Optional[LearningMemory] = None
    ) -> MissionModel:
        """Runs complete autonomous mission workflow."""
        return self.coordinator.execute_mission(request=request, learning_memory=learning_memory)
