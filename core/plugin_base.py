from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any
from core.schema import AttackRecord, DatasetMetadata

class BaseDatasetPlugin(ABC):
    """
    Abstract Base Class for all AegisSwarm Dataset Ingestion Plugins.
    Enforces a strict streaming contract to support processing millions of records
    without triggering Out-Of-Memory (OOM) errors.
    """
    
    @property
    @abstractmethod
    def dataset_id(self) -> str:
        """
        The unique string identifier for this dataset.
        e.g., 'hackaprompt-2023'
        """
        pass
        
    @property
    @abstractmethod
    def parser_version(self) -> str:
        """
        The semantic version of this parser plugin.
        Used for lineage tracking in the data lake.
        """
        pass

    @abstractmethod
    def metadata(self) -> DatasetMetadata:
        """
        Returns the core metadata (license, description, attribution) 
        for the external dataset being processed.
        """
        pass

    @abstractmethod
    def fetch(self) -> str:
        """
        Downloads or locates the raw data files required for this dataset.
        If the file already exists locally, it should skip downloading.
        
        Returns:
            str: The absolute path to the directory or file containing the raw data.
        """
        pass

    @abstractmethod
    def parse(self, raw_data_path: str) -> Iterator[Dict[str, Any]]:
        """
        Reads the raw data iteratively (e.g., streaming a JSONL or CSV file line by line).
        
        Args:
            raw_data_path (str): The path returned by the fetch() method.
            
        Yields:
            Iterator[Dict[str, Any]]: Raw, unvalidated Python dictionaries.
            MUST return a generator, not a list, to prevent OOM errors.
        """
        pass

    @abstractmethod
    def normalize(self, raw_record: Dict[str, Any]) -> AttackRecord:
        """
        Maps a single raw dictionary record into the strict AttackRecord schema.
        
        Args:
            raw_record (Dict[str, Any]): A single row/object from parse().
            
        Returns:
            AttackRecord: The fully validated Pydantic model.
        """
        pass

    def validate(self, records: Iterator[AttackRecord]) -> Iterator[AttackRecord]:
        """
        An optional validation pass on the normalized records before writing to storage.
        Yields valid records iteratively.
        
        By default, it acts as a passthrough, but subclasses can override this
        to implement custom filtering (e.g., dropping empty turns).
        
        Args:
            records (Iterator[AttackRecord]): The stream of normalized records.
            
        Yields:
            Iterator[AttackRecord]: The stream of filtered, valid records.
        """
        for record in records:
            # Default behavior passes the record through.
            yield record
