"""
Unit tests for Research Provenance Tracker, Reproducibility Manifest, and Artifact Hashes (Sprint 16.3).
"""

import os
import pytest
from research.models import BenchmarkRequest, ProvenanceRecord, ReproducibilityManifest
from research.provenance import ResearchProvenanceTracker


def test_provenance_tracker_capture(tmp_path):
    tracker = ResearchProvenanceTracker(provenance_dir=str(tmp_path))
    req = BenchmarkRequest(random_seed=123, max_attacks_per_dataset=3)
    provenance = tracker.capture_provenance(benchmark_id="bench_test_123", request=req)

    assert isinstance(provenance, ProvenanceRecord)
    assert provenance.benchmark_uuid == "bench_test_123"
    assert provenance.random_seed == 123
    assert provenance.git_commit_hash != ""
    assert "hackaprompt" in provenance.dataset_checksums
    assert os.path.exists(os.path.join(str(tmp_path), "benchmark_provenance.json"))


def test_reproducibility_manifest_generation(tmp_path):
    tracker = ResearchProvenanceTracker(provenance_dir=str(tmp_path))
    provenance = tracker.capture_provenance(benchmark_id="bench_repro_123")
    manifest = tracker.generate_reproducibility_manifest(provenance)

    assert isinstance(manifest, ReproducibilityManifest)
    assert manifest.manifest_id == "manifest_bench_repro_123"
    assert manifest.runtime_environment["python"] == provenance.python_version
    assert len(manifest.datasets) >= 7
    assert os.path.exists(os.path.join(str(tmp_path), "reproducibility_manifest.json"))


def test_artifact_hash_computation(tmp_path):
    tracker = ResearchProvenanceTracker(provenance_dir=str(tmp_path))
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    sample_file = reports_dir / "sample_report.md"
    sample_file.write_text("Scientific Research Provenance Test", encoding="utf-8")

    hashes = tracker.compute_artifact_hashes(search_dirs=[str(reports_dir)])
    assert len(hashes) == 1
    assert os.path.exists(os.path.join(str(tmp_path), "artifact_hashes.json"))
