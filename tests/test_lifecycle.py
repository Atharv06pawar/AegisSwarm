"""
Unit tests for LifecycleManager in orchestrator package.
"""

from uuid import uuid4
from orchestrator.lifecycle import LifecycleManager
from orchestrator.models import MissionModel, MissionState


def test_lifecycle_manager_transitions():
    lifecycle = LifecycleManager()
    m_id = uuid4()
    mission = MissionModel(mission_id=m_id, objective="Lifecycle test", state=MissionState.CREATED)

    mission = lifecycle.start(mission)
    assert mission.state == MissionState.READY

    mission = lifecycle.transition(mission, MissionState.PLANNING)
    assert mission.state == MissionState.PLANNING

    mission = lifecycle.cancel(mission)
    assert mission.state == MissionState.CANCELLED
