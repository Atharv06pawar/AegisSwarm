import pytest
from uuid import uuid4
from tests.test_execution_models import create_sample_attack_record
from campaign.models import CampaignConfig, CampaignObjective, CampaignTarget, CampaignStatus, CampaignBudget
from campaign.manager import CampaignManager
from campaign.exceptions import CampaignNotFound, CampaignStateError, CampaignBudgetExceeded
from campaign.worker import CampaignWorkerPool
from campaign.checkpoint import CampaignCheckpointManager


def test_campaign_manager_lifecycle(tmp_path, monkeypatch):
    """Verify full end-to-end campaign lifecycle: create, start, pause, resume, cancel, report."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")

    manager = CampaignManager()
    target = CampaignTarget(provider="openai", model="gpt-4o", max_concurrency=2)
    config = CampaignConfig(
        name="Lifecycle Test",
        objective=CampaignObjective(name="Obj"),
        targets=[target],
        maximum_attacks=5
    )

    created = manager.create_campaign(config)
    assert created.campaign_id == config.campaign_id

    records = [create_sample_attack_record() for _ in range(2)]
    result = manager.start_campaign(config.campaign_id, records)
    assert result.status == CampaignStatus.COMPLETED
    assert result.progress.completed_attacks + result.progress.failed_attacks == 2

    # Verify pause/resume/cancel
    paused = manager.pause_campaign(config.campaign_id)
    assert paused.name == "Lifecycle Test"

    resumed = manager.resume_campaign(config.campaign_id)
    assert resumed.name == "Lifecycle Test"

    cancelled = manager.cancel_campaign(config.campaign_id)
    assert cancelled.name == "Lifecycle Test"

    # Verify listing and loading
    all_campaigns = manager.list_campaigns()
    assert len(all_campaigns) >= 1

    loaded = manager.load_campaign(config.campaign_id)
    assert loaded.name == "Lifecycle Test"

    # Verify report generation
    report_md = manager.get_report(config.campaign_id, format_type="markdown")
    assert "Campaign Audit Report: Lifecycle Test" in report_md

    report_json = manager.get_report(config.campaign_id, format_type="json")
    assert "Lifecycle Test" in report_json

    report_csv = manager.get_report(config.campaign_id, format_type="csv")
    assert "completed_attacks" in report_csv


def test_campaign_manager_error_cases():
    """Verify exception handling for non-existent and invalid state campaigns."""
    manager = CampaignManager()
    non_existent = uuid4()

    with pytest.raises(CampaignNotFound):
        manager.pause_campaign(non_existent)

    with pytest.raises(CampaignNotFound):
        manager.resume_campaign(non_existent)

    with pytest.raises(CampaignNotFound):
        manager.cancel_campaign(non_existent)


def test_worker_pool_and_checkpoint_helpers(tmp_path):
    """Verify worker pool querying and checkpoint pruning."""
    cid = uuid4()
    pool = CampaignWorkerPool(campaign_id=cid)
    workers = pool.initialize_pool([CampaignTarget(provider="openai", max_concurrency=2)])

    assert len(workers) == 2
    assert pool.get_idle_worker("openai") is not None
    assert pool.get_idle_worker("non_existent_provider") is None
    assert len(pool.list_workers()) == 2

    cp_mgr = CampaignCheckpointManager(base_dir=tmp_path)
    cp_mgr.prune_old_checkpoints(cid, keep=1)
