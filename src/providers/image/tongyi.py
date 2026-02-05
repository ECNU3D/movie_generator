"""
Tongyi Image (通义图像) Provider

Supports:
- Text-to-Image: qwen-image-plus, qwen-image-max, wan2.6-t2i
- Image Editing: qwen-image-edit-max, wan2.5-i2i-preview

API Documentation: https://help.aliyun.com/zh/model-studio/
"""

import os
import base64
import mimetypes
import requests
from http import HTTPStatus
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

from .base import (
    ImageProvider,
    ImageTask,
    ImageTaskStatus,
    CharacterViewMode,
    CharacterRef,
)
from ..config import get_config


@dataclass
class TongyiImageModelInfo:
    """Information about a Tongyi image model."""
    name: str
    description: str
    model_type: str  # "t2i" or "edit"
    sync_supported: bool
    sizes: List[str]


# Available models
TONGYI_IMAGE_MODELS = {
    # Text-to-Image models
    "qwen-image-plus": TongyiImageModelInfo(
        name="qwen-image-plus",
        description="通义千问文生图 Plus - 支持复杂文字渲染",
        model_type="t2i",
        sync_supported=True,
        sizes=["1664*928", "928*1664", "1328*1328", "1472*1104", "1104*1472"],
    ),
    "qwen-image-max": TongyiImageModelInfo(
        name="qwen-image-max",
        description="通义千问文生图 Max - 最高质量",
        model_type="t2i",
        sync_supported=True,
        sizes=["1664*928", "928*1664", "1328*1328", "1472*1104", "1104*1472"],
    ),
    "wan2.6-t2i": TongyiImageModelInfo(
        name="wan2.6-t2i",
        description="通义万相2.6文生图 - 写实摄影风格",
        model_type="t2i",
        sync_supported=False,
        sizes=["1024*1024", "1440*810", "810*1440", "1440*1080", "1080*1440"],
    ),
    # Image Editing models
    "qwen-image-edit-max": TongyiImageModelInfo(
        name="qwen-image-edit-max",
        description="通义千问图像编辑 Max - 多图输入输出",
        model_type="edit",
        sync_supported=True,
        sizes=["512-2048"],  # Flexible range
    ),
    "qwen-image-edit-plus": TongyiImageModelInfo(
        name="qwen-image-edit-plus",
        description="通义千问图像编辑 Plus",
        model_type="edit",
        sync_supported=True,
        sizes=["512-2048"],
    ),
    "wan2.5-i2i-preview": TongyiImageModelInfo(
        name="wan2.5-i2i-preview",
        description="通义万相2.5图像编辑 - 多图融合",
        model_type="edit",
        sync_supported=True,
        sizes=["768*768", "1280*1280"],
    ),
}


