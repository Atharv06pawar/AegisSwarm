import os
import pytest
from pathlib import Path
from corpus.registry import CorpusRegistry
from corpus.statistics import CorpusStatisticsCalculator
from corpus.coverage import OntologyCoverageAnalyzer
from corpus.quality import CorpusQualityAuditor
from corpus.verifier import CorpusIntegrityVerifier
from corpus.manifest import CorpusManifestHandler
from corpus.manager import CorpusManager
from storage.data_lake import JSONLBackend

def test_corpus_registry_discovery(temp_lake_dir, sample_attack_record):
    """Test CorpusRegistry partition discovery over isolated lake directory."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    summary = registry.get_summary()

    assert summary.total_datasets == 1
    assert summary.total_partitions == 1
    assert "ds1" in summary.dataset_ids

def test_corpus_statistics(temp_lake_dir, sample_attack_record):
    """Test CorpusStatisticsCalculator streaming statistics computation."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record, sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    calc = CorpusStatisticsCalculator(registry=registry)
    stats = calc.compute_statistics()

    assert stats.total_records == 2
    assert stats.record_distribution_per_dataset.get("ds1") == 2
    assert "AUAO-PI-DIR-RO-AUTH-SYS" in stats.taxonomy_distribution

def test_ontology_coverage_analyzer(temp_lake_dir, sample_attack_record):
    """Test OntologyCoverageAnalyzer taxonomy tree coverage computation."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    analyzer = OntologyCoverageAnalyzer(registry=registry)
    cov = analyzer.analyze()

    assert cov.total_taxonomy_nodes > 0
    assert "AUAO-PI-DIR-RO-AUTH-SYS" in cov.represented_taxonomy_nodes

def test_corpus_quality_auditor(temp_lake_dir, sample_attack_record):
    """Test CorpusQualityAuditor schema compliance and duplicate detection."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    auditor = CorpusQualityAuditor(registry=registry)
    quality = auditor.audit()

    assert quality.total_records_audited == 1
    assert quality.schema_compliance_rate in (1.0, 100.0)

def test_corpus_integrity_verifier(temp_lake_dir, sample_attack_record, tmp_path):
    """Test CorpusIntegrityVerifier checksum verification."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    written = backend.batch_write([sample_attack_record], partition_key="ds1")

    manifest_file = tmp_path / "lineage_manifest.json"
    manifest_file.write_text('{"manifest_version":"1.0.0","records":[]}', encoding="utf-8")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    verifier = CorpusIntegrityVerifier(manifest_path=str(manifest_file), registry=registry)
    ver = verifier.verify()

    assert ver.total_partitions_scanned == 1

def test_corpus_manager_facade(temp_lake_dir, sample_attack_record, tmp_path):
    """Test CorpusManager facade get_status and create_snapshot."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    backend.batch_write([sample_attack_record], partition_key="ds1")

    registry = CorpusRegistry(lake_base_path=str(temp_lake_dir))
    manager = CorpusManager(registry=registry)

    summary = manager.get_status()
    assert summary.total_datasets == 1

    snapshot_path = str(tmp_path / "snapshot.json")
    manifest = manager.create_snapshot(output_path=snapshot_path)
    assert manifest.manifest_version == "1.0.0"
    assert os.path.exists(snapshot_path)
