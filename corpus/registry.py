import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Set

from corpus.models import DatasetPartitionInfo, DatasetInfo, CorpusSummary

class CorpusRegistry:
    """
    Registry service responsible for discovering and indexing data lake partitions.
    Operates strictly on filesystem metadata without loading dataset contents into memory.
    """

    def __init__(self, lake_base_path: str = "outputs/lake"):
        self.lake_base_path = Path(lake_base_path)

    def discover_partitions(self) -> List[DatasetPartitionInfo]:
        """
        Scans the data lake base path (outputs/lake/source=*) and discovers physical partition files.
        
        Returns:
            List[DatasetPartitionInfo]: Discovered partition metadata objects.
        """
        partitions: List[DatasetPartitionInfo] = []

        if not self.lake_base_path.exists():
            return partitions

        # Iterate over source=... directories
        for entry in self.lake_base_path.iterdir():
            if entry.is_dir() and entry.name.startswith("source="):
                source_id = entry.name.split("source=", 1)[1]
                
                # Scan partition files within the directory
                for part_file in entry.iterdir():
                    if part_file.is_file() and not part_file.name.endswith(".tmp"):
                        partition_info = self._inspect_partition_file(part_file, source_id)
                        if partition_info:
                            partitions.append(partition_info)

        return partitions

    def _inspect_partition_file(self, file_path: Path, source_id: str) -> Optional[DatasetPartitionInfo]:
        """
        Inspects a physical file to extract format, compression, and file size metadata.
        """
        name = file_path.name.lower()

        if name.endswith(".jsonl.gz"):
            fmt = "jsonl.gz"
            compression = "gzip"
        elif name.endswith(".jsonl"):
            fmt = "jsonl"
            compression = None
        elif name.endswith(".parquet"):
            fmt = "parquet"
            compression = "snappy"
        elif name.endswith(".json"):
            fmt = "json"
            compression = None
        else:
            return None

        stat = file_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        return DatasetPartitionInfo(
            partition_path=str(file_path.resolve()),
            source_id=source_id,
            format=fmt,
            size_bytes=stat.st_size,
            record_count=0, # Estimated/Calculated by Statistics subsystem
            compression=compression,
            last_modified=mtime
        )

    def list_datasets(self) -> List[DatasetInfo]:
        """
        Aggregates discovered partition metadata into structured DatasetInfo entries per source ID.
        """
        all_partitions = self.discover_partitions()
        dataset_map: Dict[str, List[DatasetPartitionInfo]] = {}

        for part in all_partitions:
            dataset_map.setdefault(part.source_id, []).append(part)

        dataset_infos: List[DatasetInfo] = []
        for source_id, parts in dataset_map.items():
            total_size = sum(p.size_bytes for p in parts)
            unique_formats = list({p.format for p in parts})
            
            dataset_infos.append(
                DatasetInfo(
                    source_id=source_id,
                    partition_count=len(parts),
                    total_size_bytes=total_size,
                    formats=unique_formats,
                    partitions=parts
                )
            )

        return dataset_infos

    def get_dataset_info(self, source_id: str) -> Optional[DatasetInfo]:
        """
        Retrieves DatasetInfo for a specific dataset source ID.
        """
        datasets = self.list_datasets()
        for ds in datasets:
            if ds.source_id == source_id:
                return ds
        return None

    def get_summary(self) -> CorpusSummary:
        """
        Computes global high-level aggregate summary of the registered corpus.
        """
        datasets = self.list_datasets()
        total_partitions = sum(ds.partition_count for ds in datasets)
        total_bytes = sum(ds.total_size_bytes for ds in datasets)
        dataset_ids = [ds.source_id for ds in datasets]

        return CorpusSummary(
            total_datasets=len(datasets),
            total_partitions=total_partitions,
            total_size_bytes=total_bytes,
            dataset_ids=dataset_ids
        )
