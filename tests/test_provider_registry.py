import pytest
from typing import Iterator, List
from providers.base import LLMProvider
from providers.models import GenerationRequest, GenerationResponse, ProviderHealth
from providers.registry import ProviderRegistry
from providers.exceptions import ProviderNotFound


class MockCustomProvider(LLMProvider):
    """Mock provider class for testing registry functionality."""
    
    @property
    def provider_name(self) -> str:
        return "mock_custom"

    def connect(self) -> None:
        self._connected = True

    def close(self) -> None:
        self._connected = False

    def health(self) -> ProviderHealth:
        return ProviderHealth(status="ok", provider=self.provider_name, latency_ms=1.0, message="Healthy")

    def list_models(self) -> List[str]:
        return ["mock-model-v1"]

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(
            completion="Mock output",
            provider=self.provider_name,
            model=request.model or "mock-model-v1"
        )

    def stream_generate(self, request: GenerationRequest) -> Iterator[str]:
        yield "Mock "
        yield "output"


def test_provider_registration_and_list():
    """Test manual provider adapter registration and listing."""
    ProviderRegistry.clear()
    ProviderRegistry.register(MockCustomProvider, name="mock_custom")

    providers = ProviderRegistry.list_providers()
    assert "mock_custom" in providers
    
    cls = ProviderRegistry.get_provider_class("mock_custom")
    assert cls is MockCustomProvider


def test_provider_unregister():
    """Test unregistering an adapter from the registry."""
    ProviderRegistry.clear()
    ProviderRegistry.register(MockCustomProvider, name="mock_custom")
    assert "mock_custom" in ProviderRegistry.list_providers()

    ProviderRegistry.unregister("mock_custom")
    assert "mock_custom" not in ProviderRegistry.list_providers()


def test_provider_not_found():
    """Test that requesting an unknown provider raises ProviderNotFound exception."""
    ProviderRegistry.clear()
    with pytest.raises(ProviderNotFound, match="non_existent_provider"):
        ProviderRegistry.get_provider_class("non_existent_provider")


def test_provider_discovery():
    """Test dynamic discovery of built-in adapters in providers/adapters/."""
    ProviderRegistry.clear()
    discovered = ProviderRegistry.discover()

    assert "openai" in discovered
    assert "anthropic" in discovered
    assert "gemini" in discovered
    assert "ollama" in discovered
    assert "openrouter" in discovered
