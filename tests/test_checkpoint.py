"""
Unit tests for CheckpointManager in orchestrator package.
"""

from uuid import uuid4
from orchestrator.checkpoint import CheckpointManager
from orchestrator.models import MissionCheckpoint, MissionState


def test_checkpoint_manager_save_and_retrieve(tmp_path):
    mgr = CheckpointManager(base_dir=tmp_path)
    m_id = uuid4()
    chk = MissionCheckpoint(
        mission_id=m_id,
        state=MissionState.EXECUTING,
        step_index=2,
        completed_stages=["reasoning", "campaign"]
    )

    path = mgr.save_checkpoint(chk)
    assert path.exists()

    retrieved = mgr.get_latest_checkpoint(m_id)
    assert retrieved is not None
    assert retrieved.mission_id == m_id
    assert retrieved.state == MissionState.EXECUTING
