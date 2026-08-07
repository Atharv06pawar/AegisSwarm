import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field, ConfigDict

from corpus.registry import CorpusRegistry
from corpus.statistics import CorpusStatisticsCalculator

class OntologyCoverageReport(BaseModel):
    """
    Pydantic v2 data contract representing the AUAO v1.0 ontology coverage analysis.
    """
    model_config = ConfigDict(frozen=True)

    total_taxonomy_nodes: int = Field(default=0, ge=0, description="Total number of taxonomy nodes defined in AUAO.")
    covered_taxonomy_nodes_count: int = Field(default=0, ge=0, description="Number of taxonomy nodes represented in the corpus.")
    coverage_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of ontology covered.")
    root_class_coverage: Dict[str, int] = Field(default_factory=dict, description="Record count per root attack domain (AUAO-RC-*).")
    represented_taxonomy_nodes: List[str] = Field(default_factory=list, description="List of taxonomy node IDs present in corpus.")
    uncovered_taxonomy_nodes: List[str] = Field(default_factory=list, description="List of taxonomy node IDs not yet represented.")
    covered_leaf_nodes: List[str] = Field(default_factory=list, description="List of leaf taxonomy nodes present.")
    uncovered_leaf_nodes: List[str] = Field(default_factory=list, description="List of leaf taxonomy nodes unrepresented.")
    depth_histogram: Dict[int, int] = Field(default_factory=dict, description="Count of represented nodes by taxonomy tree depth.")
    dataset_contribution_per_root_class: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Dataset record count matrix per root class.")


class OntologyCoverageAnalyzer:
    """
    Analyzer evaluating corpus representation against the AUAO v1.0 Universal Attack Ontology taxonomy tree.
    Reads ontology definitions from ontology/root_classes.json and ontology/attack_taxonomy.json,
    and streams Data Lake records without loading complete datasets into RAM.
    """

    def __init__(
        self,
        ontology_dir: str = "ontology",
        registry: Optional[CorpusRegistry] = None,
        calculator: Optional[CorpusStatisticsCalculator] = None
    ):
        self.ontology_dir = Path(ontology_dir)
        self.registry = registry or CorpusRegistry()
        self.calculator = calculator or CorpusStatisticsCalculator(registry=self.registry)

        self.root_classes = self._load_root_classes()
        self.taxonomy_nodes = self._load_attack_taxonomy()

    def _load_root_classes(self) -> Dict[str, Dict[str, Any]]:
        path = self.ontology_dir / "root_classes.json"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                items = data.get("root_classes", data.get("nodes", []))
                return {rc["id"]: rc for rc in items if isinstance(rc, dict) and "id" in rc}
            elif isinstance(data, list):
                return {rc["id"]: rc for rc in data if isinstance(rc, dict) and "id" in rc}
            return {}

    def _load_attack_taxonomy(self) -> Dict[str, Dict[str, Any]]:
        path = self.ontology_dir / "attack_taxonomy.json"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                items = data.get("nodes", data.get("taxonomy", []))
                return {node["id"]: node for node in items if isinstance(node, dict) and "id" in node}
            elif isinstance(data, list):
                return {node["id"]: node for node in data if isinstance(node, dict) and "id" in node}
            return {}

    def analyze(self) -> OntologyCoverageReport:
        """
        Streams Data Lake partition files and calculates complete AUAO ontology coverage metrics.
        
        Returns:
            OntologyCoverageReport: Comprehensive coverage analysis report.
        """
        discovered_partitions = self.registry.discover_partitions()
        represented_nodes_set: Set[str] = set()
        root_class_counts: Dict[str, int] = {rc_id: 0 for rc_id in self.root_classes}
        dataset_root_matrix: Dict[str, Dict[str, int]] = {}

        # Stream records line by line
        for part in discovered_partitions:
            source_id = part.source_id
            if source_id not in dataset_root_matrix:
                dataset_root_matrix[source_id] = {rc_id: 0 for rc_id in self.root_classes}

            for rec in self.calculator.stream_records(part.partition_path):
                tax_node = str(rec.get("taxonomy_node", ""))
                if tax_node:
                    represented_nodes_set.add(tax_node)

                    # Determine root class mapping
                    root_id = self._resolve_root_class(tax_node)
                    if root_id:
                        root_class_counts[root_id] = root_class_counts.get(root_id, 0) + 1
                        dataset_root_matrix[source_id][root_id] = dataset_root_matrix[source_id].get(root_id, 0) + 1

        all_node_ids = set(self.taxonomy_nodes.keys())
        total_nodes = len(all_node_ids)

        represented_list = sorted(list(represented_nodes_set.intersection(all_node_ids)))
        uncovered_list = sorted(list(all_node_ids - represented_nodes_set))

        # Leaf node analysis
        leaf_nodes = {nid: node for nid, node in self.taxonomy_nodes.items() if node.get("is_leaf", False)}
        covered_leaves = sorted([nid for nid in leaf_nodes if nid in represented_nodes_set])
        uncovered_leaves = sorted([nid for nid in leaf_nodes if nid not in represented_nodes_set])

        # Depth histogram
        depth_hist: Dict[int, int] = {}
        for nid in represented_list:
            node = self.taxonomy_nodes.get(nid, {})
            depth = int(node.get("depth", 0))
            depth_hist[depth] = depth_hist.get(depth, 0) + 1

        coverage_pct = round((len(represented_list) / total_nodes * 100.0), 2) if total_nodes > 0 else 0.0

        return OntologyCoverageReport(
            total_taxonomy_nodes=total_nodes,
            covered_taxonomy_nodes_count=len(represented_list),
            coverage_percentage=coverage_pct,
            root_class_coverage=root_class_counts,
            represented_taxonomy_nodes=represented_list,
            uncovered_taxonomy_nodes=uncovered_list,
            covered_leaf_nodes=covered_leaves,
            uncovered_leaf_nodes=uncovered_leaves,
            depth_histogram=depth_hist,
            dataset_contribution_per_root_class=dataset_root_matrix
        )

    def _resolve_root_class(self, taxonomy_node_id: str) -> Optional[str]:
        """
        Resolves the root class ID for a given taxonomy node ID.
        """
        if taxonomy_node_id in self.root_classes:
            return taxonomy_node_id

        node = self.taxonomy_nodes.get(taxonomy_node_id)
        if not node:
            # Fallback prefix matching (e.g. AUAO-PI-DIR-RO -> AUAO-RC-01)
            prefix = taxonomy_node_id.split("-")[1] if "-" in taxonomy_node_id else ""
            prefix_map = {
                "PI": "AUAO-RC-01", "JB": "AUAO-RC-02", "LK": "AUAO-RC-03",
                "TL": "AUAO-RC-04", "MC": "AUAO-RC-05", "RG": "AUAO-RC-06",
                "MM": "AUAO-RC-10", "RC": "AUAO-RC-09"
            }
            return prefix_map.get(prefix)

        # Climb parent chain if available
        curr = node
        visited = set()
        while curr and curr.get("id") not in visited:
            visited.add(curr.get("id"))
            if curr.get("id") in self.root_classes:
                return curr.get("id")
            parent_id = curr.get("parent", curr.get("parent_id"))
            if not parent_id:
                break
            curr = self.taxonomy_nodes.get(parent_id)

        # Fallback to root_class property if present
        return node.get("root_class")

    def get_uncovered_nodes(self) -> List[str]:
        """
        Returns a list of unrepresented taxonomy node IDs.
        """
        return self.analyze().uncovered_taxonomy_nodes
