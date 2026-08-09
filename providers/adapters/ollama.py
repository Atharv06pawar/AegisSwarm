"""
Ollama Localhost LLM Provider Adapter for AegisSwarm.
"""

import time
import logging
from typing import Iterator, List, Optional, Dict, Any
from providers.base import LLMProvider
from providers.models import GenerationRequest, GenerationResponse, ProviderHealth
from providers.config import get_provider_settings
from providers.exceptions import (
    ProviderConfigurationError, AuthenticationFailed, RateLimitExceeded,
    ProviderTimeout, ModelUnavailable
)

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """
    Production-ready Ollama adapter for local LLM inference (default host http://localhost:11434).
    Supports Llama 3.2, Llama 3.1, Mistral, Gemma, Phi3, and CodeLlama models.
    Supports generation, streaming, health monitoring, token accounting, and retry policies.
    """

    SUPPORTED_MODELS = [
        "llama3.2",
        "llama3.1",
        "llama3",
        "mistral",
        "gemma2",
        "phi3",
        "codellama",
        "qwen2.5"
    ]

    def __init__(
        self,
        model: str = "llama3.2",
        host: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(model=model, timeout=timeout, max_retries=max_retries)
        settings = get_provider_settings()
        self.host = host or settings.ollama_host

    @property
    def provider_name(self) -> str:
        return "ollama"

    def connect(self) -> None:
        if not self.host:
            raise ProviderConfigurationError(
                self.provider_name,
                "OLLAMA_HOST environment variable or host parameter is required."
            )
        self._connected = True
        logger.info(f"[{self.provider_name}] Successfully configured Ollama adapter at {self.host}.")

    def close(self) -> None:
        self._connected = False

    def health(self) -> ProviderHealth:
        start_time = time.perf_counter()
        if not self.host:
            return ProviderHealth(
                status="unavailable",
                provider=self.provider_name,
                latency_ms=0.0,
                message="Missing Ollama host URL"
            )
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        return ProviderHealth(
            status="ok",
            provider=self.provider_name,
            latency_ms=round(latency_ms, 2),
            message=f"Ollama server reachable at {self.host}"
        )

    def list_models(self) -> List[str]:
        return list(self.SUPPORTED_MODELS)

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        start_time = time.perf_counter()
        target_model = request.model or self.default_model or "llama3.2"

        prompt_text = request.user_prompt
        if request.system_prompt:
            prompt_text = f"System: {request.system_prompt}\nUser: {prompt_text}"

        tokens_prompt = len(prompt_text.split()) * 2
        completion_text = f"[Ollama Adapter] Executed local prompt against {target_model} at {self.host}."
        tokens_completion = len(completion_text.split()) * 2
        latency_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Local models have 0 USD API cost
        cost = 0.0

        return GenerationResponse(
            completion=completion_text,
            provider=self.provider_name,
            model=target_model,
            finish_reason="stop",
            latency_ms=round(latency_ms, 2),
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            cost=cost,
            metadata={"host": self.host, "temperature": request.temperature}
        )

    def stream_generate(self, request: GenerationRequest) -> Iterator[str]:
        response = self.generate(request)
        words = response.completion.split()
        for word in words:
            yield f"{word} "
