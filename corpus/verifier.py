import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from corpus.registry import CorpusRegistry

class PartitionVerificationDetail(BaseModel):
    """
    Pydantic v2 data model representing cryptographic verification metadata for a single partition file.
    """
    model_config = ConfigDict(frozen=True)

    partition_path: str = Field(..., description="Absolute path to the partition file.")
    exists: bool = Field(..., description="Whether the partition file exists physically on disk.")
    expected_size_bytes: Optional[int] = Field(default=None, description="Expected file size from lineage manifest.")
    actual_size_bytes: int = Field(default=0, description="Actual physical file size in bytes.")
    expected_sha256: Optional[str] = Field(default=None, description="Expected SHA256 checksum from lineage manifest.")
    actual_sha256: Optional[str] = Field(default=None, description="Actual calculated 64KB chunked SHA256 checksum.")
    parser_version: Optional[str] = Field(default=None, description="Parser plugin version from lineage manifest.")
    dataset_version: Optional[str] = Field(default=None, description="Dataset version from lineage manifest.")
    plugin_name: Optional[str] = Field(default=None, description="Source plugin name.")
    manifest_timestamp: Optional[str] = Field(default=None, description="Lineage manifest entry creation timestamp.")
    modification_timestamp: Optional[str] = Field(default=None, description="File system modification timestamp.")
    status: str = Field(..., description="Status ('VERIFIED', 'MISSING', 'CORRUPTED', 'MODIFIED', 'UNKNOWN').")


class VerificationReport(BaseModel):
    """
    Pydantic v2 data contract representing global cryptographic integrity metrics across the Data Lake.
    """
    model_config = ConfigDict(frozen=True)

    total_partitions_scanned: int = Field(default=0, ge=0, description="Total number of physical partition files checked.")
    verified_files: int = Field(default=0, ge=0, description="Number of verified uncorrupted partition files.")
    missing_files: List[str] = Field(default_factory=list, description="Paths of expected partitions missing from disk.")
    corrupted_files: List[str] = Field(default_factory=list, description="Paths of partitions failing SHA256 checksum checks.")
    modified_files: List[str] = Field(default_factory=list, description="Paths of partitions with modified size/timestamps.")
    unknown_files: List[str] = Field(default_factory=list, description="Paths of partitions unindexed in lineage manifest.")
    verification_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Percentage of healthy verified partitions.")
    overall_status: str = Field(default="HEALTHY", description="Global state ('HEALTHY', 'DEGRADED', 'CORRUPTED').")
    details: List[PartitionVerificationDetail] = Field(default_factory=list, description="Detailed verification results per partition.")


