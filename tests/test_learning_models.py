import pytest
from learning.models import LearningMemoryRecord, AttackPlan, GraphNode, GraphEdge, AttackGraphModel, ReplaySessionModel


def test_learning_memory_record_model():
    """Verify LearningMemoryRecord model defaults and validation."""
    rec = LearningMemoryRecord(attack_id="atk-1", provider="openai", model="gpt-4o", attack_success=True)
    assert rec.attack_id == "atk-1"
    assert rec.attack_success is True


def test_attack_plan_model():
    """Verify AttackPlan model defaults."""
    plan = AttackPlan(target_provider="anthropic", chosen_family="roleplay")
    assert plan.target_provider == "anthropic"
    assert plan.chosen_family == "roleplay"


def test_attack_graph_model():
    """Verify AttackGraphModel serialization."""
    node = GraphNode(node_id="n1", node_type="Prompt", label="PromptNode")
    edge = GraphEdge(source_id="n1", target_id="n2", edge_type="mutation")
    graph = AttackGraphModel(nodes=[node], edges=[edge])
    assert len(graph.nodes) == 1
    assert len(graph.edges) == 1
