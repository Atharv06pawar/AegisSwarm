import pytest
from providers.factory import LLMFactory
from providers.models import GenerationRequest
from providers.adapters.openai import OpenAIProvider
from providers.adapters.anthropic import AnthropicProvider
from providers.adapters.gemini import GeminiProvider
from providers.adapters.ollama import OllamaProvider
from providers.adapters.openrouter import OpenRouterProvider


def test_factory_creates_openai():
    """Verify LLMFactory creates OpenAIProvider with model override."""
    adapter = LLMFactory.create("openai", model="gpt-4.1", api_key="sk-test-key")
    assert isinstance(adapter, OpenAIProvider)
    assert adapter.provider_name == "openai"
    assert adapter.default_model == "gpt-4.1"


def test_factory_creates_anthropic():
    """Verify LLMFactory creates AnthropicProvider."""
    adapter = LLMFactory.create("anthropic", model="claude-3-5-sonnet-20241022", api_key="sk-ant-key")
    assert isinstance(adapter, AnthropicProvider)
    assert adapter.provider_name == "anthropic"
    assert "claude-3-5-sonnet-20241022" in adapter.list_models()
    
    # Test health check & generation
    health = adapter.health()
    assert health.status == "ok"
    res = adapter.generate(GenerationRequest(user_prompt="Anthropic prompt", system_prompt="System prompt"))
    assert "[Anthropic Adapter]" in res.completion
    assert res.provider == "anthropic"
    
    # Stream test
    chunks = list(adapter.stream_generate(GenerationRequest(user_prompt="Stream Anthropic")))
    assert len(chunks) > 0


def test_factory_creates_gemini():
    """Verify LLMFactory creates GeminiProvider."""
    adapter = LLMFactory.create("gemini", model="gemini-1.5-pro", api_key="AIzaSyTest")
    assert isinstance(adapter, GeminiProvider)
    assert adapter.provider_name == "gemini"
    assert "gemini-1.5-pro" in adapter.list_models()
    
    # Test health check & generation
    health = adapter.health()
    assert health.status == "ok"
    res = adapter.generate(GenerationRequest(user_prompt="Gemini prompt", system_prompt="System prompt"))
    assert "[Gemini Adapter]" in res.completion
    assert res.provider == "gemini"
    
    # Stream test
    chunks = list(adapter.stream_generate(GenerationRequest(user_prompt="Stream Gemini")))
    assert len(chunks) > 0


def test_factory_creates_openrouter():
    """Verify LLMFactory creates OpenRouterProvider."""
    adapter = LLMFactory.create("openrouter", model="meta-llama/llama-3.1-70b-instruct", api_key="sk-or-key")
    assert isinstance(adapter, OpenRouterProvider)
    assert adapter.provider_name == "openrouter"
    assert "openai/gpt-4o" in adapter.list_models()
    
    # Test health check & generation
    health = adapter.health()
    assert health.status == "ok"
    res = adapter.generate(GenerationRequest(user_prompt="OpenRouter prompt", system_prompt="System prompt"))
    assert "[OpenRouter Adapter]" in res.completion
    assert res.provider == "openrouter"
    
    # Stream test
    chunks = list(adapter.stream_generate(GenerationRequest(user_prompt="Stream OpenRouter")))
    assert len(chunks) > 0


def test_factory_creates_ollama():
    """Verify LLMFactory creates OllamaProvider with host parameter."""
    adapter = LLMFactory.create("ollama", model="llama3.2", host="http://localhost:11434")
    assert isinstance(adapter, OllamaProvider)
    assert adapter.provider_name == "ollama"
    assert adapter.host == "http://localhost:11434"