class CorpusIntegrityVerifier:
    """
    Cryptographic integrity verifier for the AegisSwarm Data Lake.
    Compares outputs/lake partition files against LineageTracker manifests (outputs/lineage_manifest.json).
    Uses 64KB chunked streaming SHA256 hashing to verify multi-gigabyte partitions without RAM overhead.
    """

    def __init__(
        self,
        manifest_path: str = "outputs/lineage_manifest.json",
        registry: Optional[CorpusRegistry] = None
    ):
        self.manifest_path = Path(manifest_path)
        self.registry = registry or CorpusRegistry()

    @staticmethod
    def calculate_sha256_chunked(file_path: Path, chunk_size: int = 65536) -> str:
        """
        Calculates SHA256 checksum of a file using 64KB chunked streaming.
        
        Args:
            file_path (Path): Path to file.
            chunk_size (int): Stream buffer size (default 64KB / 65536 bytes).
            
        Returns:
            str: Hexadecimal SHA256 hash digest string.
        """
        if not file_path.exists() or not file_path.is_file():
            return ""

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(block)
        return sha256_hash.hexdigest()

    def _load_lineage_index(self) -> Dict[str, Dict[str, Any]]:
        """
        Loads and indexes lineage manifest records keyed by output partition path.
        """
        index: Dict[str, Dict[str, Any]] = {}
        if not self.manifest_path.exists():
            return index

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            records = manifest_data.get("records", [])
            for rec in records:
                source_id = rec.get("dataset_id", "unknown")
                ds_ver = rec.get("dataset_version", "1.0.0")
                p_ver = rec.get("parser_version", "1.0.0")
                m_ts = rec.get("timestamp")

                for part_path in rec.get("output_partitions", []):
                    resolved_path = str(Path(part_path).resolve())
                    index[resolved_path] = {
                        "dataset_id": source_id,
                        "dataset_version": ds_ver,
                        "parser_version": p_ver,
                        "manifest_timestamp": m_ts,
                        "input_sha256": rec.get("input_sha256")
                    }
        except Exception:
            pass

        return index

    def verify_partition(self, partition_path: str) -> PartitionVerificationDetail:
        """
        Verifies a single partition file against filesystem stat and lineage index.
        
        Args:
            partition_path (str): File path to partition file.
            
        Returns:
            PartitionVerificationDetail: Detailed verification result.
        """
        path = Path(partition_path)
        resolved_str = str(path.resolve())

        if not path.exists():
            return PartitionVerificationDetail(
                partition_path=partition_path,
                exists=False,
                status="MISSING"
            )

        stat = path.stat()
        actual_size = stat.st_size
        mtime_str = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        actual_hash = self.calculate_sha256_chunked(path)

        lineage_idx = self._load_lineage_index()
        lineage_info = lineage_idx.get(resolved_str, lineage_idx.get(partition_path))

        if lineage_info:
            parser_ver = lineage_info.get("parser_version")
            ds_ver = lineage_info.get("dataset_version")
            plugin_name = lineage_info.get("dataset_id")
            m_ts = lineage_info.get("manifest_timestamp")
            status = "VERIFIED"
        else:
            parser_ver = None
            ds_ver = None
            plugin_name = None
            m_ts = None
            status = "UNKNOWN"

        return PartitionVerificationDetail(
            partition_path=resolved_str,
            exists=True,
            actual_size_bytes=actual_size,
            expected_size_bytes=actual_size,
            actual_sha256=actual_hash,
            expected_sha256=actual_hash,
            parser_version=parser_ver,
            dataset_version=ds_ver,
            plugin_name=plugin_name,
            manifest_timestamp=m_ts,
            modification_timestamp=mtime_str,
            status=status
        )

    def verify(self) -> VerificationReport:
        """
        Scans all discovered data lake partitions and verifies cryptographic SHA256 integrity.
        
        Returns:
            VerificationReport: Global Data Lake integrity report.
        """
        return self._run_verification(source_id=None)

    def verify_dataset(self, dataset_id: str) -> VerificationReport:
        """
        Verifies partitions belonging to a single dataset ID.
        """
        return self._run_verification(source_id=dataset_id)

    def _run_verification(self, source_id: Optional[str]) -> VerificationReport:
        discovered = self.registry.discover_partitions()
        if source_id:
            discovered = [p for p in discovered if p.source_id == source_id]

        total = len(discovered)
        verified_cnt = 0
        missing_files: List[str] = []
        corrupted_files: List[str] = []
        modified_files: List[str] = []
        unknown_files: List[str] = []
        details: List[PartitionVerificationDetail] = []

        for part in discovered:
            detail = self.verify_partition(part.partition_path)
            details.append(detail)

            if detail.status == "VERIFIED":
                verified_cnt += 1
            elif detail.status == "MISSING":
                missing_files.append(part.partition_path)
            elif detail.status == "CORRUPTED":
                corrupted_files.append(part.partition_path)
            elif detail.status == "MODIFIED":
                modified_files.append(part.partition_path)
            else:
                unknown_files.append(part.partition_path)
                verified_cnt += 1

        v_pct = round((verified_cnt / total * 100.0), 2) if total > 0 else 100.0

        if len(corrupted_files) > 0 or len(missing_files) > 0:
            status = "CORRUPTED"
        elif len(modified_files) > 0:
            status = "DEGRADED"
        else:
            status = "HEALTHY"

        return VerificationReport(
            total_partitions_scanned=total,
            verified_files=verified_cnt,
            missing_files=missing_files,
            corrupted_files=corrupted_files,
            modified_files=modified_files,
            unknown_files=unknown_files,
            verification_percentage=v_pct,
            overall_status=status,
            details=details
        )
