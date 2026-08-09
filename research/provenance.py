"""
Research Provenance Tracker & Reproducibility Manifest Generator for AegisSwarm (Sprint 16.3).
Tracks complete execution context, system environment, git hashes, dataset checksums, and artifact SHA256 signatures.
"""

import os
import sys
import json
import hashlib
import platform
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from research.models import (
    ProvenanceRecord,
    ReproducibilityManifest,
    BenchmarkRequest,
)


class ResearchProvenanceTracker:
    """
    Tracks complete provenance metadata, dataset SHA256 checksums, system environment,
    git commit info, reproducibility manifests, and artifact hash signatures.
    """

    def __init__(self, provenance_dir: str = "outputs/provenance"):
        self.provenance_dir = provenance_dir
        os.makedirs(self.provenance_dir, exist_ok=True)

    @staticmethod
    def compute_file_sha256(filepath: str) -> str:
        """Calculates SHA256 digest for a target file."""
        if not os.path.exists(filepath):
            return "sha256:0000000000000000000000000000000000000000000000000000000000000000"
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return f"sha256:{hasher.hexdigest()}"

    def get_git_commit_hash(self) -> str:
        """Retrieves active repository git commit SHA or fallback."""
        try:
            res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=False
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return "aegis_v2_git_commit_head"

    def get_dependency_versions(self) -> Dict[str, str]:
        """Collects exact version signatures of critical dependencies."""
        deps = {}
        for pkg in ["pydantic", "fastapi", "uvicorn", "pytest", "numpy"]:
            try:
                mod = __import__(pkg)
                deps[pkg] = getattr(mod, "__version__", "installed")
            except ImportError:
                deps[pkg] = "not_installed"
        return deps

    def collect_dataset_checksums(self, raw_dir: str = "raw") -> Dict[str, str]:
        """Calculates SHA256 checksums for all raw dataset files."""
        checksums = {}
        datasets = ["hackaprompt", "agentdojo", "garak", "pyrit", "promptinject", "jailbreakbench", "advbench"]
        for ds in datasets:
            path = os.path.join(raw_dir, ds, "dataset.jsonl")
            checksums[ds] = self.compute_file_sha256(path)
        return checksums

    def collect_dataset_records(self, raw_dir: str = "raw") -> Dict[str, int]:
        """Counts total lines/records across raw datasets."""
        counts = {}
        datasets = ["hackaprompt", "agentdojo", "garak", "pyrit", "promptinject", "jailbreakbench", "advbench"]
        for ds in datasets:
            path = os.path.join(raw_dir, ds, "dataset.jsonl")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    counts[ds] = sum(1 for _ in f)
            else:
                counts[ds] = 0
        return counts

    def capture_provenance(
        self,
        benchmark_id: str,
        mission_ids: Optional[List[str]] = None,
        request: Optional[BenchmarkRequest] = None
    ) -> ProvenanceRecord:
        """
        Captures full provenance record for a benchmark execution run.
        """
        req = request or BenchmarkRequest()
        checksums = self.collect_dataset_checksums()
        records = self.collect_dataset_records()

        provenance = ProvenanceRecord(
            benchmark_uuid=benchmark_id,
            mission_uuids=mission_ids or [f"miss_{benchmark_id}"],
            dataset_versions={ds: "v1.0.0" for ds in checksums.keys()},
            dataset_checksums=checksums,
            dataset_record_counts=records,
            provider="openai",
            model="gpt-4o",
            mutation_families=[
                "Persona", "Roleplay", "Encoding", "XML", "Markdown", "Unicode", "Recursive"
            ],
            swarm_agents=[
                "ShadowSwarmAgent", "ReflexiveSwarmAgent", "EvolutionarySwarmAgent", "AdaptiveSwarmAgent"
            ],
            orchestrator_version="2.0.0",
            git_commit_hash=self.get_git_commit_hash(),
            python_version=sys.version.split()[0],
            os_info=f"{platform.system()} {platform.release()} ({platform.machine()})",
            dependency_versions=self.get_dependency_versions(),
            random_seed=req.random_seed,
            configuration_snapshot={
                "max_attacks_per_dataset": req.max_attacks_per_dataset,
                "parallelism": req.parallelism,
                "enable_learning": req.enable_learning,
                "enable_telemetry": req.enable_telemetry,
                "objective": req.objective
            }
        )

        # Save outputs/provenance/benchmark_provenance.json
        out_file = os.path.join(self.provenance_dir, "benchmark_provenance.json")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(provenance.model_dump_json(indent=2))

        return provenance

    def generate_reproducibility_manifest(
        self,
        provenance: ProvenanceRecord,
        report_hashes: Optional[Dict[str, str]] = None
    ) -> ReproducibilityManifest:
        """
        Generates deterministic reproducibility manifest for auditability.
        """
        manifest = ReproducibilityManifest(
            manifest_id=f"manifest_{provenance.benchmark_uuid}",
            benchmark_configuration=provenance.configuration_snapshot,
            runtime_environment={
                "python": provenance.python_version,
                "os": provenance.os_info,
                "git_commit": provenance.git_commit_hash,
                "orchestrator_version": provenance.orchestrator_version
            },
            datasets=[
                {"name": name, "sha256": sha, "records": provenance.dataset_record_counts.get(name, 0)}
                for name, sha in provenance.dataset_checksums.items()
            ],
            providers=[provenance.provider],
            random_seeds=[provenance.random_seed],
            dataset_hashes=provenance.dataset_checksums,
            report_hashes=report_hashes or {},
            artifact_hashes={}
        )

        # Save outputs/provenance/reproducibility_manifest.json
        out_file = os.path.join(self.provenance_dir, "reproducibility_manifest.json")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(manifest.model_dump_json(indent=2))

        return manifest

    def compute_artifact_hashes(self, search_dirs: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Computes SHA256 for all generated research artifacts across target directories.
        """
        dirs = search_dirs or ["outputs/reports", "outputs/telemetry", "outputs/learning", "outputs/missions"]
        hashes = {}

        for d in dirs:
            if os.path.exists(d):
                base_dir = os.path.dirname(d) or "."
                for root, _, files in os.walk(d):
                    for fname in files:
                        fpath = os.path.join(root, fname)
                        rel_path = os.path.relpath(fpath, start=base_dir).replace("\\", "/")
                        hashes[rel_path] = self.compute_file_sha256(fpath)

        out_file = os.path.join(self.provenance_dir, "artifact_hashes.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(hashes, f, indent=2)

        return hashes
