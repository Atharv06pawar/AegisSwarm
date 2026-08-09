import pytest
from learning.graph import AttackGraph
from learning.exceptions import GraphError


def test_attack_graph_traversal_and_export():
    """Verify AttackGraph node/edge creation, BFS, DFS, path search, and export."""
    graph = AttackGraph()

    n1 = graph.add_node("n1", "Prompt", "Base Prompt")
    n2 = graph.add_node("n2", "Mutation", "Persona Obfuscation")
    n3 = graph.add_node("n3", "Provider", "openai:gpt-4o")

    graph.add_edge("n1", "n2", "mutation")
    graph.add_edge("n2", "n3", "provider_switch")

    bfs_order = graph.bfs("n1")
    assert bfs_order == ["n1", "n2", "n3"]

    dfs_order = graph.dfs("n1")
    assert dfs_order == ["n1", "n2", "n3"]

    best = graph.best_path("n1", "n3")
    assert best == ["n1", "n2", "n3"]

    model = graph.export()
    assert len(model.nodes) == 3
    assert len(model.edges) == 2


def test_attack_graph_invalid_edge():
    """Verify GraphError when adding edge with non-existent node."""
    graph = AttackGraph()
    with pytest.raises(GraphError):
        graph.add_edge("missing1", "missing2", "success")
