from typing import List, Optional
from pathlib import Path

from corpus.models import CorpusSummary, DatasetInfo, CorpusManifest
from corpus.registry import CorpusRegistry
from corpus.manifest import CorpusManifestHandler

class CorpusManager:
    """
    Facade service orchestrating CorpusRegistry and CorpusManifestHandler.
    Provides a unified management API for inspecting dataset status, partitions,
    and creating state snapshots without loading dataset records into memory.
    """

    def __init__(
        self, 
        registry: Optional[CorpusRegistry] = None,
        manifest_handler: Optional[CorpusManifestHandler] = None
    ):
        self.registry = registry or CorpusRegistry()
        self.manifest_handler = manifest_handler or CorpusManifestHandler()

    def get_status(self) -> CorpusSummary:
        """
        Retrieves high-level summary metrics of the current corpus.
        """
        return self.registry.get_summary()

    def list_datasets(self) -> List[DatasetInfo]:
        """
        Lists all registered datasets and their partition details.
        """
        return self.registry.list_datasets()

    def get_dataset(self, source_id: str) -> Optional[DatasetInfo]:
        """
        Retrieves partition information for a single dataset.
        """
        return self.registry.get_dataset_info(source_id)

    def create_snapshot(self, output_path: str = "outputs/corpus_manifest.json") -> CorpusManifest:
        """
        Creates and exports a reproducible CorpusManifest snapshot file.
        
        Args:
            output_path (str): Destination path for the manifest JSON.
            
        Returns:
            CorpusManifest: The generated manifest object.
        """
        summary = self.registry.get_summary()
        datasets = self.registry.list_datasets()
        manifest = self.manifest_handler.create_manifest(summary, datasets)
        self.manifest_handler.export_manifest(manifest, output_path)
        return manifest

    def load_snapshot(self, input_path: str = "outputs/corpus_manifest.json") -> CorpusManifest:
        """
        Loads and validates an existing CorpusManifest snapshot.
        """
        return self.manifest_handler.load_manifest(input_path)
