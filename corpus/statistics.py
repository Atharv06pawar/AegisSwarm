import os
import gzip
import json
from pathlib import Path
from typing import Iterator, Dict, Any, List, Optional, Set
from pydantic import BaseModel, Field, ConfigDict

try:
    import pandas as pd
except ImportError:
    pd = None

from corpus.cache import CorpusCache
from corpus.registry import CorpusRegistry

class CorpusStatisticsReport(BaseModel):
    """
    Strongly typed Pydantic v2 model representing aggregated statistics for the AegisSwarm Corpus.
    """
    model_config = ConfigDict(frozen=True)

    total_records: int = Field(default=0, ge=0, description="Total AttackRecord count.")
    total_turns: int = Field(default=0, ge=0, description="Total ConversationTurn count.")
    total_messages: int = Field(default=0, ge=0, description="Total Message count.")
    average_turns_per_record: float = Field(default=0.0, ge=0.0, description="Average turns per record.")
    average_messages_per_record: float = Field(default=0.0, ge=0.0, description="Average messages per record.")
    average_prompt_length: float = Field(default=0.0, ge=0.0, description="Average injection prompt character length.")
    maximum_prompt_length: int = Field(default=0, ge=0, description="Maximum prompt character length.")
    minimum_prompt_length: int = Field(default=0, ge=0, description="Minimum prompt character length.")
    storage_size_bytes: int = Field(default=0, ge=0, description="Total raw uncompressed storage footprint.")
    compressed_size_bytes: int = Field(default=0, ge=0, description="Total compressed physical storage size.")
    record_distribution_per_dataset: Dict[str, int] = Field(default_factory=dict, description="Record count per dataset.")
    taxonomy_distribution: Dict[str, int] = Field(default_factory=dict, description="Count per AUAO taxonomy node.")
    difficulty_distribution: Dict[str, int] = Field(default_factory=dict, description="Count per difficulty level.")
    evaluation_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall attack success rate.")
    average_severity_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Average evaluation severity score.")
    unique_target_models: List[str] = Field(default_factory=list, description="List of unique evaluation target models.")
    dataset_sizes: Dict[str, int] = Field(default_factory=dict, description="Physical size in bytes per dataset.")


