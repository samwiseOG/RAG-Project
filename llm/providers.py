from abc import ABC, abstractmethod
from typing import Optional, List
import os
from langchain_core.language_models import BaseLanguageModel


class BaseProvider(ABC):
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.provider_type = "base"

    @abstractmethod
    def get_llm(self) -> BaseLanguageModel:
        """Return a LangChain BaseLanguageModel instance."""
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Check if required credentials are available."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models for this provider."""
        pass


class OllamaProvider(BaseProvider):
    def __init__(self, model_name: str, ollama_host: str = "localhost:11434", **kwargs):
        super().__init__(model_name)
        self.provider_type = "ollama"
        self.ollama_host = ollama_host or os.getenv("OLLAMA_HOST", "localhost:11434")

    def get_llm(self) -> BaseLanguageModel:
        from langchain_community.llms import Ollama
        return Ollama(
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


class ClaudeProvider(BaseProvider):
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name)
        self.provider_type = "claude"
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    def get_llm(self) -> BaseLanguageModel:
        from langchain_anthropic import ChatAnthropic
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        return ChatAnthropic(
            model=self.model_name,
            api_key=self.api_key,
        )

    def validate_credentials(self) -> bool:
        return bool(self.api_key)

    def get_available_models(self) -> List[str]:
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]


class OpenAIProvider(BaseProvider):
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name)
        self.provider_type = "openai"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def get_llm(self) -> BaseLanguageModel:
        from langchain_openai import ChatOpenAI
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        return ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
        )

    def validate_credentials(self) -> bool:
        return bool(self.api_key)

    def get_available_models(self) -> List[str]:
        return [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-4",
        ]


class GeminiProvider(BaseProvider):
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name)
        self.provider_type = "gemini"
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

    def get_llm(self) -> BaseLanguageModel:
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            api_key=self.api_key,
        )

    def validate_credentials(self) -> bool:
        return bool(self.api_key)

    def get_available_models(self) -> List[str]:
        return [
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
        ]


PROVIDERS = {
    "ollama": OllamaProvider,
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
}

MODEL_REGISTRY = {
    "ollama": [
        "deepseek-r1:1.5b",
        "mistral",
        "llama2",
        "neural-chat",
        "nomic-embed-text",
    ],
    "claude": [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gpt-4",
    ],
    "gemini": [
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-pro",
    ],
}


def get_provider(
    provider_name: str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> BaseProvider:
    """Factory function to create a provider instance."""
    provider_name_lower = provider_name.lower()

    if provider_name_lower not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}")

    provider_class = PROVIDERS[provider_name_lower]

    if model_name is None:
        if provider_name_lower == "ollama":
            model_name = "deepseek-r1:1.5b"
        elif provider_name_lower == "claude":
            model_name = "claude-3-5-sonnet-20241022"
        elif provider_name_lower == "openai":
            model_name = "gpt-4o"
        elif provider_name_lower == "gemini":
            model_name = "gemini-2.0-flash"

    return provider_class(model_name=model_name, api_key=api_key, **kwargs)


def parse_model_string(model_string: str) -> tuple[str, str]:
    """Parse 'provider:model_name' format into (provider, model_name)."""
    if ":" not in model_string:
        return "ollama", model_string

    parts = model_string.split(":", 1)
    return parts[0].lower(), parts[1]
