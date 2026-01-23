"""
Configuration management for video generation providers.

Supports loading configuration from:
1. config.yaml (default)
2. config.local.yaml (local overrides, gitignored)
3. Environment variables (highest priority)
"""

import os
import yaml
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    """Configuration for a single provider."""
    enabled: bool = False
    name: str = ""
    base_url: str = ""
    api_key: str = ""
    access_key: str = ""
    secret_key: str = ""
    region: str = ""
    service: str = ""
    model: str = ""
    defaults: dict = field(default_factory=dict)


@dataclass
class GlobalConfig:
    """Global configuration settings."""
    default_provider: str = "kling"
    timeout: int = 300
    retry_attempts: int = 3
    retry_delay: int = 5


class Config:
    """Configuration manager for all providers."""

    def __init__(self, config_path: Optional[str] = None):
        self._config: dict = {}
        self._providers: dict[str, ProviderConfig] = {}
        self._global: GlobalConfig = GlobalConfig()

        # Determine config file path
        if config_path:
            self._config_path = Path(config_path)
        else:
            self._config_path = Path(__file__).parent / "config.yaml"

        self._load_config()

    def _load_config(self):
        """Load configuration from YAML files and environment variables."""
        # Load base config
        if self._config_path.exists():
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

        # Load local overrides (config.local.yaml)
        local_config_path = self._config_path.parent / "config.local.yaml"
        if local_config_path.exists():
            with open(local_config_path, "r", encoding="utf-8") as f:
                local_config = yaml.safe_load(f) or {}
                self._deep_merge(self._config, local_config)

        # Parse global config
        global_cfg = self._config.get("global", {})
        self._global = GlobalConfig(
            default_provider=global_cfg.get("default_provider", "kling"),
            timeout=global_cfg.get("timeout", 300),
            retry_attempts=global_cfg.get("retry_attempts", 3),
            retry_delay=global_cfg.get("retry_delay", 5),
        )

        # Parse provider configs
        providers_cfg = self._config.get("providers", {})
        for name, cfg in providers_cfg.items():
            self._providers[name] = self._parse_provider_config(name, cfg)

    def _parse_provider_config(self, name: str, cfg: dict) -> ProviderConfig:
        """Parse a provider configuration with environment variable overrides."""
        env_prefix = name.upper()

        return ProviderConfig(
            enabled=cfg.get("enabled", False),
            name=cfg.get("name", name),
            base_url=os.getenv(f"{env_prefix}_BASE_URL", cfg.get("base_url", "")),
            api_key=os.getenv(f"{env_prefix}_API_KEY", cfg.get("api_key", "")),
            access_key=os.getenv(f"{env_prefix}_ACCESS_KEY", cfg.get("access_key", "")),
            secret_key=os.getenv(f"{env_prefix}_SECRET_KEY", cfg.get("secret_key", "")),
            region=cfg.get("region", ""),
            service=cfg.get("service", ""),
            model=os.getenv(f"{env_prefix}_MODEL", cfg.get("model", "")),
            defaults=cfg.get("defaults", {}),
        )

    def _deep_merge(self, base: dict, override: dict):
        """Deep merge override into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    @property
    def global_config(self) -> GlobalConfig:
        """Get global configuration."""
        return self._global

    def get_provider_config(self, name: str) -> ProviderConfig:
        """Get configuration for a specific provider."""
        if name not in self._providers:
            raise ValueError(f"Unknown provider: {name}")
        return self._providers[name]

    def get_enabled_providers(self) -> list[str]:
        """Get list of enabled provider names."""
        return [name for name, cfg in self._providers.items() if cfg.enabled]

    def get_test_prompts(self) -> dict:
        """Get test prompts from configuration."""
        return self._config.get("test_prompts", {})

    def is_provider_configured(self, name: str) -> bool:
        """Check if a provider has valid credentials configured."""
        if name not in self._providers:
            return False

        cfg = self._providers[name]
        if not cfg.enabled:
            return False

        # Check for required credentials based on provider type
        if name == "kling":
            return bool(cfg.access_key and cfg.secret_key)
        elif name == "tongyi":
            return bool(cfg.api_key)
        elif name == "jimeng":
            return bool(cfg.access_key and cfg.secret_key)
        elif name == "hailuo":
            return bool(cfg.api_key)

        return False


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None or config_path is not None:
        _config = Config(config_path)
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """Reload configuration from disk."""
    global _config
    _config = Config(config_path)
    return _config
