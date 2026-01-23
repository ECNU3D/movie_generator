"""
Video Generation Providers Package

This package provides a unified interface for multiple AI video generation platforms:
- Kling AI (可灵)
- Tongyi Wanxiang (通义万相)
- JiMeng AI (即梦AI)
- Hailuo AI / MiniMax (海螺视频)
"""

from .base import VideoProvider, VideoTask, TaskStatus
from .config import Config, get_config
from .kling import KlingProvider
from .tongyi import TongyiProvider
from .jimeng import JimengProvider
from .hailuo import HailuoProvider

__all__ = [
    "VideoProvider",
    "VideoTask",
    "TaskStatus",
    "Config",
    "get_config",
    "KlingProvider",
    "TongyiProvider",
    "JimengProvider",
    "HailuoProvider",
]


def get_provider(name: str) -> VideoProvider:
    """Get a provider instance by name."""
    providers = {
        "kling": KlingProvider,
        "tongyi": TongyiProvider,
        "jimeng": JimengProvider,
        "hailuo": HailuoProvider,
    }

    if name not in providers:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")

    return providers[name]()
