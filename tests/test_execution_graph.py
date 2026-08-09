"""
Unit tests for ExecutionGraphBuilder in orchestrator package.
"""

from uuid import uuid4
from orchestrator.execution_graph import ExecutionGraphBuilder


def test_execution_graph_builder_and_mermaid():
    builder = ExecutionGraphBuilder()
    m_id = uuid4()
    graph = builder.build_default_graph(m_id)

    assert len(graph.nodes) == 8
    assert len(graph.edges) == 7

    mermaid = builder.export_mermaid(graph)
    assert "graph TD" in mermaid
    assert "REASONING" in mermaid
    assert "REPORTING" in mermaid
