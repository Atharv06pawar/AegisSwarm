import pytest
from learning.memory import LearningMemory
from learning.models import LearningMemoryRecord
from learning.replay import ReplayEngine


def test_replay_engine_campaign_and_attack():
    """Verify ReplayEngine campaign and attack replay reproduction."""
    mem = LearningMemory()
    rec = LearningMemoryRecord(attack_id="atk-100", campaign_id="camp-1", provider="openai", model="gpt-4o", attack_success=True, evaluation_score=0.95)
    mem.store(rec)

    replay_eng = ReplayEngine(memory=mem)

    camp_res = replay_eng.replay_campaign("camp-1")
    assert camp_res.original_campaign_id == "camp-1"
    assert camp_res.reproduced_success is True

    atk_res = replay_eng.replay_attack("atk-100")
    assert atk_res.historical_score == 0.95
