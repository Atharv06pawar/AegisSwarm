import json

def verify():
    with open("ontology/attack_properties.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    groups = data["property_groups"]
    total_props = 0
    prop_ids = set()
    prop_names = set()

    for g in groups:
        g_name = g["group_name"]
        props = g["properties"]
        print(f"Group '{g_name}': {len(props)} properties")
        for p in props:
            p_id = p["id"]
            p_name = p["canonical_name"]
            
            assert p_id not in prop_ids, f"Duplicate property ID: {p_id}"
            assert p_name not in prop_names, f"Duplicate property canonical_name: {p_name}"
            
            prop_ids.add(p_id)
            prop_names.add(p_name)
            total_props += 1

    print(f"Total Property Groups: {len(groups)}")
    print(f"Total Unique Properties: {total_props}")
    print("PHASE 2 VALIDATION SUCCESSFUL!")

if __name__ == "__main__":
    verify()
