"""
Custom exception hierarchy for the AegisSwarm Provider Abstraction Layer.
"""

class ProviderError(Exception):
    """Base exception for all provider abstraction errors."""
    def __init__(self, message: str, provider: str = "unknown"):
        self.message = message
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class ProviderNotFound(ProviderError):
    """Raised when a requested provider adapter is not registered in the registry."""
    def __init__(self, provider: str):
        super().__init__(message=f"Provider '{provider}' is not registered.", provider=provider)


class AuthenticationFailed(ProviderError):
    """Raised when provider API key or authentication credentials fail."""
    def __init__(self, provider: str, details: str = "Invalid API key or authentication failure."):
        super().__init__(message=f"Authentication failed: {details}", provider=provider)


class RateLimitExceeded(ProviderError):
    """Raised when provider rate limit (HTTP 429) or quota is exceeded."""
    def __init__(self, provider: str, details: str = "Rate limit exceeded."):
        super().__init__(message=f"Rate limit exceeded: {details}", provider=provider)


class ProviderTimeout(ProviderError):
    """Raised when a provider request times out."""
    def __init__(self, provider: str, timeout_seconds: float = 30.0):
        super().__init__(message=f"Request timed out after {timeout_seconds} seconds.", provider=provider)


class ModelUnavailable(ProviderError):
    """Raised when a requested model is not supported or unavailable for the provider."""
    def __init__(self, provider: str, model: str):
        super().__init__(message=f"Model '{model}' is unavailable for provider '{provider}'.", provider=provider)


class ProviderConfigurationError(ProviderError):
    """Raised when provider configuration or environment settings are missing or invalid."""
    def __init__(self, provider: str, details: str):
        super().__init__(message=f"Configuration error: {details}", provider=provider)
