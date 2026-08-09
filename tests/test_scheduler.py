"""
Unit tests for OrchestratorScheduler in orchestrator package.
"""

import pytest
from orchestrator.scheduler import OrchestratorScheduler
from orchestrator.models import MissionRequest
from orchestrator.exceptions import SchedulerError


def test_scheduler_mission_batch():
    scheduler = OrchestratorScheduler()
    req = MissionRequest(objective="Scheduler test", target_provider="openai", max_attacks=5, budget_usd=10.0)
    plan_details = {"confidence": 0.9}

    tasks = scheduler.schedule_mission(req, plan_details)
    assert len(tasks) == 5
    for t in tasks:
        assert t["provider"] == "openai"
        assert t["estimated_cost"] > 0.0


def test_scheduler_zero_budget():
    scheduler = OrchestratorScheduler()
    req = MissionRequest(objective="Zero budget test", budget_usd=0.0)
    with pytest.raises(SchedulerError):
        scheduler.schedule_mission(req, {})
