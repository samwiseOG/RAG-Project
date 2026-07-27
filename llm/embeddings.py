from abc import ABC, abstractmethod
from typing import Optional, List
import os
from langchain_core.embeddings import Embeddings


class BaseEmbeddingProvider(ABC):
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.provider_type = "base"

    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        """Return a LangChain Embeddings instance."""
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Check if required credentials are available."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models for this provider."""
        pass


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str, ollama_host: str = "localhost:11434", **kwargs):
        super().__init__(model_name)
        self.provider_type = "ollama"
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "localhost:11434")

    def get_embeddings(self) -> Embeddings:
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(
            model=self.model_name,
            base_url=f"http://{self.ollama_host}",
        )

    def validate_credentials(self) -> bool:
        import requests
        try:
            response = requests.get(f"http://{self.ollama_host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        try:
            import requests
            response = requests.get(f"http://{self.ollama_host}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", m) for m in models]
        except Exception:
            pass
        return [self.model_name]


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name)
        self.provider_type = "openai"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def get_embeddings(self) -> Embeddings:
        from langchain_openai import OpenAIEmbeddings
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        return OpenAIEmbeddings(
            model=self.model_name,
            api_key=self.api_key,
        )

    def validate_credentials(self) -> bool:
        return bool(self.api_key)

    def get_available_models(self) -> List[str]:
        return [
            "text-embedding-3-large",
            "text-embedding-3-small",
            "text-embedding-ada-002",
        ]


EMBEDDING_PROVIDERS = {
    "ollama": OllamaEmbeddingProvider,
    "openai": OpenAIEmbeddingProvider,
}

EMBEDDING_MODEL_REGISTRY = {
    "ollama": [
        "nomic-embed-text",
        "mxbai-embed-large",
        "all-minilm",
    ],
    "openai": [
        "text-embedding-3-large",
        "text-embedding-3-small",
        "text-embedding-ada-002",
    ],
}


def get_embedding_provider(
    provider_name: str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> BaseEmbeddingProvider:
    """Factory function to create an embedding provider instance."""
    provider_name_lower = provider_name.lower()

    if provider_name_lower not in EMBEDDING_PROVIDERS:
        raise ValueError(f"Unknown embedding provider: {provider_name}")

    provider_class = EMBEDDING_PROVIDERS[provider_name_lower]

    if model_name is None:
        if provider_name_lower == "ollama":
            model_name = "nomic-embed-text"
        elif provider_name_lower == "openai":
            model_name = "text-embedding-3-small"

    return provider_class(model_name=model_name, api_key=api_key, **kwargs)


def parse_embedding_model_string(model_string: str) -> tuple[str, str]:
    """Parse 'provider:model_name' format into (provider, model_name)."""
    if ":" not in model_string:
        return "ollama", model_string

    parts = model_string.split(":", 1)
    return parts[0].lower(), parts[1]
