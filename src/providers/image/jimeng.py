"""
JiMeng AI (即梦/Seedream) Image Generation Provider

Uses Volcengine Ark platform's OpenAI-compatible REST API.

API Documentation: https://www.volcengine.com/docs/

Supported Models:
- doubao-seedream-4-5-251128: Seedream 4.5 (latest, strongest)
- doubao-seedream-4-0-250828: Seedream 4.0 (balanced)

Key Features:
- Single endpoint for both text-to-image and image editing
- Up to 14 reference images
- Sequential image generation for multi-image output
- Synchronous response (no polling needed)
"""

import os
import uuid
import base64
import mimetypes
import logging
import requests
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from .base import (
    ImageProvider,
    ImageTask,
    ImageTaskStatus,
    CharacterRef,
)
from ..config import get_config

logger = logging.getLogger(__name__)


@dataclass
class JiMengImageModelInfo:
    """Information about a JiMeng/Seedream image model."""
    name: str
    description: str
    model_type: str  # "t2i" - same endpoint handles both t2i and i2i
    sizes: List[str]
    max_input_images: int = 14


JIMENG_IMAGE_MODELS = {
    "doubao-seedream-4-5-251128": JiMengImageModelInfo(
        name="doubao-seedream-4-5-251128",
        description="即梦 Seedream 4.5 - 最新最强，编辑一致性佳",
        model_type="t2i",
        sizes=["2K", "4K", "2560x1440", "1440x2560", "2048x2048", "3840x2160"],
    ),
    "doubao-seedream-4-0-250828": JiMengImageModelInfo(
        name="doubao-seedream-4-0-250828",
        description="即梦 Seedream 4.0 - 平衡预算与质量",
        model_type="t2i",
        sizes=["1K", "2K", "4K", "1280x720", "720x1280", "1024x1024", "2048x2048"],
    ),
}

# Map common base-class sizes (WIDTH*HEIGHT) to JiMeng-compatible sizes
_SIZE_MAPPING = {
    "1664*928": "2560x1440",
    "928*1664": "1440x2560",
    "1328*1328": "2048x2048",
    "1280*720": "2560x1440",
    "720*1280": "1440x2560",
    "1024*1024": "2048x2048",
    "1472*1104": "2K",
    "1104*1472": "2K",
}


