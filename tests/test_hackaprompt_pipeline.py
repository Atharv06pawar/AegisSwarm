import os
import json
import gzip
import pytest
from pathlib import Path
from core.orchestrator import PipelineOrchestrator
from plugins.datasets.hackaprompt import HackAPromptPlugin
from storage.data_lake import JSONLBackend
from core.registry import PluginRegistry

def test_hackaprompt_end_to_end_pipeline(tmp_path):
    """
    End-to-end integration test verifying the complete HackAPrompt ingestion lifecycle:
    1. Plugin Discovery & Metadata validation
    2. Data fetching / parsing / normalization / custom validation
    3. Storage partitioning (JSONL.GZ)
    4. Lineage manifest generation & verification
    """
    # 1. Setup isolated workspace & Plugin Registry
    PluginRegistry.clear()
    PluginRegistry.register(HackAPromptPlugin)
    
    lake_dir = tmp_path / "lake"
    manifest_dir = tmp_path / "manifests"
    raw_dir = tmp_path / "raw" / "hackaprompt"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Write a test raw JSONL file
    raw_file = raw_dir / "dataset.jsonl"
    with open(raw_file, "w", encoding="utf-8") as f:
        f.write(json.dumps({"prompt": "Valid injection prompt", "level": 1, "expected": "foo", "model": "gpt-4"}) + "\n")
        f.write(json.dumps({"prompt": "", "level": 2, "expected": "bar", "model": "gpt-3.5"}) + "\n") # Corrupted record
    
    # Patch HackAPromptPlugin.fetch to point to our test raw_file
    orig_fetch = HackAPromptPlugin.fetch
    HackAPromptPlugin.fetch = lambda self: str(raw_file)
    
    try:
        # 2. Instantiate Orchestrator with isolated StorageBackend
        storage_backend = JSONLBackend(base_path=str(lake_dir), compression="gzip")
        orchestrator = PipelineOrchestrator(
            storage_backend=storage_backend,
            plugin_registry=PluginRegistry,
            batch_size=5
        )
        orchestrator.lineage_tracker.manifest_dir = manifest_dir
        manifest_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Execute Pipeline
        orchestrator.run_plugin("hackaprompt")
        
        # 4. Verify Execution Stats
        assert "hackaprompt" in orchestrator.stats
        assert orchestrator.stats["hackaprompt"]["records_processed"] == 1, "Should process 1 valid record and drop 1 corrupted"
        assert orchestrator.stats["hackaprompt"]["batches_written"] == 1
        
        # 5. Flush Lineage
        orchestrator.lineage_tracker.save_manifest()
        
        # 6. Verify Partition File Creation
        partition_dir = lake_dir / "source=hackaprompt"
        assert partition_dir.exists(), "Partition directory was not created"
        
        gz_files = list(partition_dir.glob("*.jsonl.gz"))
        assert len(gz_files) == 1, "Expected exactly 1 compressed partition file"
        
        # 7. Verify Data Content & AegisSwarm Schema Alignment
        with gzip.open(gz_files[0], "rt", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
            assert len(lines) == 1
            record = lines[0]
            assert "sample_id" in record
            assert record["dataset_metadata"]["dataset_id"] == "hackaprompt"
            assert record["taxonomy_node"] == "Direct Prompt Injection"
            assert len(record["turns"]) == 1
            
            msg = record["turns"][0]["messages"][0]
            assert msg["content"] == "Valid injection prompt"
            assert msg["is_injection_source"] is True
            
        # 8. Verify Lineage Generation
        manifests = list(manifest_dir.glob("*.json"))
        assert len(manifests) == 1, "Lineage manifest was not saved"
        
        with open(manifests[0], "r", encoding="utf-8") as f:
            manifest = json.load(f)
            assert len(manifest["records"]) >= 1, "Manifest should contain dataset record"

    finally:
        HackAPromptPlugin.fetch = orig_fetch
