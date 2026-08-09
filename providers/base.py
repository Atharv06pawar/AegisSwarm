"""
Abstract Base Class for AegisSwarm LLM Provider Adapters.
"""

from abc import ABC, abstractmethod
from typing import Iterator, List, Optional, Dict, Any
from providers.models import GenerationRequest, GenerationResponse, ProviderHealth


class LLMProvider(ABC):
    """
    Abstract Base Class that every AegisSwarm LLM Provider Adapter must inherit.
    Defines the contract for connectivity, model discovery, text generation, and streaming.
    """

    def __init__(self, model: Optional[str] = None, timeout: float = 30.0, max_retries: int = 3):
        self.default_model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self._connected = False

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """The unique identifier string for this provider adapter (e.g. 'openai')."""
        pass

    @abstractmethod
    def connect(self) -> None:
        """Initializes client sessions or verifies connection parameters."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Closes open HTTP connections or network resources."""
        pass

    @abstractmethod
    def health(self) -> ProviderHealth:
        """
        Executes a lightweight health check to verify provider reachability and credentials.
        
        Returns:
            ProviderHealth: Status, latency, and operational message.
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        Retrieves the list of available model names supported by this provider.
        
        Returns:
            List[str]: Model identifiers.
        """
        pass

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Executes a synchronous model text generation request.
        
        Args:
            request (GenerationRequest): Structured generation request.
            
        Returns:
            GenerationResponse: Standard response model.
        """
        pass

    @abstractmethod
    def stream_generate(self, request: GenerationRequest) -> Iterator[str]:
        """
        Executes a streaming text generation request, yielding completion chunks.
        
        Args:
            request (GenerationRequest): Structured generation request.
            
        Yields:
            Iterator[str]: Chunks of generated text.
        """
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
