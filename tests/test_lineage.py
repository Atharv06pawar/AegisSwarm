import os
import json
import pytest
from pathlib import Path
from storage.lineage import LineageTracker, calculate_sha256

def test_lineage_record_tracking(temp_manifest_dir, tmp_path):
    """Test tracking output partitions and generating lineage manifest."""
    input_file = tmp_path / "raw.jsonl"
    input_file.write_text('{"prompt":"test"}', encoding="utf-8")

    tracker = LineageTracker(manifest_dir=str(temp_manifest_dir))
    
    tracker.record_execution(
        dataset_id="test_ds",
        dataset_version="1.0.0",
        parser_version="1.0.0",
        input_file=str(input_file),
        output_partitions=["outputs/lake/source=test_ds/part-0.jsonl.gz"]
    )

    saved_path = tracker.save_manifest()
    assert os.path.exists(saved_path)

    # Verify manifest JSON
    with open(saved_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["manifest_id"].startswith("run_")
    assert len(manifest["records"]) == 1
    assert manifest["records"][0]["dataset_id"] == "test_ds"

def test_lineage_sha256_calculation(tmp_path):
    """Test 4KB chunked SHA256 file checksum calculation."""
    test_file = tmp_path / "data.txt"
    test_file.write_text("AegisSwarm Lineage Test Data", encoding="utf-8")

    digest = calculate_sha256(str(test_file))
    assert len(digest) == 64 # Hexadecimal SHA256 string
