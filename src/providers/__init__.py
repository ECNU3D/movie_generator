"""
AI Generation Providers Package

This package provides unified interfaces for AI generation platforms:

Video Providers:
- Kling AI (可灵)
- Tongyi Wanxiang (通义万相)
- JiMeng AI (即梦AI)
- Hailuo AI / MiniMax (海螺视频)

Image Providers:
- Tongyi Image (通义图像)
"""

# Base classes
from .base import VideoProvider, VideoTask, TaskStatus
from .config import Config, get_config

# Video providers
from .video.kling import KlingProvider
from .video.tongyi import TongyiProvider
from .video.jimeng import JimengProvider
from .video.hailuo import HailuoProvider

# Image providers
from .image.base import ImageProvider, ImageTask, ImageTaskStatus, CharacterViewMode, ImageSize
from .image.tongyi import TongyiImageProvider
from .image.jimeng import JiMengImageProvider

__all__ = [
    # Base - Video
    "VideoProvider",
    "VideoTask",
    "TaskStatus",
    "Config",
    "get_config",
    # Video providers
    "KlingProvider",
    "TongyiProvider",
    "JimengProvider",
    "HailuoProvider",
    # Base - Image
    "ImageProvider",
    "ImageTask",
    "ImageTaskStatus",
    "CharacterViewMode",
    "ImageSize",
    # Image providers
    "TongyiImageProvider",
    "JiMengImageProvider",
]


def get_provider(name: str) -> VideoProvider:
    """Get a video provider instance by name."""
    providers = {
        "kling": KlingProvider,
        "tongyi": TongyiProvider,
        "jimeng": JimengProvider,
        "hailuo": HailuoProvider,
    }

    if name not in providers:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")

    return providers[name]()


def get_image_provider(name: str):
    """Get an image provider instance by name."""
    from .image.tongyi import TongyiImageProvider
    from .image.jimeng import JiMengImageProvider

    providers = {
        "tongyi": TongyiImageProvider,
        "jimeng": JiMengImageProvider,
    }

    if name not in providers:
        raise ValueError(f"Unknown image provider: {name}. Available: {list(providers.keys())}")

    return providers[name]()