class TongyiImageProvider(ImageProvider):
    """
    Tongyi Image generation provider.

    Supports:
    - Text-to-Image generation
    - Image editing with multi-image input
    - Character view generation
    - Frame generation for video
    """

    # API endpoints
    BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

    def __init__(self):
        super().__init__()
        self._name = "tongyi"
        self._api_key: Optional[str] = None
        self._t2i_model = "qwen-image-plus"
        self._edit_model = "qwen-image-edit-max"

    def initialize(self, config=None):
        """Initialize with API key."""
        super().initialize(config)
        if self._config and self._config.api_key:
            self._api_key = self._config.api_key
        else:
            self._api_key = os.getenv("DASHSCOPE_API_KEY")

    @property
    def api_key(self) -> str:
        """Get API key."""
        if not self._api_key:
            self.initialize()
        if not self._api_key:
            raise ValueError("Tongyi API key not configured")
        return self._api_key

    def set_models(
        self,
        t2i_model: str = "qwen-image-plus",
        edit_model: str = "qwen-image-edit-max"
    ):
        """Set which models to use for different tasks."""
        if t2i_model in TONGYI_IMAGE_MODELS:
            self._t2i_model = t2i_model
        if edit_model in TONGYI_IMAGE_MODELS:
            self._edit_model = edit_model

    def _get_headers(self) -> dict:
        """Get API request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _encode_image_to_base64(self, file_path: str) -> str:
        """Encode local file to base64."""
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/png"
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"

    def _prepare_image_input(self, image: str) -> str:
        """Prepare image input - handle URL, local path, or base64."""
        if image.startswith("data:"):
            # Already base64
            return image
        elif image.startswith("http://") or image.startswith("https://"):
            # URL - use directly
            return image
        elif os.path.exists(image):
            # Local file - convert to base64
            return self._encode_image_to_base64(image)
        else:
            # Assume it's already a URL or raise error
            return image

    # ========== Core Methods ==========

    def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1664*928",
        n: int = 1,
        model: Optional[str] = None,
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None,
        **kwargs
    ) -> ImageTask:
        """
        Generate image(s) from text prompt using Tongyi.

        Args:
            prompt: Text description
            negative_prompt: Things to avoid
            size: Image size (e.g., "1664*928" for 16:9)
            n: Number of images (1-4)
            model: Model to use (default: qwen-image-plus)
            prompt_extend: Enable smart prompt enhancement
            watermark: Add watermark
            seed: Random seed for reproducibility

        Returns:
            ImageTask with generated images
        """
        model = model or self._t2i_model
        model_info = TONGYI_IMAGE_MODELS.get(model)

        if not model_info:
            raise ValueError(f"Unknown model: {model}")

        # Use DashScope SDK for sync call
        try:
            from dashscope import ImageSynthesis
            import dashscope

            dashscope.base_http_api_url = self.BASE_URL

            rsp = ImageSynthesis.call(
                api_key=self.api_key,
                model=model,
                prompt=prompt,
                negative_prompt=negative_prompt or "",
                n=min(n, 4),
                size=size,
                prompt_extend=prompt_extend,
                watermark=watermark,
                seed=seed,
            )

            if rsp.status_code == HTTPStatus.OK:
                image_urls = [result.url for result in rsp.output.results]
                return ImageTask(
                    task_id=rsp.request_id,
                    provider=self._name,
                    status=ImageTaskStatus.COMPLETED,
                    image_urls=image_urls,
                    completed_at=datetime.now(),
                    metadata={
                        "model": model,
                        "prompt": prompt,
                        "size": size,
                    }
                )
            else:
                return ImageTask(
                    task_id=rsp.request_id or "error",
                    provider=self._name,
                    status=ImageTaskStatus.FAILED,
                    error_message=f"Error {rsp.status_code}: {rsp.code} - {rsp.message}",
                )

        except ImportError:
            # Fallback to HTTP API if SDK not installed
            return self._text_to_image_http(
                prompt=prompt,
                negative_prompt=negative_prompt,
                size=size,
                n=n,
                model=model,
                prompt_extend=prompt_extend,
                watermark=watermark,
                seed=seed,
            )

    def _text_to_image_http(
        self,
        prompt: str,
        negative_prompt: Optional[str],
        size: str,
        n: int,
        model: str,
        prompt_extend: bool,
        watermark: bool,
        seed: Optional[int],
    ) -> ImageTask:
        """HTTP API fallback for text-to-image."""
        url = f"{self.BASE_URL}/services/aigc/text2image/image-synthesis"

        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
            },
            "parameters": {
                "size": size,
                "n": n,
                "prompt_extend": prompt_extend,
                "watermark": watermark,
            }
        }

        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt
        if seed is not None:
            payload["parameters"]["seed"] = seed

        response = requests.post(url, headers=self._get_headers(), json=payload)
        data = response.json()

        if response.status_code == 200 and data.get("output", {}).get("task_status") == "SUCCEEDED":
            results = data.get("output", {}).get("results", [])
            image_urls = [r.get("url") for r in results if r.get("url")]
            return ImageTask(
                task_id=data.get("request_id", ""),
                provider=self._name,
                status=ImageTaskStatus.COMPLETED,
                image_urls=image_urls,
                completed_at=datetime.now(),
                metadata={"model": model, "prompt": prompt}
            )
        else:
            return ImageTask(
                task_id=data.get("request_id", "error"),
                provider=self._name,
                status=ImageTaskStatus.FAILED,
                error_message=data.get("message", str(data)),
            )

    def edit_image(
        self,
        images: List[str],
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: Optional[str] = None,
        n: int = 1,
        model: Optional[str] = None,
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None,
        **kwargs
    ) -> ImageTask:
        """
        Edit image(s) with text instructions.

        Args:
            images: List of image URLs/paths (1-3 images)
            prompt: Editing instructions
            negative_prompt: Things to avoid
            size: Output size
            n: Number of output images (1-6 for edit models)
            model: Model to use
            prompt_extend: Enable smart prompt enhancement
            watermark: Add watermark
            seed: Random seed

        Returns:
            ImageTask with edited images
        """
        model = model or self._edit_model
        model_info = TONGYI_IMAGE_MODELS.get(model)

        if not model_info:
            raise ValueError(f"Unknown model: {model}")

        # Prepare image inputs
        prepared_images = [self._prepare_image_input(img) for img in images[:3]]

        try:
            from dashscope import MultiModalConversation
            import dashscope

            dashscope.base_http_api_url = self.BASE_URL

            # Build messages for multi-modal conversation
            content = []
            for img in prepared_images:
                content.append({"image": img})
            content.append({"text": prompt})

            messages = [{"role": "user", "content": content}]

            params = {
                "api_key": self.api_key,
                "model": model,
                "messages": messages,
                "stream": False,
                "n": min(n, 6),
                "watermark": watermark,
                "prompt_extend": prompt_extend,
            }

            if negative_prompt:
                params["negative_prompt"] = negative_prompt
            if size:
                params["size"] = size
            if seed is not None:
                params["seed"] = seed

            response = MultiModalConversation.call(**params)

            if response.status_code == 200:
                # Extract image URLs from response
                image_urls = []
                choices = response.output.get("choices", [])
                if choices:
                    for content_item in choices[0].get("message", {}).get("content", []):
                        if "image" in content_item:
                            image_urls.append(content_item["image"])

                return ImageTask(
                    task_id=response.request_id,
                    provider=self._name,
                    status=ImageTaskStatus.COMPLETED,
                    image_urls=image_urls,
                    completed_at=datetime.now(),
                    metadata={
                        "model": model,
                        "prompt": prompt,
                        "input_images": len(images),
                    }
                )
            else:
                return ImageTask(
                    task_id=response.request_id or "error",
                    provider=self._name,
                    status=ImageTaskStatus.FAILED,
                    error_message=f"Error {response.status_code}: {response.code} - {response.message}",
                )

        except ImportError:
            return self._edit_image_http(
                images=prepared_images,
                prompt=prompt,
                negative_prompt=negative_prompt,
                size=size,
                n=n,
                model=model,
                prompt_extend=prompt_extend,
                watermark=watermark,
                seed=seed,
            )

    def _edit_image_http(
        self,
        images: List[str],
        prompt: str,
        negative_prompt: Optional[str],
        size: Optional[str],
        n: int,
        model: str,
        prompt_extend: bool,
        watermark: bool,
        seed: Optional[int],
    ) -> ImageTask:
        """HTTP API fallback for image editing."""
        # Use wan2.5-i2i-preview with ImageSynthesis API
        url = f"{self.BASE_URL}/services/aigc/image2image/image-synthesis"

        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "images": images,
            },
            "parameters": {
                "n": n,
                "prompt_extend": prompt_extend,
                "watermark": watermark,
            }
        }

        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt
        if size:
            payload["parameters"]["size"] = size
        if seed is not None:
            payload["parameters"]["seed"] = seed

        response = requests.post(url, headers=self._get_headers(), json=payload)
        data = response.json()

        if response.status_code == 200:
            results = data.get("output", {}).get("results", [])
            image_urls = [r.get("url") for r in results if r.get("url")]
            return ImageTask(
                task_id=data.get("request_id", ""),
                provider=self._name,
                status=ImageTaskStatus.COMPLETED,
                image_urls=image_urls,
                completed_at=datetime.now(),
                metadata={"model": model, "prompt": prompt}
            )
        else:
            return ImageTask(
                task_id=data.get("request_id", "error"),
                provider=self._name,
                status=ImageTaskStatus.FAILED,
                error_message=data.get("message", str(data)),
            )

    # ========== Frame Generation (Override for Tongyi-specific) ==========

    def generate_frame(
        self,
        prompt: str,
        size: str = "1664*928",
        style: str = "cinematic",
        **kwargs
    ) -> ImageTask:
        """
        Generate a frame image for video (first/last frame).

        Args:
            prompt: Scene description
            size: Frame size (default 16:9 for video)
            style: Visual style
            **kwargs: Additional parameters

        Returns:
            ImageTask with frame image
        """
        style_hint = self.STYLE_HINTS.get(style, style)
        enhanced_prompt = f"""{prompt}
