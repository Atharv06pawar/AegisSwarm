"""
ExecutionGraphBuilder constructing and managing DAG execution representations for missions.
"""

from uuid import UUID
from typing import List, Dict, Any, Optional

from orchestrator.models import MissionExecutionGraph, MissionGraphNode, MissionGraphEdge
from orchestrator.exceptions import ExecutionGraphError


class ExecutionGraphBuilder:
    """
    Constructs and traverses a directed acyclic graph (DAG) representing mission pipeline stages.
    """

    STAGES = ["reasoning", "campaign", "swarm", "cluster", "execution", "evaluation", "learning", "reporting"]

    def build_default_graph(self, mission_id: UUID) -> MissionExecutionGraph:
        """
        Builds standard DAG pipeline connecting reasoning -> campaign -> swarm -> cluster -> execution -> evaluation -> learning -> reporting.
        """
        nodes: List[MissionGraphNode] = []
        edges: List[MissionGraphEdge] = []

        for i, stage in enumerate(self.STAGES):
            node_id = f"node-{stage}"
            nodes.append(
                MissionGraphNode(
                    node_id=node_id,
                    stage_name=stage,
                    status="PENDING",
                    details={"sequence_order": i + 1}
                )
            )

        for i in range(len(self.STAGES) - 1):
            src = f"node-{self.STAGES[i]}"
            tgt = f"node-{self.STAGES[i+1]}"
            edges.append(MissionGraphEdge(source_id=src, target_id=tgt, edge_type="dependency"))

        return MissionExecutionGraph(mission_id=mission_id, nodes=nodes, edges=edges)

    def export_mermaid(self, graph: MissionExecutionGraph) -> str:
        """Exports DAG graph topology as a Mermaid diagram string."""
        lines = ["graph TD"]
        for node in graph.nodes:
            lines.append(f'  {node.node_id}["{node.stage_name.upper()} ({node.status})"]')
        for edge in graph.edges:
            lines.append(f'  {edge.source_id} --> {edge.target_id}')
        return "\n".join(lines)
