import pytest
from learning.models import LearningMemoryRecord
from learning.memory import LearningMemory


def test_learning_memory_operations():
    """Verify LearningMemory store, lookup, history, statistics, and pruning."""
    mem = LearningMemory(capacity=5)

    rec1 = LearningMemoryRecord(attack_id="atk-1", provider="openai", model="gpt-4o", attack_success=True, evaluation_score=0.9)
    rec2 = LearningMemoryRecord(attack_id="atk-2", provider="openai", model="gpt-4o", attack_success=False, evaluation_score=0.2)

    mem.store(rec1)
    mem.store(rec2)

    assert mem.lookup("atk-1") == rec1
    assert len(mem.history(limit=10)) == 2

    stats = mem.statistics()
    assert stats["total_records"] == 2
    assert stats["overall_success_rate"] == 0.5

    mem.forget(rec1.record_id)
    assert mem.lookup("atk-1") is None
    assert len(mem.history()) == 1