Style: {style_hint}, high quality, detailed, professional cinematography, film still."""

        return self.text_to_image(
            prompt=enhanced_prompt,
            size=size,
            n=1,
            prompt_extend=True,
            **kwargs
        )

    def generate_frame_with_character(
        self,
        prompt: str,
        character_reference: str,
        size: str = "1664*928",
        style: str = "cinematic",
        **kwargs
    ) -> ImageTask:
        """
        Generate a frame image with character reference for consistency.

        Args:
            prompt: Scene description
            character_reference: Character reference image URL
            size: Frame size (default 16:9)
            style: Visual style
            **kwargs: Additional parameters

        Returns:
            ImageTask with frame image
        """
        style_hint = self.STYLE_HINTS.get(style, style)
        enhanced_prompt = f"""{prompt}
Keep the character's appearance exactly as in the reference image.
Style: {style_hint}, high quality, detailed, professional cinematography, film still."""

        return self.edit_image(
            images=[character_reference],
            prompt=enhanced_prompt,
            size=size,
            n=1,
            prompt_extend=True,
            **kwargs
        )

    # ========== Character Generation (Override for Tongyi-specific) ==========

    def generate_character_front_view(
        self,
        character_description: str,
        style: str = "realistic",
        size: str = "1328*1328",
        **kwargs
    ) -> ImageTask:
        """
        Generate a front view of a character.

        Args:
            character_description: Detailed character description
            style: Art style
            size: Image size (square recommended)

        Returns:
            ImageTask with character image
        """
        prompt = self._build_single_view_prompt(character_description, "front", style)
        return self.text_to_image(
            prompt=prompt,
            size=size,
            n=1,
            prompt_extend=True,
            **kwargs
        )

    # ========== Scene Composition (Override for Tongyi-specific) ==========

    def composite_character_scene(
        self,
        characters: List[CharacterRef],
        scene_description: str,
        style: str = "cinematic",
        size: str = "1664*928",
        background_image: Optional[str] = None,
        n: int = 1,
        model: Optional[str] = None,
        prompt_extend: bool = True,
        seed: Optional[int] = None,
        **kwargs
    ) -> ImageTask:
        """
        Compose a scene with 1-3 characters (Tongyi-specific).

        Model recommendations:
        - qwen-image-edit-max: Best character consistency, up to 6 outputs
        - qwen-image-edit-plus: Strong character consistency, up to 4 outputs
        - wan2.5-i2i-preview: Good multi-image fusion, up to 4 outputs

        Args:
            characters: List of 1-3 CharacterRef objects
            scene_description: Scene/setting description
            style: Visual style
            size: Output image size
            background_image: Optional background image URL
            n: Number of output images
            model: Model to use (default: qwen-image-edit-max)
            prompt_extend: Enable prompt enhancement
            seed: Random seed for reproducibility
        """
        if model is None:
            model = "qwen-image-edit-max"

        return super().composite_character_scene(
            characters=characters,
            scene_description=scene_description,
            style=style,
            size=size,
            background_image=background_image,
            n=n,
            model=model,
            prompt_extend=prompt_extend,
            seed=seed,
            **kwargs
        )

    # ========== Utility Methods ==========

    @staticmethod
    def get_available_models() -> dict:
        """Get list of available models."""
        return TONGYI_IMAGE_MODELS

    @staticmethod
    def get_supported_sizes(model: str = "qwen-image-plus") -> List[str]:
        """Get supported sizes for a model."""
        model_info = TONGYI_IMAGE_MODELS.get(model)
        if model_info:
            return model_info.sizes
        return []
