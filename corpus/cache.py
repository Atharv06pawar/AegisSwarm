import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

class CacheEntry(BaseModel):
    """
    Data model representing a single cached statistics entry for a partition file.
    """
    model_config = ConfigDict(frozen=True)

    partition_path: str = Field(..., description="Absolute path to partition file.")
    mtime: float = Field(..., description="File modification timestamp (mtime).")
    size_bytes: int = Field(..., ge=0, description="File size in bytes.")
    stats: Dict[str, Any] = Field(..., description="Computed statistics dictionary for the partition.")
    timestamp: str = Field(..., description="UTC ISO timestamp when cache entry was created.")


class CorpusCache:
    """
    Disk-backed cache manager for partition-level statistics.
    Persists data at outputs/corpus_cache.json and automatically invalidates entries
    when file mtime or file size changes.
    """

    def __init__(self, cache_file: str = "outputs/corpus_cache.json"):
        self.cache_file = Path(cache_file)
        self.entries: Dict[str, CacheEntry] = {}
        self.load()

    def load(self) -> None:
        """
        Loads cached partition entries from outputs/corpus_cache.json.
        """
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for path_key, entry_dict in data.items():
                        self.entries[path_key] = CacheEntry.model_validate(entry_dict)
            except Exception:
                # If cache is corrupted, reset gracefully
                self.entries = {}

    def save(self) -> None:
        """
        Persists cached entries to outputs/corpus_cache.json.
        """
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        serialized_data = {k: v.model_dump() for k, v in self.entries.items()}
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(serialized_data, f, indent=2)

    def get(self, partition_path: str, mtime: float, size_bytes: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached statistics for a partition file if mtime and size match.
        Automatically invalidates stale cache entries.
        """
        entry = self.entries.get(partition_path)
        if entry:
            if entry.mtime == mtime and entry.size_bytes == size_bytes:
                return entry.stats
            else:
                # File modified or resized; invalidate entry
                self.invalidate(partition_path)
        return None

    def put(self, partition_path: str, mtime: float, size_bytes: int, stats: Dict[str, Any]) -> None:
        """
        Stores computed statistics for a partition file into the cache.
        """
        self.entries[partition_path] = CacheEntry(
            partition_path=partition_path,
            mtime=mtime,
            size_bytes=size_bytes,
            stats=stats,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self.save()

    def invalidate(self, partition_path: str) -> None:
        """
        Removes a specific partition entry from the cache.
        """
        if partition_path in self.entries:
            del self.entries[partition_path]
            self.save()

    def clear(self) -> None:
        """
        Clears all cached entries and deletes the cache file.
        """
        self.entries.clear()
        if self.cache_file.exists():
            self.cache_file.unlink(missing_ok=True)
