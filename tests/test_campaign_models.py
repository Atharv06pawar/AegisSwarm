import pytest
from uuid import uuid4
from campaign.models import (
    CampaignConfig,
    CampaignObjective,
    CampaignTarget,
    CampaignBudget,
    CampaignStatus,
    CampaignWorker,
    CampaignMetrics,
    CampaignCheckpoint,
    CampaignResult,
    CampaignProgress
)


def test_campaign_config_model():
    """Verify CampaignConfig instantiation and defaults."""
    obj = CampaignObjective(name="Red-Team Benchmark", description="Test campaign")
    target = CampaignTarget(provider="openai", model="gpt-4o", max_concurrency=4)
    budget = CampaignBudget(max_cost_usd=50.0)

    config = CampaignConfig(
        name="Test Campaign",
        objective=obj,
        targets=[target],
        selected_datasets=["jailbreakbench"],
        swarm_agents=["jailbreak"],
        maximum_attacks=50,
        parallel_workers=4,
        budget=budget
    )

    assert config.name == "Test Campaign"
    assert config.objective.name == "Red-Team Benchmark"
    assert config.budget.max_cost_usd == 50.0
    assert len(config.targets) == 1
    assert config.campaign_id is not None


def test_campaign_checkpoint_model():
    """Verify CampaignCheckpoint model."""
    cid = uuid4()
    cp = CampaignCheckpoint(
        campaign_id=cid,
        status=CampaignStatus.RUNNING,
        completed_attack_ids=["att-1"],
        remaining_attack_ids=["att-2"]
    )
    assert cp.campaign_id == cid
    assert cp.status == CampaignStatus.RUNNING
    assert len(cp.completed_attack_ids) == 1
