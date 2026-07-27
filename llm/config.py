import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class ConfigManager:
    """Manage configuration from multiple sources with fallback chain."""

    def __init__(self):
        self.env_vars = os.environ.copy()
        self.streamlit_secrets = self._load_streamlit_secrets()

    def _load_streamlit_secrets(self) -> Dict[str, Any]:
        """Load Streamlit secrets if available."""
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                return dict(st.secrets)
        except Exception:
            pass
        return {}

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value with fallback chain."""
        # 1. Try environment variables
        if key in self.env_vars:
            return self.env_vars[key]

        # 2. Try Streamlit secrets
        if key in self.streamlit_secrets:
            return self.streamlit_secrets[key]

        # 3. Return default
        return default

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        provider_lower = provider.lower()

        key_mapping = {
            "claude": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GOOGLE_API_KEY",
        }

        if provider_lower not in key_mapping:
            return None

        return self.get(key_mapping[provider_lower])

    def get_ollama_host(self) -> str:
        """Get Ollama host address."""
        return self.get("OLLAMA_HOST", "localhost:11434")

    def is_provider_configured(self, provider: str) -> bool:
        """Check if a provider has required credentials."""
        provider_lower = provider.lower()

        if provider_lower == "ollama":
            # Always return True if Ollama is available
            return True

        api_key = self.get_api_key(provider)
        return bool(api_key)


# Global config instance
_config = None


def get_config() -> ConfigManager:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config


def reload_config():
    """Reload configuration (useful for testing)."""
    global _config
    _config = ConfigManager()
