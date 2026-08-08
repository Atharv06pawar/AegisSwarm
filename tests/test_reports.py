import os
import json
import pytest
from pathlib import Path
from corpus.reporter import CorpusReporter
from corpus.registry import CorpusRegistry
from storage.data_lake import JSONLBackend

def test_corpus_reporter_json(temp_lake_dir, sample_attack_record):
    """Test CorpusReporter generate_json dictionary generation."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    reporter = CorpusReporter(registry=registry)
    data = reporter.generate_json()

    assert "generation_timestamp" in data
    assert "corpus_summary" in data
    assert "statistics" in data
    assert "coverage" in data

def test_corpus_reporter_markdown(temp_lake_dir, sample_attack_record):
    """Test CorpusReporter generate_markdown whitepaper formatting."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    reporter = CorpusReporter(registry=registry)
    md = reporter.generate_markdown()

    assert "# AegisSwarm Universal AI Attack Corpus Research Whitepaper" in md
    assert "Executive Summary" in md
    assert "Dataset Inventory" in md

def test_corpus_reporter_export(temp_lake_dir, sample_attack_record, tmp_path):
    """Test CorpusReporter export writing both corpus_report.md and corpus_report.json."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    reporter = CorpusReporter(registry=registry)
    
    out_dir = tmp_path / "reports"
    paths = reporter.export(output_dir=str(out_dir))

    assert "json" in paths
    assert "markdown" in paths
    assert os.path.exists(paths["json"])
    assert os.path.exists(paths["markdown"])
