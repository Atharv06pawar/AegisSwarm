"""
RecoveryEngine restoring mission execution from state checkpoints.
"""

from typing import Optional
from uuid import UUID
from orchestrator.models import MissionCheckpoint, MissionState
from orchestrator.exceptions import RecoveryError


class RecoveryEngine:
    """
    Handles automatic fault recovery and state restoration from saved checkpoints.
    """

    def recover_mission(
        self,
        mission_id: UUID,
        checkpoint: Optional[MissionCheckpoint] = None
    ) -> MissionState:
        """
        Restores mission from checkpoint and returns safe target recovery state.
        """
        if not checkpoint:
            return MissionState.PLANNING

        if checkpoint.state == MissionState.FAILED:
            return MissionState.EXECUTING
        elif checkpoint.state == MissionState.EXECUTING:
            return MissionState.EVALUATING
        else:
            return MissionState.READY
