"""
AttackGraph module building, traversing, and searching directed attack execution graphs.
"""

from collections import deque
from typing import Dict, List, Optional, Set, Any
from uuid import uuid4

from learning.models import GraphNode, GraphEdge, AttackGraphModel
from learning.exceptions import GraphError


class AttackGraph:
    """
    Directed Graph representing attack execution nodes, mutations, provider paths, and outcomes.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._adjacency: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node_id: str, node_type: str, label: str, attributes: Optional[Dict[str, Any]] = None) -> GraphNode:
        """Adds a node to the attack graph."""
        node = GraphNode(node_id=node_id, node_type=node_type, label=label, attributes=attributes or {})
        self.nodes[node_id] = node
        if node_id not in self._adjacency:
            self._adjacency[node_id] = []
        return node

    def add_edge(self, source_id: str, target_id: str, edge_type: str, attributes: Optional[Dict[str, Any]] = None) -> GraphEdge:
        """Adds a directed edge between two graph nodes."""
        if source_id not in self.nodes or target_id not in self.nodes:
            raise GraphError("Source and target nodes must exist in AttackGraph before connecting edge.")

        edge = GraphEdge(source_id=source_id, target_id=target_id, edge_type=edge_type, attributes=attributes or {})
        self.edges.append(edge)
        self._adjacency[source_id].append(edge)
        return edge

    def bfs(self, start_node_id: str) -> List[str]:
        """Performs Breadth-First Search traversal starting from specified node."""
        if start_node_id not in self.nodes:
            return []

        visited: Set[str] = set()
        queue = deque([start_node_id])
        order: List[str] = []

        while queue:
            curr = queue.popleft()
            if curr not in visited:
                visited.add(curr)
                order.append(curr)
                for edge in self._adjacency.get(curr, []):
                    if edge.target_id not in visited:
                        queue.append(edge.target_id)
        return order

    def dfs(self, start_node_id: str) -> List[str]:
        """Performs Depth-First Search traversal starting from specified node."""
        if start_node_id not in self.nodes:
            return []

        visited: Set[str] = set()
        order: List[str] = []

        def _dfs_recursive(nid: str):
            visited.add(nid)
            order.append(nid)
            for edge in self._adjacency.get(nid, []):
                if edge.target_id not in visited:
                    _dfs_recursive(edge.target_id)

        _dfs_recursive(start_node_id)
        return order

    def find_paths(self, start_node_id: str, end_node_id: str) -> List[List[str]]:
        """Finds all paths from start_node_id to end_node_id."""
        paths: List[List[str]] = []

        def _find_dfs(curr: str, path: List[str]):
            if curr == end_node_id:
                paths.append(list(path))
                return
            for edge in self._adjacency.get(curr, []):
                if edge.target_id not in path:
                    _find_dfs(edge.target_id, path + [edge.target_id])

        if start_node_id in self.nodes and end_node_id in self.nodes:
            _find_dfs(start_node_id, [start_node_id])

        return paths

    def best_path(self, start_node_id: str, end_node_id: str) -> Optional[List[str]]:
        """Returns the shortest path between start_node_id and end_node_id."""
        paths = self.find_paths(start_node_id, end_node_id)
        if not paths:
            return None
        paths.sort(key=len)
        return paths[0]

    def export(self) -> AttackGraphModel:
        """Exports to Pydantic AttackGraphModel."""
        return AttackGraphModel(
            nodes=list(self.nodes.values()),
            edges=self.edges
        )
