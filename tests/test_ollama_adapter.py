import pytest
from providers.adapters.ollama import OllamaProvider
from providers.models import GenerationRequest


def test_ollama_initialization_defaults():
    """Verify Ollama adapter initializes with localhost default host."""
    adapter = OllamaProvider(host="http://localhost:11434")
    assert adapter.provider_name == "ollama"
    assert adapter.host == "http://localhost:11434"
    assert adapter.default_model == "llama3.2"


def test_ollama_list_models():
    """Verify list_models returns expected local Ollama models."""
    adapter = OllamaProvider(host="http://localhost:11434")
    models = adapter.list_models()
    assert "llama3.2" in models
    assert "mistral" in models


def test_ollama_health_check():
    """Verify Ollama health check status response."""
    adapter = OllamaProvider(host="http://localhost:11434")
    health = adapter.health()
    assert health.status == "ok"
    assert health.provider == "ollama"
    assert "localhost:11434" in health.message


def test_ollama_generation_zero_cost():
    """Verify local Ollama generation calculates 0 USD API cost."""
    adapter = OllamaProvider(model="llama3.2", host="http://localhost:11434")
    request = GenerationRequest(
        user_prompt="Run local prompt",
        temperature=0.7
    )
    
    response = adapter.generate(request)
    assert response.provider == "ollama"
    assert response.model == "llama3.2"
    assert "[Ollama Adapter]" in response.completion
    assert response.cost == 0.0  # Local models must have 0 cost


def test_ollama_streaming():
    """Verify Ollama stream_generate yields chunks of text."""
    adapter = OllamaProvider(model="llama3.2", host="http://localhost:11434")
    request = GenerationRequest(user_prompt="Stream test local")
    
    chunks = list(adapter.stream_generate(request))
    assert len(chunks) > 0
    combined = "".join(chunks)
    assert "[Ollama Adapter]" in combined