class CorpusStatisticsCalculator:
    """
    Streaming statistics calculator engine.
    Computes corpus-wide metrics incrementally across JSONL, JSONL.GZ, JSON, and Parquet data lake files
    without loading full datasets into memory.
    """

    def __init__(
        self, 
        registry: Optional[CorpusRegistry] = None,
        cache: Optional[CorpusCache] = None
    ):
        self.registry = registry or CorpusRegistry()
        self.cache = cache or CorpusCache()

    def stream_records(self, partition_path: str) -> Iterator[Dict[str, Any]]:
        """
        Memory-safe generator yielding dictionaries line-by-line from a data lake partition file.
        Supports .jsonl, .jsonl.gz, .json, and .parquet.
        """
        path = Path(partition_path)
        if not path.exists():
            raise FileNotFoundError(f"Partition file not found: {partition_path}")

        name = path.name.lower()

        if name.endswith(".jsonl.gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        yield json.loads(line)

        elif name.endswith(".jsonl"):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        yield json.loads(line)

        elif name.endswith(".parquet"):
            if pd is None:
                raise ImportError("Pandas / PyArrow is required to stream .parquet partitions.")
            # Read in chunked batches to keep RAM memory bounded
            df = pd.read_parquet(path)
            for _, row in df.iterrows():
                yield row.to_dict()

        elif name.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        yield item
                else:
                    yield data
        else:
            raise ValueError(f"Unsupported partition format: {partition_path}")

    def _compute_partition_stats(self, partition_path: str, source_id: str) -> Dict[str, Any]:
        """
        Streams a partition file and incrementally computes primitive statistics counters.
        """
        path = Path(partition_path)
        stat = path.stat()
        mtime = stat.st_mtime
        size_bytes = stat.st_size

        # Check cache
        cached_stats = self.cache.get(partition_path, mtime, size_bytes)
        if cached_stats:
            return cached_stats

        # Compute stats incrementally
        rec_count = 0
        turns_count = 0
        messages_count = 0
        prompt_lens: List[int] = []
        taxonomy_counts: Dict[str, int] = {}
        difficulty_counts: Dict[str, int] = {}
        eval_successes = 0
        eval_total = 0
        severity_sum = 0.0
        severity_count = 0
        target_models: Set[str] = set()

        for rec in self.stream_records(partition_path):
            rec_count += 1

            # Taxonomy
            tax_node = rec.get("taxonomy_node", "AUAO-PI-DIR")
            taxonomy_counts[tax_node] = taxonomy_counts.get(tax_node, 0) + 1

            # Difficulty
            diff = rec.get("difficulty_level", "Medium")
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

            # Turns & Messages
            turns = rec.get("turns", [])
            if isinstance(turns, list):
                turns_count += len(turns)
                for turn in turns:
                    if isinstance(turn, dict):
                        msgs = turn.get("messages", [])
                        if isinstance(msgs, list):
                            messages_count += len(msgs)
                            for msg in msgs:
                                if isinstance(msg, dict) and msg.get("is_injection_source", False):
                                    content = msg.get("content", "")
                                    prompt_lens.append(len(content))

            # Evaluations
            evals = rec.get("evaluations", [])
            if isinstance(evals, list):
                for ev in evals:
                    if isinstance(ev, dict):
                        target_model = ev.get("target_model")
                        if target_model and target_model != "unknown":
                            target_models.add(str(target_model))

                        if "attack_success" in ev:
                            eval_total += 1
                            if ev["attack_success"]:
                                eval_successes += 1

                        if "severity_score" in ev and ev["severity_score"] is not None:
                            severity_sum += float(ev["severity_score"])
                            severity_count += 1

        partition_stats = {
            "source_id": source_id,
            "partition_path": partition_path,
            "size_bytes": size_bytes,
            "record_count": rec_count,
            "turns_count": turns_count,
            "messages_count": messages_count,
            "prompt_lens_sum": sum(prompt_lens),
            "prompt_lens_count": len(prompt_lens),
            "prompt_lens_max": max(prompt_lens) if prompt_lens else 0,
            "prompt_lens_min": min(prompt_lens) if prompt_lens else 0,
            "taxonomy_counts": taxonomy_counts,
            "difficulty_counts": difficulty_counts,
            "eval_successes": eval_successes,
            "eval_total": eval_total,
            "severity_sum": severity_sum,
            "severity_count": severity_count,
            "target_models": list(target_models)
        }

        # Store into cache
        self.cache.put(partition_path, mtime, size_bytes, partition_stats)
        return partition_stats

    def compute_statistics(self, source_id: Optional[str] = None) -> CorpusStatisticsReport:
        """
        Computes aggregate corpus statistics, optionally filtering by source_id.
        
        Args:
            source_id (Optional[str]): Dataset source filter (e.g. 'hackaprompt').
            
        Returns:
            CorpusStatisticsReport: Strong typed aggregate statistics report.
        """
        discovered_partitions = self.registry.discover_partitions()

        if source_id:
            discovered_partitions = [p for p in discovered_partitions if p.source_id == source_id]

        total_records = 0
        total_turns = 0
        total_messages = 0
        total_size_bytes = 0
        compressed_size_bytes = 0
        prompt_lens_sum = 0
        prompt_lens_count = 0
        max_prompt_len = 0
        min_prompt_len = float("inf")

        record_dist: Dict[str, int] = {}
        dataset_sizes: Dict[str, int] = {}
        taxonomy_dist: Dict[str, int] = {}
        difficulty_dist: Dict[str, int] = {}

        eval_successes = 0
        eval_total = 0
        severity_sum = 0.0
        severity_count = 0
        unique_target_models: Set[str] = set()

        for part in discovered_partitions:
            p_stats = self._compute_partition_stats(part.partition_path, part.source_id)

            ds_id = part.source_id
            rec_cnt = p_stats["record_count"]
            s_bytes = p_stats["size_bytes"]

            total_records += rec_cnt
            total_turns += p_stats["turns_count"]
            total_messages += p_stats["messages_count"]
            total_size_bytes += s_bytes
            compressed_size_bytes += s_bytes if part.compression else s_bytes

            record_dist[ds_id] = record_dist.get(ds_id, 0) + rec_cnt
            dataset_sizes[ds_id] = dataset_sizes.get(ds_id, 0) + s_bytes

            # Prompt length aggregation
            p_sum = p_stats["prompt_lens_sum"]
            p_cnt = p_stats["prompt_lens_count"]
            prompt_lens_sum += p_sum
            prompt_lens_count += p_cnt

            if p_stats["prompt_lens_max"] > max_prompt_len:
                max_prompt_len = p_stats["prompt_lens_max"]
            if p_cnt > 0 and p_stats["prompt_lens_min"] < min_prompt_len:
                min_prompt_len = p_stats["prompt_lens_min"]

            # Taxonomy & Difficulty aggregation
            for tax_k, tax_v in p_stats["taxonomy_counts"].items():
                taxonomy_dist[tax_k] = taxonomy_dist.get(tax_k, 0) + tax_v

            for diff_k, diff_v in p_stats["difficulty_counts"].items():
                difficulty_dist[diff_k] = difficulty_dist.get(diff_k, 0) + diff_v

            # Evaluation metrics aggregation
            eval_successes += p_stats["eval_successes"]
            eval_total += p_stats["eval_total"]
            severity_sum += p_stats["severity_sum"]
            severity_count += p_stats["severity_count"]

            for tm in p_stats["target_models"]:
                unique_target_models.add(tm)

        avg_turns = round(total_turns / total_records, 2) if total_records > 0 else 0.0
        avg_messages = round(total_messages / total_records, 2) if total_records > 0 else 0.0
        avg_prompt_len = round(prompt_lens_sum / prompt_lens_count, 2) if prompt_lens_count > 0 else 0.0
        min_prompt_len_final = int(min_prompt_len) if min_prompt_len != float("inf") else 0
        eval_succ_rate = round(eval_successes / eval_total, 4) if eval_total > 0 else 0.0
        avg_severity = round(severity_sum / severity_count, 2) if severity_count > 0 else 0.0

        return CorpusStatisticsReport(
            total_records=total_records,
            total_turns=total_turns,
            total_messages=total_messages,
            average_turns_per_record=avg_turns,
            average_messages_per_record=avg_messages,
            average_prompt_length=avg_prompt_len,
            maximum_prompt_length=max_prompt_len,
            minimum_prompt_length=min_prompt_len_final,
            storage_size_bytes=total_size_bytes,
            compressed_size_bytes=compressed_size_bytes,
            record_distribution_per_dataset=record_dist,
            taxonomy_distribution=taxonomy_dist,
            difficulty_distribution=difficulty_dist,
            evaluation_success_rate=eval_succ_rate,
            average_severity_score=avg_severity,
            unique_target_models=sorted(list(unique_target_models)),
            dataset_sizes=dataset_sizes
        )

    def compute_dataset_statistics(self, dataset_id: str) -> CorpusStatisticsReport:
        """
        Computes statistics specifically for a single dataset ID.
        """
        return self.compute_statistics(source_id=dataset_id)
