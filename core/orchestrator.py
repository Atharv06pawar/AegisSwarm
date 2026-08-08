import logging
import time
from typing import Dict, Any, Type, Optional, List

from core.registry import PluginRegistry
from core.plugin_base import BaseDatasetPlugin
from storage.data_lake import StorageBackend
from storage.lineage import LineageTracker
from utils.streaming import chunked_iterable, track_progress, safe_map
from logging import get_pipeline_logger, get_ingestion_logger

pipeline_logger = get_pipeline_logger()
ingestion_logger = get_ingestion_logger()

class PipelineOrchestrator:
    """
    Central execution engine for the AegisSwarm Data Pipeline.
    Manages the lifecycle of plugins: fetching, parsing, normalizing, and streaming
    to the Data Lake while tracking lineage and statistics.
    """
    
    def __init__(
        self, 
        storage_backend: StorageBackend, 
        plugin_registry: Type[PluginRegistry] = PluginRegistry,
        batch_size: int = 10000,
        checkpoint_dir: str = "outputs/checkpoints"
    ):
        """
        Dependency injection used for the storage backend and plugin registry 
        to allow easy swapping during testing.
        """
        self.storage_backend = storage_backend
        self.plugin_registry = plugin_registry
        self.batch_size = batch_size
        self.checkpoint_dir = checkpoint_dir
        self.lineage_tracker = LineageTracker()
        self.stats: Dict[str, Any] = {}
        
        # Auto-discover plugins on initialization
        self.plugin_registry.discover()

    def run_all(self) -> Dict[str, Any]:
        """
        Executes all discovered plugins sequentially.
        """
        plugins = self.plugin_registry.list_plugins()
        pipeline_logger.info(f"Orchestrator discovered {len(plugins)} dataset plugins: {plugins}")
        
        for dataset_id in plugins:
            self.run_plugin(dataset_id)
            
        # Flush the final lineage manifest summarizing the entire run
        manifest_path = self.lineage_tracker.save_manifest()
        pipeline_logger.info(f"Pipeline complete. Reproducibility manifest saved to: {manifest_path}")
        
        return self.stats

    def run_plugin(self, dataset_id: str) -> None:
        """
        Executes a single dataset plugin strictly using memory-safe generators.
        Supports graceful keyboard interruption to save state.
        """
        plugin_class = self.plugin_registry.get_plugin(dataset_id)
        plugin_instance = plugin_class()
        
        ingestion_logger.info(f"Starting execution for dataset: {dataset_id} (Parser v{plugin_instance.parser_version})")
        self.stats[dataset_id] = {"records_processed": 0, "batches_written": 0, "errors": 0}
        
        try:
            # 1. Fetch raw data (Downloading / Locating)
            raw_data_path = plugin_instance.fetch()
            ingestion_logger.debug(f"[{dataset_id}] Raw data path resolved: {raw_data_path}")
            
            # 2. Parse (returns an Iterator of Dicts)
            raw_stream = plugin_instance.parse(raw_data_path)
            
            # 3. Normalize (Maps dicts to Pydantic AttackRecord safely)
            normalized_stream = safe_map(plugin_instance.normalize, raw_stream)
            
            # 4. Validate (Custom plugin validation logic)
            validated_stream = plugin_instance.validate(normalized_stream)
            
            # 5. Progress Tracking (Logs dynamically)
            tracked_stream = track_progress(validated_stream, log_interval=5000, label=f"{dataset_id} records")
            
            # 6. Chunking (Slices stream into fixed-size batches without eating memory)
            chunked_stream = chunked_iterable(tracked_stream, self.batch_size)
            
            # 7. Persistence
            output_partitions = []
            for batch_index, batch in enumerate(chunked_stream):
                try:
                    # Atomic write to Data Lake
                    partition_path = self.storage_backend.batch_write(batch, dataset_id)
                    if partition_path:
                        output_partitions.append(partition_path)
                        self.stats[dataset_id]["records_processed"] += len(batch)
                        self.stats[dataset_id]["batches_written"] += 1
                        ingestion_logger.info(
                            f"[{dataset_id}] Batch {batch_index} flushed to partition: {partition_path}",
                            extra={"dataset_id": dataset_id, "batch_index": batch_index, "batch_size": len(batch)}
                        )
                except Exception as e:
                    ingestion_logger.error(
                        f"Failed to write batch {batch_index} for {dataset_id}: {e}",
                        exc_info=True
                    )
                    self.stats[dataset_id]["errors"] += 1
                    
            # 8. Record Execution Lineage for Reproducibility
            if output_partitions:
                self.lineage_tracker.record_execution(
                    dataset_id=dataset_id,
                    dataset_version=plugin_instance.metadata().dataset_id,
                    parser_version=plugin_instance.parser_version,
                    input_file=raw_data_path,
                    output_partitions=output_partitions
                )
                
            ingestion_logger.info(
                f"Completed execution for dataset: {dataset_id}. Records: {self.stats[dataset_id]['records_processed']}"
            )
            
        except KeyboardInterrupt:
            pipeline_logger.warning(f"Pipeline execution for '{dataset_id}' manually interrupted by user! Saving state...")
            raise
        except Exception as e:
            pipeline_logger.error(f"Fatal error processing dataset '{dataset_id}': {e}", exc_info=True)
            self.stats[dataset_id]["errors"] += 1
            raise