class JiMengImageProvider(ImageProvider):
    """
    JiMeng/Seedream image generation provider.

    Uses Volcengine Ark platform's OpenAI-compatible REST API.
    Endpoint: POST https://ark.cn-beijing.volces.com/api/v3/images/generations
    Auth: Bearer token (ARK_API_KEY)
    """

    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    IMAGES_ENDPOINT = f"{BASE_URL}/images/generations"
    DEFAULT_MODEL = "doubao-seedream-4-5-251128"

    def __init__(self):
        super().__init__()
        self._name = "jimeng"
        self._ark_api_key: Optional[str] = None
        self._default_model = self.DEFAULT_MODEL

    def initialize(self, config=None):
        """Initialize with Ark API key from config or environment."""
        try:
            super().initialize(config)
            if self._config and self._config.ark_api_key:
                self._ark_api_key = self._config.ark_api_key
        except (ValueError, RuntimeError):
            pass

        if not self._ark_api_key:
            self._ark_api_key = os.getenv("ARK_API_KEY")

    def is_configured(self) -> bool:
        """Check if JiMeng Image provider has a valid Ark API key."""
        return bool(self._ark_api_key)

    # ========== Internal Methods ==========

    def _get_headers(self) -> dict:
        """Get API request headers."""
        if not self._ark_api_key:
            raise RuntimeError("ARK_API_KEY not configured. Set it in config or ARK_API_KEY env var.")
        return {
            "Authorization": f"Bearer {self._ark_api_key}",
            "Content-Type": "application/json",
        }

    def _convert_size(self, size: str) -> str:
        """Convert base class size format (WIDTH*HEIGHT) to JiMeng format.

        Handles:
        - Preset names: "1K", "2K", "4K" -> pass through
        - JiMeng format: "2048x2048" -> pass through
        - Base format: "1664*928" -> map to JiMeng equivalent or convert * to x
        """
        if size in ("1K", "2K", "4K"):
            return size
        if "x" in size and "*" not in size:
            return size
        if size in _SIZE_MAPPING:
            return _SIZE_MAPPING[size]
        if "*" in size:
            return size.replace("*", "x")
        return size

    def _prepare_image(self, image: str) -> str:
        """Prepare image input - handle URL or local path."""
        if image.startswith(("http://", "https://")):
            return image
        if os.path.exists(image):
            mime_type, _ = mimetypes.guess_type(image)
            if not mime_type or not mime_type.startswith("image/"):
                mime_type = "image/png"
            with open(image, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime_type};base64,{encoded}"
        return image

    def _make_request(self, payload: dict, timeout: int = 120) -> dict:
        """Make API request to Ark endpoint.

        Returns parsed JSON response.
        Raises Exception on error.
        """
        response = requests.post(
            self.IMAGES_ENDPOINT,
            headers=self._get_headers(),
            json=payload,
            timeout=timeout,
        )

        result = response.json()

        # Check for API errors
        if "error" in result:
            error = result["error"]
            code = error.get("code", "unknown")
            message = error.get("message", "Unknown error")
            raise Exception(f"JiMeng API Error [{code}]: {message}")

        response.raise_for_status()
        return result

    # ========== Core Methods ==========

    def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "2K",
        n: int = 1,
        model: Optional[str] = None,
        watermark: bool = False,
        optimize_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> ImageTask:
        """
        Generate image(s) from text prompt.

        Args:
            prompt: Text description (max 300 Chinese chars / 600 English words)
            negative_prompt: Ignored (JiMeng does not support negative prompts)
            size: Image size - preset ("2K", "4K") or pixel ("2048x2048")
            n: Number of images (uses sequential generation for n > 1)
            model: Model ID (default: doubao-seedream-4-5-251128)
            watermark: Add "AI Generated" watermark
            optimize_prompt: Prompt optimization mode ("standard" or "fast")
            seed: Random seed for reproducibility
            **kwargs: Additional parameters

        Returns:
            ImageTask with image URLs
        """
        if negative_prompt:
            logger.debug("JiMeng does not support negative_prompt, ignoring")

        model = model or self._default_model
        converted_size = self._convert_size(size)

        payload = {
            "model": model,
            "prompt": prompt[:900],
            "size": converted_size,
            "response_format": "url",
            "watermark": watermark,
        }

        if n > 1:
            payload["sequential_image_generation"] = "auto"
            payload["sequential_image_generation_options"] = {"max_images": n}
        else:
            payload["sequential_image_generation"] = "disabled"

        if seed is not None:
            payload["seed"] = seed

        if optimize_prompt:
            payload["optimize_prompt_options"] = {"mode": optimize_prompt}

        task_id = str(uuid.uuid4())

        try:
            result = self._make_request(payload)
            image_urls = [item["url"] for item in result.get("data", [])]

            return ImageTask(
                task_id=task_id,
                provider=self._name,
                status=ImageTaskStatus.COMPLETED,
                image_urls=image_urls,
                completed_at=datetime.now(),
                metadata={
                    "model": model,
                    "size": converted_size,
                    "prompt": prompt,
                },
            )
        except Exception as e:
            return ImageTask(
                task_id=task_id,
                provider=self._name,
                status=ImageTaskStatus.FAILED,
                error_message=str(e),
            )

    def edit_image(
        self,
        images: List[str],
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: Optional[str] = None,
        n: int = 1,
        model: Optional[str] = None,
        watermark: bool = False,
        optimize_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> ImageTask:
        """
        Edit image(s) with text instructions.

        Uses the same endpoint as text_to_image, with added `image` parameter.
        Supports up to 14 input images.

        Args:
            images: List of image URLs or local paths (1-14 images)
            prompt: Text instructions for editing
            negative_prompt: Ignored (JiMeng does not support negative prompts)
            size: Output image size (optional)
            n: Number of output images
            model: Model ID (default: doubao-seedream-4-5-251128)
            watermark: Add watermark
            optimize_prompt: Prompt optimization mode
            seed: Random seed
            **kwargs: Additional parameters

        Returns:
            ImageTask with edited image URLs
        """
        if negative_prompt:
            logger.debug("JiMeng does not support negative_prompt, ignoring")

        if not images:
            raise ValueError("At least one image is required")
        if len(images) > 14:
            raise ValueError(f"JiMeng supports at most 14 input images, got {len(images)}")

        model = model or self._default_model

        # Prepare images
        prepared = [self._prepare_image(img) for img in images]
        image_param = prepared[0] if len(prepared) == 1 else prepared

        payload = {
            "model": model,
            "prompt": prompt[:900],
            "image": image_param,
            "response_format": "url",
            "watermark": watermark,
            "sequential_image_generation": "disabled",
        }

        if size:
            payload["size"] = self._convert_size(size)

        if n > 1:
            payload["sequential_image_generation"] = "auto"
            payload["sequential_image_generation_options"] = {"max_images": n}

        if seed is not None:
            payload["seed"] = seed

        if optimize_prompt:
            payload["optimize_prompt_options"] = {"mode": optimize_prompt}

        task_id = str(uuid.uuid4())

        try:
            result = self._make_request(payload)
            image_urls = [item["url"] for item in result.get("data", [])]

            return ImageTask(
                task_id=task_id,
                provider=self._name,
                status=ImageTaskStatus.COMPLETED,
                image_urls=image_urls,
                completed_at=datetime.now(),
                metadata={
                    "model": model,
                    "prompt": prompt,
                    "input_images": len(images),
                },
            )
        except Exception as e:
            return ImageTask(
                task_id=task_id,
                provider=self._name,
                status=ImageTaskStatus.FAILED,
                error_message=str(e),
            )

    # ========== Scene Composition Override ==========

    def composite_character_scene(
        self,
        characters: List[CharacterRef],
        scene_description: str,
        style: str = "cinematic",
        size: str = "2K",
        background_image: Optional[str] = None,
        n: int = 1,
        **kwargs
    ) -> ImageTask:
        """
        Compose a scene with up to 14 characters (JiMeng supports up to 14 input images).

        Args:
            characters: List of CharacterRef objects (1-14, or 1-13 with background)
            scene_description: Description of the scene/setting
            style: Visual style
            size: Output image size
            background_image: Optional background reference image
            n: Number of output images
            **kwargs: Additional parameters (model, seed, etc.)

        Returns:
            ImageTask with composed scene image(s)
        """
        max_chars = 13 if background_image else 14
        if not characters or len(characters) > max_chars:
            raise ValueError(
                f"Must provide 1-{max_chars} characters, got {len(characters) if characters else 0}"
            )

        images = [c.image_url for c in characters]

        use_bg = background_image and len(images) < 14
        if use_bg:
            images.append(background_image)

        prompt = self._build_scene_composition_prompt(
            characters=characters,
            scene_description=scene_description,
            style=style,
            has_background_image=bool(use_bg),
            total_images=len(images),
        )

        return self.edit_image(
            images=images,
            prompt=prompt,
            size=size,
            n=n,
            **kwargs
        )

    # ========== Utility Methods ==========

    @staticmethod
    def get_available_models() -> dict:
        """Get list of available JiMeng image models."""
        return JIMENG_IMAGE_MODELS

    @staticmethod
    def get_supported_sizes(model: str = "doubao-seedream-4-5-251128") -> List[str]:
        """Get supported sizes for a model."""
        model_info = JIMENG_IMAGE_MODELS.get(model)
        if model_info:
            return model_info.sizes
        return []

    def test_connection(self) -> dict:
        """Test connection by verifying API key is configured."""
        if not self._ark_api_key:
            return {
                "success": False,
                "error": "ARK_API_KEY not configured",
            }
        return {
            "success": True,
            "message": "API key configured",
            "api_key_preview": f"{self._ark_api_key[:8]}...",
            "supported_models": list(JIMENG_IMAGE_MODELS.keys()),
        }
