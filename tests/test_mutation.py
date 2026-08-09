import pytest
from learning.mutation import MutationEngine
from learning.persistence import LearningPersistence
from learning.models import LearningMemoryRecord, AttackGraphModel
from learning.exceptions import LearningError, MemoryError, PlannerError, MutationError, GraphError, OptimizerError, ReplayError


def test_mutation_engine_all_families():
    """Verify MutationEngine mutates prompts across all 18 mutation families."""
    engine = MutationEngine()
    families = engine.list_families()
    assert len(families) == 18

    for fam in families:
        res = engine.mutate("Test prompt for safety evaluation", family=fam)
        assert res["family"] == fam
        assert "mutated_prompt" in res
        assert res["confidence"] > 0.0

    with pytest.raises(MutationError):
        engine.mutate("prompt", family="invalid_family_xyz")


def test_learning_persistence_all_methods(tmp_path):
    """Verify LearningPersistence saves memory, attack_graph, strategies, scores, and optimizer_state."""
    persistence = LearningPersistence(base_dir=tmp_path)
    rec = LearningMemoryRecord(attack_id="atk-p", provider="openai", model="gpt-4o")

    m_path = persistence.save_memory([rec])
    assert m_path.exists()

    g_model = AttackGraphModel()
    g_path = persistence.save_attack_graph(g_model)
    assert g_path.exists()

    s_path = persistence.save_strategies([{"strategy": "persona", "score": 0.8}])
    assert s_path.exists()

    sc_path = persistence.save_scores({"overall": 0.85})
    assert sc_path.exists()

    opt_path = persistence.save_optimizer_state({"agent_ordering": ["jailbreak"]})
    assert opt_path.exists()


def test_learning_exceptions():
    """Verify custom exception representations."""
    e1 = LearningError("base error")
    assert "[learning] base error" in str(e1)

    e2 = MemoryError("memory overflow")
    assert "[memory]" in str(e2)

    e3 = PlannerError("planner timeout")
    assert "[planner]" in str(e3)

    e4 = MutationError("family missing")
    assert "[mutation]" in str(e4)

    e5 = GraphError("node missing")
    assert "[graph]" in str(e5)

    e6 = OptimizerError("optimizer convergence failed")
    assert "[optimizer]" in str(e6)

    e7 = ReplayError("replay failed")
    assert "[replay]" in str(e7)
