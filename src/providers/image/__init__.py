"""
Image Generation Providers

Providers for various image generation platforms.

API Overview:
=============

Core Methods:
- text_to_image(): Generate image from text prompt
- edit_image(): Edit existing image with text instructions

Character Generation:
- generate_character_front_view(): Generate character reference image
- generate_character_side_view(): Generate character side view
- generate_character_back_view(): Generate character back view
- generate_character_three_views(): Generate three separate view images
- generate_character_sheet(): Generate single image with three views
- generate_character_turnaround(): Generate game-style turnaround sheet

Frame Generation:
- generate_frame(): Generate video frame (first/last frame)
- generate_frame_with_character(): Generate frame with character reference

Image Download:
- download_image(): Download single image from URL
- download_task_images(): Download all images from a task

Utility:
- get_available_models(): List available models
- get_supported_sizes(): Get supported sizes for a model
- test_connection(): Test provider connection
"""

from .base import (
    ImageProvider,
    ImageTask,
    ImageTaskStatus,
    CharacterViewMode,
    CharacterRef,
    ArtStyle,
    ImageSize,
)
from .tongyi import TongyiImageProvider, TONGYI_IMAGE_MODELS
from .jimeng import JiMengImageProvider, JIMENG_IMAGE_MODELS

__all__ = [
    # Base classes
    "ImageProvider",
    "ImageTask",
    "ImageTaskStatus",
    "CharacterViewMode",
    "CharacterRef",
    "ArtStyle",
    "ImageSize",
    # Providers
    "TongyiImageProvider",
    "TONGYI_IMAGE_MODELS",
    "JiMengImageProvider",
    "JIMENG_IMAGE_MODELS",
]
