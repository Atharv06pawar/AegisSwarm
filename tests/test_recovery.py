"""
Unit tests for RecoveryEngine in orchestrator package.
"""

from uuid import uuid4
from orchestrator.recovery import RecoveryEngine
from orchestrator.models import MissionCheckpoint, MissionState


def test_recovery_engine():
    engine = RecoveryEngine()
    m_id = uuid4()

    assert engine.recover_mission(m_id, None) == MissionState.PLANNING

    chk_failed = MissionCheckpoint(mission_id=m_id, state=MissionState.FAILED)
    assert engine.recover_mission(m_id, chk_failed) == MissionState.EXECUTING

    chk_exec = MissionCheckpoint(mission_id=m_id, state=MissionState.EXECUTING)
    assert engine.recover_mission(m_id, chk_exec) == MissionState.EVALUATING
