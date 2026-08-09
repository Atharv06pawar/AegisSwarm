import pytest
from uuid import uuid4
from tests.test_execution_models import create_sample_attack_record
from campaign.models import CampaignConfig, CampaignObjective, CampaignTarget
from campaign.worker import CampaignWorkerPool
from campaign.dispatcher import CampaignDispatcher


def test_campaign_dispatcher_dispatch_task(tmp_path, monkeypatch):
    """Verify CampaignDispatcher dispatches task to worker pool, executes, and updates telemetry."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-123")

    cid = uuid4()
    target = CampaignTarget(provider="openai", model="gpt-4o", max_concurrency=2)
    config = CampaignConfig(campaign_id=cid, name="Dispatch Test", objective=CampaignObjective(name="Obj"), targets=[target])

    pool = CampaignWorkerPool(campaign_id=cid)
    pool.initialize_pool([target])

    dispatcher = CampaignDispatcher(worker_pool=pool)
    record = create_sample_attack_record()

    exec_res, eval_res = dispatcher.dispatch_task(config, provider="openai", record=record)

    assert exec_res.provider == "openai"
    assert eval_res.evaluation_id is not None
