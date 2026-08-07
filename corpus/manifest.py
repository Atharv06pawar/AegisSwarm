import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

from corpus.models import CorpusManifest, CorpusSummary, DatasetInfo

class CorpusManifestHandler:
    """
    Handler for generating, serializing, and loading reproducible corpus snapshot manifests.
    """

    @staticmethod
    def create_manifest(summary: CorpusSummary, datasets: List[DatasetInfo]) -> CorpusManifest:
        """
        Creates a new CorpusManifest instance.
        """
        return CorpusManifest(
            manifest_version="1.0.0",
            created_at=datetime.now(timezone.utc),
            summary=summary,
            datasets=datasets
        )

    @staticmethod
    def export_manifest(manifest: CorpusManifest, output_path: str = "outputs/corpus_manifest.json") -> str:
        """
        Serializes a CorpusManifest to a JSON file.
        
        Args:
            manifest (CorpusManifest): The manifest instance to export.
            output_path (str): File path destination.
            
        Returns:
            str: Absolute path to written manifest file.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        json_data = manifest.model_dump(mode="json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        return str(path.resolve())

    @staticmethod
    def load_manifest(input_path: str = "outputs/corpus_manifest.json") -> CorpusManifest:
        """
        Deserializes a CorpusManifest from a JSON file.
        
        Args:
            input_path (str): File path to manifest JSON.
            
        Returns:
            CorpusManifest: Deserialized Pydantic v2 manifest model.
        """
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Corpus manifest file not found: {input_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return CorpusManifest.model_validate(data)
