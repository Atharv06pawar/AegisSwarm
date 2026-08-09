import pytest
from uuid import uuid4
from campaign.models import CampaignCheckpoint, CampaignStatus, CampaignBudget
from campaign.checkpoint import CampaignCheckpointManager
from campaign.exceptions import CheckpointError


def test_checkpoint_manager_save_and_load(tmp_path):
    """Verify CampaignCheckpointManager atomic save and load operations."""
    mgr = CampaignCheckpointManager(base_dir=tmp_path)
    cid = uuid4()

    cp = CampaignCheckpoint(
        campaign_id=cid,
        status=CampaignStatus.RUNNING,
        completed_attack_ids=["sample-1"],
        remaining_attack_ids=["sample-2"],
        current_budget=CampaignBudget(max_cost_usd=100.0, current_cost_usd=5.0)
    )

    path = mgr.save_checkpoint(cp)
    assert path.exists()
    assert "checkpoint.json" in path.name

    loaded = mgr.load_checkpoint(cid)
    assert loaded.campaign_id == cid
    assert loaded.status == CampaignStatus.RUNNING
    assert loaded.current_budget.current_cost_usd == 5.0


def test_checkpoint_manager_load_non_existent_raises(tmp_path):
    """Verify loading non-existent checkpoint raises CheckpointError."""
    mgr = CampaignCheckpointManager(base_dir=tmp_path)
    with pytest.raises(CheckpointError, match="Checkpoint file not found"):
        mgr.load_checkpoint(uuid4())
