import pytest
from tests.test_execution_models import create_sample_attack_record
from campaign.models import CampaignConfig, CampaignObjective, CampaignTarget, CampaignBudget
from campaign.scheduler import CampaignScheduler
from campaign.exceptions import CampaignConfigurationError


def test_campaign_scheduler_builds_queue():
    """Verify CampaignScheduler builds execution queue matching target providers."""
    obj = CampaignObjective(name="Benchmark")
    target1 = CampaignTarget(provider="openai")
    target2 = CampaignTarget(provider="anthropic")
    config = CampaignConfig(name="Scheduler Test", objective=obj, targets=[target1, target2], maximum_attacks=10)

    records = [create_sample_attack_record() for _ in range(4)]
    scheduler = CampaignScheduler()
    queue = scheduler.build_execution_queue(config, records)

    assert len(queue) == 4
    assert queue[0][0] == "openai"
    assert queue[1][0] == "anthropic"


def test_campaign_scheduler_empty_records_raises():
    """Verify empty records raises CampaignConfigurationError."""
    obj = CampaignObjective(name="Benchmark")
    config = CampaignConfig(name="Scheduler Test", objective=obj, targets=[CampaignTarget(provider="openai")])
    scheduler = CampaignScheduler()

    with pytest.raises(CampaignConfigurationError, match="empty records"):
        scheduler.build_execution_queue(config, [])
