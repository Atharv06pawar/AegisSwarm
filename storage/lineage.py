import json
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from pathlib import Path

def calculate_sha256(file_path: str) -> str:
    """
    Calculates the SHA256 checksum of a file.
    Reads in 4KB chunks to prevent high memory usage on large files.
    """
    sha256_hash = hashlib.sha256()
    path = Path(file_path)
    
    if not path.exists() or not path.is_file():
        return "FILE_NOT_FOUND"
        
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@dataclass
class LineageRecord:
    """
    Represents a single lineage tracking record for a processed dataset.
    """
    dataset_id: str
    dataset_version: str
    parser_version: str
    input_file: str
    input_sha256: str
    output_partitions: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    git_commit: Optional[str] = None

@dataclass
class ReproducibilityManifest:
    """
    A collection of LineageRecords representing an entire pipeline run.
    """
    manifest_id: str
    created_at: str
    records: List[LineageRecord] = field(default_factory=list)

    def add_record(self, record: LineageRecord) -> None:
        """Appends a new lineage record to the manifest."""
        self.records.append(record)

    def save(self, filepath: str) -> None:
        """Saves the manifest as an indented JSON file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=4)

class LineageTracker:
    """
    Handles tracking execution metadata to ensure total research reproducibility.
    """
    
    def __init__(self, manifest_dir: str = "metadata/manifests"):
        self.manifest_dir = Path(manifest_dir)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)
        
        manifest_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.manifest = ReproducibilityManifest(
            manifest_id=f"run_{manifest_id}",
            created_at=datetime.now(timezone.utc).isoformat()
        )

    def record_execution(
        self, 
        dataset_id: str, 
        dataset_version: str, 
        parser_version: str, 
        input_file: str, 
        output_partitions: List[str], 
        git_commit: Optional[str] = None
    ) -> None:
        """
        Records the successful parsing of a dataset.
        Automatically calculates the SHA256 checksum of the input file.
        """
        sha256_hash = calculate_sha256(input_file)
        
        record = LineageRecord(
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            parser_version=parser_version,
            input_file=input_file,
            input_sha256=sha256_hash,
            output_partitions=output_partitions,
            git_commit=git_commit
        )
        self.manifest.add_record(record)
        
    def save_manifest(self) -> str:
        """
        Flushes the tracked records to disk as a JSON manifest.
        
        Returns:
            str: The path to the saved manifest file.
        """
        filepath = self.manifest_dir / f"manifest_{self.manifest.manifest_id}.json"
        self.manifest.save(str(filepath))
        return str(filepath)
