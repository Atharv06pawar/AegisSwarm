import os
import json
import uuid
import tempfile
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pd = None

from core.schema import AttackRecord

logger = logging.getLogger(__name__)

class StorageBackend(ABC):
    """
    Abstract interface for AegisSwarm Data Lake storage backends.
    Defines the contract for batch writes, partitioning, compression, and atomic operations.
    """
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_partition_dir(self, partition_key: str) -> Path:
        """
        Determines the partitioned directory path (e.g., source=hackaprompt)
        and creates it if it does not exist.
        """
        partition_dir = self.base_path / f"source={partition_key}"
        partition_dir.mkdir(parents=True, exist_ok=True)
        return partition_dir

    @abstractmethod
    def batch_write(self, records: List[AttackRecord], partition_key: str) -> str:
        """
        Atomically writes a batch of records to the data lake.
        
        Args:
            records (List[AttackRecord]): The validated records to write.
            partition_key (str): The dataset source ID to partition by.
            
        Returns:
            str: The final written file path.
        """
        pass


class JSONLBackend(StorageBackend):
    """
    JSON Lines storage backend. 
    Ideal for human readability, git-diffing small sets, and streaming compatibility.
    """
    
    def __init__(self, base_path: str, compression: Optional[str] = "gzip"):
        """
        Args:
            base_path (str): The root directory of the data lake.
            compression (str): Compression algorithm ('gzip', 'bz2', 'zip', 'xz', or None).
        """
        super().__init__(base_path)
        self.compression = compression

    def batch_write(self, records: List[AttackRecord], partition_key: str) -> str:
        if not records:
            return ""
            
        partition_dir = self._get_partition_dir(partition_key)
        file_id = uuid.uuid4().hex[:8]
        
        ext = "jsonl"
        if self.compression == "gzip":
            ext = "jsonl.gz"
        elif self.compression:
            ext = f"jsonl.{self.compression}"
            
        final_path = partition_dir / f"part-{file_id}.{ext}"
        
        # Serialize Pydantic models to JSON-safe dictionaries
        dicts = [r.model_dump(mode='json') for r in records]
        
        # Create a temporary file in the same partition directory for atomic move
        fd, tmp_path = tempfile.mkstemp(dir=partition_dir, suffix=".tmp")
        os.close(fd)
        
        try:
            if pd is not None:
                # Leverage Pandas for robust I/O and native compression handling
                df = pd.DataFrame(dicts)
                df.to_json(tmp_path, orient="records", lines=True, compression=self.compression)
            else:
                # Fallback implementation if Pandas is not installed
                import gzip
                open_func = gzip.open if self.compression == "gzip" else open
                mode = 'wt' if self.compression == "gzip" else 'w'
                with open_func(tmp_path, mode, encoding='utf-8') as f:
                    for d in dicts:
                        f.write(json.dumps(d) + "\n")
                        
            # Atomic POSIX rename (os.replace works safely across platforms for same-filesystem moves)
            os.replace(tmp_path, final_path)
            logger.debug(f"JSONLBackend: Atomically wrote {len(records)} records to {final_path}")
            
        except Exception as e:
            # Cleanup temp file on failure
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            logger.error(f"Failed to write batch to JSONL: {e}")
            raise e
            
        return str(final_path)


class ParquetBackend(StorageBackend):
    """
    Parquet storage backend.
    Highly optimized for columnar analytics, compression, and seamless schema evolution.
    """
    
    def __init__(self, base_path: str, compression: str = "snappy"):
        """
        Args:
            base_path (str): The root directory of the data lake.
            compression (str): Compression algorithm (default 'snappy', alternatives 'gzip', 'brotli').
        """
        super().__init__(base_path)
        self.compression = compression

    def batch_write(self, records: List[AttackRecord], partition_key: str) -> str:
        if not records:
            return ""
            
        if pd is None:
            raise ImportError("Pandas and PyArrow are required to use the ParquetBackend.")
            
        partition_dir = self._get_partition_dir(partition_key)
        file_id = uuid.uuid4().hex[:8]
        final_path = partition_dir / f"part-{file_id}.parquet"
        
        # Serialize Pydantic models to JSON-safe dictionaries before loading to dataframe
        # This resolves complex types (datetime, UUID) that parquet/pandas might struggle with directly
        dicts = [r.model_dump(mode='json') for r in records]
        df = pd.DataFrame(dicts)
        
        # Atomic write via temporary file
        fd, tmp_path = tempfile.mkstemp(dir=partition_dir, suffix=".tmp")
        os.close(fd)
        
        try:
            # Parquet natively supports schema evolution. 
            # If a new plugin adds extra fields to 'dataset_metadata', writing it to a 
            # new partitioned part file is perfectly valid. The query engine (PyArrow Dataset/DuckDB) 
            # will unify the schema upon read.
            df.to_parquet(
                tmp_path, 
                engine="pyarrow", 
                compression=self.compression, 
                index=False
            )
            
            # Atomic swap
            os.replace(tmp_path, final_path)
            logger.debug(f"ParquetBackend: Atomically wrote {len(records)} records to {final_path}")
            
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            logger.error(f"Failed to write batch to Parquet: {e}")
            raise e
            
        return str(final_path)
