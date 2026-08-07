import json
from pathlib import Path

def verify_phase1():
    root_file = Path("ontology/root_classes.json")
    tax_file = Path("ontology/attack_taxonomy.json")
    rel_file = Path("ontology/relationships.json")

    with open(root_file, "r", encoding="utf-8") as f:
        roots_data = json.load(f)["root_classes"]

    with open(tax_file, "r", encoding="utf-8") as f:
        tax_nodes = json.load(f)["nodes"]

    with open(rel_file, "r", encoding="utf-8") as f:
        rel_data = json.load(f)

    # Collect IDs
    root_ids = {r["id"] for r in roots_data}
    tax_ids = {t["id"] for t in tax_nodes}

    print(f"Total Root Classes: {len(root_ids)}")
    print(f"Total Taxonomy Nodes: {len(tax_ids)}")

    # 1. Uniqueness
    assert len(tax_nodes) == len(tax_ids), "Duplicate node IDs found in attack_taxonomy.json!"

    # 2. Every root class must exist in taxonomy
    for r_id in root_ids:
        assert r_id in tax_ids, f"Root class {r_id} missing from attack_taxonomy.json!"

    # 3. Check Parent-Child consistency
    node_dict = {t["id"]: t for t in tax_nodes}

    for n in tax_nodes:
        # Check parent
        p_id = n["parent"]
        if p_id is not None:
            assert p_id in node_dict, f"Node {n['id']} references invalid parent {p_id}"
            assert n["id"] in node_dict[p_id]["children"], f"Parent {p_id} does not list child {n['id']}"

        # Check children
        for c_id in n["children"]:
            assert c_id in node_dict, f"Node {n['id']} lists invalid child {c_id}"
            assert node_dict[c_id]["parent"] == n["id"], f"Child {c_id} parent does not match {n['id']}"

    # 4. Check Relationship node references
    edges = rel_data["graph_edges"]
    for edge in edges:
        s_id = edge["source_id"]
        # Source must be a valid attack node ID
        assert s_id in node_dict, f"Relationship source {s_id} is not a valid taxonomy node!"

    print("ALL PHASE 1 ONTOLOGY CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    verify_phase1()
