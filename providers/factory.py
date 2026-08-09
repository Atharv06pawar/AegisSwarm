"""
LLMFactory for convenient creation of LLMProvider adapter instances.
"""

from typing import Optional
from providers.base import LLMProvider
from providers.registry import ProviderRegistry


class LLMFactory:
    """
    Factory interface for creating configured LLMProvider adapter instances.
    Simplifies instantiation of OpenAI, Anthropic, Gemini, OpenRouter, and Ollama providers.
    """

    @staticmethod
    def create(provider: str, model: Optional[str] = None, **kwargs) -> LLMProvider:
        """
        Creates and returns a configured LLMProvider adapter instance.
        
        Args:
            provider (str): Provider name identifier (e.g. 'openai', 'anthropic', 'ollama').
            model (Optional[str]): Target model override.
            **kwargs: Additional parameters (api_key, host, timeout, max_retries).
            
        Returns:
            LLMProvider: Configured adapter instance.
            
        Example:
            provider = LLMFactory.create(provider="openai", model="gpt-4.1")
        """
        if model:
            kwargs["model"] = model
            
        return ProviderRegistry.create(provider_name=provider, **kwargs)
