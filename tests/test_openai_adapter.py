import pytest
from providers.adapters.openai import OpenAIProvider
from providers.models import GenerationRequest
from providers.exceptions import ProviderConfigurationError, AuthenticationFailed, ModelUnavailable


def test_openai_missing_api_key_raises_error():
    """Verify connect() raises ProviderConfigurationError when API key is missing."""
    adapter = OpenAIProvider(api_key=None)
    with pytest.raises(ProviderConfigurationError, match="OPENAI_API_KEY environment variable or api_key parameter is required"):
        adapter.connect()


def test_openai_list_models():
    """Verify list_models returns expected OpenAI models."""
    adapter = OpenAIProvider(api_key="sk-test-key")
    models = adapter.list_models()
    assert "gpt-4o" in models
    assert "gpt-4.1" in models


def test_openai_health_check():
    """Verify OpenAI health check returns status ok when configured."""
    adapter = OpenAIProvider(api_key="sk-test-key")
    health = adapter.health()
    assert health.status == "ok"
    assert health.provider == "openai"
    assert health.latency_ms >= 0.0


def test_openai_generation():
    """Verify OpenAI text generation response formatting and token accounting."""
    adapter = OpenAIProvider(model="gpt-4o", api_key="sk-test-key")
    request = GenerationRequest(
        system_prompt="You are an assistant.",
        user_prompt="Hello OpenAI",
        temperature=0.5
    )
    
    response = adapter.generate(request)
    assert response.provider == "openai"
    assert response.model == "gpt-4o"
    assert "[OpenAI Adapter]" in response.completion
    assert response.tokens_prompt > 0
    assert response.tokens_completion > 0
    assert response.cost >= 0.0


def test_openai_streaming():
    """Verify OpenAI stream_generate yields chunks of text."""
    adapter = OpenAIProvider(model="gpt-4o", api_key="sk-test-key")
    request = GenerationRequest(user_prompt="Stream test")
    
    chunks = list(adapter.stream_generate(request))
    assert len(chunks) > 0
    combined = "".join(chunks)
    assert "[OpenAI Adapter]" in combined


def test_openai_invalid_model_raises():
    """Verify requesting an unsupported model name raises ModelUnavailable."""
    adapter = OpenAIProvider(api_key="sk-test-key")
    request = GenerationRequest(user_prompt="Test", model="invalid-model-999")
    
    with pytest.raises(ModelUnavailable, match="invalid-model-999"):
        adapter.generate(request)
