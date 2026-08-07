import os
import json
import pytest
from pathlib import Path

from core.registry import PluginRegistry
from core.orchestrator import PipelineOrchestrator
from storage.data_lake import JSONLBackend
from plugins.datasets.hackaprompt import HackAPromptPlugin

@pytest.fixture
def temp_workspace(tmp_path):
    """
    Creates a temporary workspace with mock raw data for end-to-end testing.
    """
    raw_dir = tmp_path / "raw" / "hackaprompt"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    mock_file = raw_dir / "dataset.jsonl"
    with open(mock_file, "w", encoding="utf-8") as f:
        # Valid record
        f.write(json.dumps({"prompt": "Valid injection prompt", "level": 1, "model": "gpt-3.5"}) + "\n")
        # Invalid record (empty prompt), should be dropped by plugin.validate()
        f.write(json.dumps({"prompt": "   ", "level": 2, "model": "gpt-4"}) + "\n") 
        # Valid record
        f.write(json.dumps({"prompt": "Another valid prompt", "level": 3, "model": "claude"}) + "\n")
        
    return tmp_path, mock_file

def test_hackaprompt_end_to_end_pipeline(temp_workspace, monkeypatch):
    """
    Verifies the entire ingestion pipeline end-to-end.
    Covers: Discovery, Fetching (Mocked), Parsing, Normalization, 
    Validation, Batching, Storage, and Lineage Tracking.
    """
    tmp_path, mock_file = temp_workspace
    
    # 1. Plugin Discovery
    registry = PluginRegistry()
    registry.clear() # Ensure clean state
    
    # Auto-discover plugins from the actual package
    registry.discover(package_path="plugins.datasets")
    assert "hackaprompt" in registry.list_plugins(), "Registry failed to discover hackaprompt plugin"

    # 2. Mock Network Fetching
    # We mock the fetch method to return our temporary mock file instead of trying to download.
    def mock_fetch(self):
        return str(mock_file)
    monkeypatch.setattr(HackAPromptPlugin, "fetch", mock_fetch)

    # 3. Setup Storage Backend
    lake_dir = tmp_path / "outputs" / "lake"
    # Use uncompressed JSONL to easily read it back during assertions
    storage_backend = JSONLBackend(base_path=str(lake_dir), compression=None) 

    # 4. Orchestrator Initialization
    orchestrator = PipelineOrchestrator(
        storage_backend=storage_backend,
        plugin_registry=registry,
        batch_size=2 # Very small batch size to test chunking mechanics
    )
    
    # Override lineage manifest directory to keep it in tmp_path
    orchestrator.lineage_tracker.manifest_dir = tmp_path / "metadata" / "manifests"
    orchestrator.lineage_tracker.manifest_dir.mkdir(parents=True, exist_ok=True)

    # 5. Run Pipeline
    stats = orchestrator.run_all()
    
    # 6. Verify Statistics Collection
    assert "hackaprompt" in stats
    dataset_stats = stats["hackaprompt"]
    
    # We provided 3 raw records, but 1 was empty space and should have been dropped.
    assert dataset_stats["records_processed"] == 2
    # With batch_size=2 and 2 valid records, it should write exactly 1 batch.
    assert dataset_stats["batches_written"] == 1 
    assert dataset_stats.get("errors", 0) == 0

    # 7. Verify Storage & Normalization
    partition_dir = lake_dir / "source=hackaprompt"
    assert partition_dir.exists(), "Partition directory was not created"
    
    part_files = list(partition_dir.glob("*.jsonl"))
    assert len(part_files) == 1, "Expected exactly 1 part file in the data lake"
    
    with open(part_files[0], "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 2, "Expected exactly 2 normalized records written"
        
        # Verify schema normalization on the first record
        record = json.loads(lines[0])
        assert "sample_id" in record
        assert record["dataset_metadata"]["dataset_id"] == "hackaprompt"
        assert record["taxonomy_node"] == "Direct Prompt Injection"
        assert len(record["turns"]) == 1
        
        msg = record["turns"][0]["messages"][0]
        assert msg["content"] == "Valid injection prompt"
        assert msg["is_injection_source"] is True

    # 8. Verify Lineage Generation
    manifests = list(orchestrator.lineage_tracker.manifest_dir.glob("*.json"))
    assert len(manifests) == 1, "Lineage manifest was not saved"
    
    with open(manifests[0], "r", encoding="utf-8") as f:
        manifest = json.load(f)
        assert len(manifest["records"]) == 1, "Manifest should contain exactly 1 dataset record"
        
        lineage_record = manifest["records"][0]
        assert lineage_record["dataset_id"] == "hackaprompt"
        assert lineage_record["input_file"] == str(mock_file)
        assert len(lineage_record["output_partitions"]) == 1
        
        # Validate that SHA256 was calculated correctly on the raw file
        assert lineage_record["input_sha256"] != "UNKNOWN_AT_PARSE_TIME"
        assert lineage_record["input_sha256"] != "FILE_NOT_FOUND"
        assert len(lineage_record["input_sha256"]) == 64 # Standard SHA256 length
