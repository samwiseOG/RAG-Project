import os
from pathlib import Path
from typing import Optional, Dict, Any
import toml


class SecretsManager:
    """Manage Streamlit secrets file (secrets.toml)."""

    def __init__(self):
        self.secrets_file = Path.home() / ".streamlit" / "secrets.toml"

    def load_secrets(self) -> Dict[str, Any]:
        """Load secrets from secrets.toml file."""
        if not self.secrets_file.exists():
            return {}

        try:
            with open(self.secrets_file, "r") as f:
                return toml.load(f)
        except Exception as e:
            print(f"Error loading secrets: {e}")
            return {}

    def save_secrets(self, secrets: Dict[str, Any]) -> bool:
        """Save secrets to secrets.toml file."""
        try:
            self.secrets_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.secrets_file, "w") as f:
                toml.dump(secrets, f)
            return True
        except Exception as e:
            print(f"Error saving secrets: {e}")
            return False

    def get_credential(self, provider: str) -> Optional[str]:
        """Get API key credential for a provider."""
        secrets = self.load_secrets()

        credential_keys = {
            "claude": "llm_credentials.anthropic_api_key",
            "openai": "llm_credentials.openai_api_key",
            "gemini": "llm_credentials.google_api_key",
        }

        if provider.lower() not in credential_keys:
            return None

        key_path = credential_keys[provider.lower()]
        keys = key_path.split(".")

        current = secrets
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current if isinstance(current, str) else None

    def set_credential(self, provider: str, api_key: str) -> bool:
        """Set API key credential for a provider."""
        secrets = self.load_secrets()

        if "llm_credentials" not in secrets:
            secrets["llm_credentials"] = {}

        credential_keys = {
            "claude": "anthropic_api_key",
            "openai": "openai_api_key",
            "gemini": "google_api_key",
        }

        if provider.lower() not in credential_keys:
            return False

        secrets["llm_credentials"][credential_keys[provider.lower()]] = api_key
        return self.save_secrets(secrets)

    def clear_credential(self, provider: str) -> bool:
        """Clear API key credential for a provider."""
        secrets = self.load_secrets()

        if "llm_credentials" not in secrets:
            return True

        credential_keys = {
            "claude": "anthropic_api_key",
            "openai": "openai_api_key",
            "gemini": "google_api_key",
        }

        if provider.lower() not in credential_keys:
            return False

        key = credential_keys[provider.lower()]
        if key in secrets["llm_credentials"]:
            del secrets["llm_credentials"][key]
            return self.save_secrets(secrets)

        return True

    def get_ollama_host(self) -> Optional[str]:
        """Get Ollama host from secrets."""
        secrets = self.load_secrets()
        return secrets.get("llm_providers", {}).get("ollama_host")

    def set_ollama_host(self, host: str) -> bool:
        """Set Ollama host in secrets."""
        secrets = self.load_secrets()

        if "llm_providers" not in secrets:
            secrets["llm_providers"] = {}

        secrets["llm_providers"]["ollama_host"] = host
        return self.save_secrets(secrets)

    def get_default_models(self) -> Dict[str, str]:
        """Get default model selections for each provider."""
        secrets = self.load_secrets()
        defaults = secrets.get("llm_defaults", {})

        return {
            "ollama": defaults.get(
                "default_model_ollama", "deepseek-r1:1.5b"
            ),
            "claude": defaults.get(
                "default_model_claude", "claude-3-5-sonnet-20241022"
            ),
            "openai": defaults.get(
                "default_model_openai", "gpt-4o"
            ),
            "gemini": defaults.get(
                "default_model_gemini", "gemini-2.0-flash"
            ),
        }

    def set_default_model(self, provider: str, model: str) -> bool:
        """Set default model for a provider."""
        secrets = self.load_secrets()

        if "llm_defaults" not in secrets:
            secrets["llm_defaults"] = {}

        secrets["llm_defaults"][f"default_model_{provider}"] = model
        return self.save_secrets(secrets)


_secrets_manager = None


def get_secrets_manager() -> SecretsManager:
    """Get or create global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
