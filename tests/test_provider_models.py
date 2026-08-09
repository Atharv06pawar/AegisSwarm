import pytest
from datetime import datetime
from providers.models import GenerationRequest, GenerationResponse, ProviderHealth

def test_generation_request_defaults():
    """Verify GenerationRequest default fields and validations."""
    req = GenerationRequest(user_prompt="Explain quantum computing.")
    assert req.user_prompt == "Explain quantum computing."
    assert req.system_prompt is None
    assert req.conversation == []
    assert req.temperature == 0.7
    assert req.top_p == 1.0
    assert req.max_tokens is None
    assert req.seed is None
    assert req.tools == []
    assert req.attachments == []
    assert req.model is None
    assert req.metadata == {}

def test_generation_request_custom():
    """Verify GenerationRequest custom field assignment."""
    req = GenerationRequest(
        system_prompt="You are a cybersecurity expert.",
        user_prompt="Analyze this payload.",
        temperature=0.2,
        top_p=0.9,
        max_tokens=500,
        seed=42,
        model="gpt-4o",
        metadata={"session_id": "test_123"}
    )
    assert req.system_prompt == "You are a cybersecurity expert."
    assert req.temperature == 0.2
    assert req.max_tokens == 500
    assert req.seed == 42
    assert req.model == "gpt-4o"
    assert req.metadata["session_id"] == "test_123"

def test_generation_response_validation():
    """Verify GenerationResponse fields and accounting metrics."""
    res = GenerationResponse(
        completion="Quantum computing uses qubits.",
        provider="openai",
        model="gpt-4o",
        finish_reason="stop",
        latency_ms=125.4,
        tokens_prompt=15,
        tokens_completion=25,
        cost=0.00045,
        metadata={"rate_limit_remaining": 99}
    )
    assert res.completion == "Quantum computing uses qubits."
    assert res.provider == "openai"
    assert res.model == "gpt-4o"
    assert res.latency_ms == 125.4
    assert res.tokens_prompt == 15
    assert res.tokens_completion == 25
    assert res.cost == 0.00045
    assert res.created_at is not None

def test_provider_health():
    """Verify ProviderHealth status data structure."""
    health = ProviderHealth(status="ok", provider="ollama", latency_ms=12.5, message="Healthy")
    assert health.status == "ok"
    assert health.provider == "ollama"
    assert health.latency_ms == 12.5
    assert health.message == "Healthy"
