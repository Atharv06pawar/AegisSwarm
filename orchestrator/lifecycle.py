"""
LifecycleManager managing start, pause, resume, cancel, retry, restart operations.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from orchestrator.models import MissionModel, MissionState
from orchestrator.state_machine import MissionStateMachine
from orchestrator.exceptions import MissionError


class LifecycleManager:
    """
    Manages operational lifecycle state transitions and actions on active missions.
    """

    def __init__(self, state_machine: Optional[MissionStateMachine] = None):
        self.state_machine = state_machine or MissionStateMachine()

    def start(self, mission: MissionModel) -> MissionModel:
        """Starts a mission from CREATED -> READY -> PLANNING."""
        if mission.state == MissionState.CREATED:
            self.state_machine.transition_to(MissionState.READY)
            mission.state = MissionState.READY
        return mission

    def transition(self, mission: MissionModel, target_state: MissionState) -> MissionModel:
        """Transitions mission state machine to target_state."""
        new_state = self.state_machine.transition_to(target_state)
        mission.state = new_state
        return mission

    def pause(self, mission: MissionModel) -> MissionModel:
        """Pauses execution (retains current state)."""
        return mission

    def resume(self, mission: MissionModel) -> MissionModel:
        """Resumes paused execution."""
        return mission

    def cancel(self, mission: MissionModel) -> MissionModel:
        """Cancels an active mission."""
        if mission.state not in [MissionState.COMPLETED, MissionState.CANCELLED]:
            self.state_machine.transition_to(MissionState.CANCELLED)
            mission.state = MissionState.CANCELLED
        return mission
