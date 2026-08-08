"""
Custom exceptions for AegisSwarm core platform and dataset ingestion.
"""

class DatasetNotFoundError(FileNotFoundError):
    """
    Raised when an authentic benchmark dataset file is missing from raw storage
    and automatic fallback generation is disabled.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
