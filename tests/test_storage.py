import os
import gzip
import json
import pytest
from pathlib import Path
from storage.data_lake import JSONLBackend, ParquetBackend

def test_jsonl_backend_write(temp_lake_dir, sample_attack_record):
    """Test JSONLBackend batch writing and compressed partition file creation."""
    backend = JSONLBackend(base_path=str(temp_lake_dir), compression="gzip")
    
    written_path = backend.batch_write([sample_attack_record], partition_key="test_ds")
    assert written_path is not None
    assert os.path.exists(written_path)
    assert written_path.endswith(".jsonl.gz")
    assert "source=test_ds" in written_path

    # Verify contents can be uncompressed and read
    with gzip.open(written_path, "rt", encoding="utf-8") as f:
        line = f.readline().strip()
        data = json.loads(line)
        assert data["taxonomy_node"] == "AUAO-PI-DIR-RO-AUTH-SYS"

def test_jsonl_backend_uncompressed(temp_lake_dir, sample_attack_record):
    """Test uncompressed JSONLBackend batch writing."""
    backend = JSONLBackend(base_path=str(temp_lake_dir), compression=None)
    
    written_path = backend.batch_write([sample_attack_record], partition_key="test_ds")
    assert written_path is not None
    assert os.path.exists(written_path)
    assert written_path.endswith(".jsonl")

    with open(written_path, "r", encoding="utf-8") as f:
        data = json.loads(f.readline())
        assert data["taxonomy_node"] == "AUAO-PI-DIR-RO-AUTH-SYS"

def test_parquet_backend_write(temp_lake_dir, sample_attack_record):
    """Test ParquetBackend batch writing if pandas/pyarrow is installed."""
    try:
        backend = ParquetBackend(base_path=str(temp_lake_dir))
        written_path = backend.batch_write([sample_attack_record], partition_key="parquet_ds")
        assert written_path is not None
        assert os.path.exists(written_path)
        assert written_path.endswith(".parquet")
    except ImportError:
        pytest.skip("Pandas/pyarrow not installed for ParquetBackend test")

def test_empty_batch_write(temp_lake_dir):
    """Test that writing an empty list of records returns empty or handles gracefully."""
    backend = JSONLBackend(base_path=str(temp_lake_dir))
    written = backend.batch_write([], partition_key="empty_ds")
    assert written == "" or written is None
