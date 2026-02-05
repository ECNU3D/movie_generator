"""
Base classes for image generation providers.

All image provider implementations should inherit from ImageProvider
and implement the required abstract methods.

API Overview:
=============

Core Methods (Abstract):
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

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, List
import os
import requests
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath

from ..config import get_config, ProviderConfig


class ImageTaskStatus(Enum):
    """Image generation task status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CharacterViewMode(Enum):
    """Character view generation mode."""
    SINGLE_IMAGE_THREE_VIEWS = "single_image_three_views"  # One image with front/side/back
    THREE_SEPARATE_IMAGES = "three_separate_images"  # Three separate images
    TURNAROUND_SHEET = "turnaround_sheet"  # Character turnaround/reference sheet


class ArtStyle(Enum):
    """Common art styles for image generation."""
    REALISTIC = "realistic"
    ANIME = "anime"
    CARTOON = "cartoon"
    THREE_D = "3d"
    WATERCOLOR = "watercolor"
    OIL_PAINTING = "oil_painting"
    SKETCH = "sketch"
    PIXEL_ART = "pixel_art"
    CINEMATIC = "cinematic"


class ImageSize(Enum):
    """Common image sizes."""
    SQUARE_1024 = "1024*1024"  # 1:1
    LANDSCAPE_16_9 = "1280*720"  # 16:9
    PORTRAIT_9_16 = "720*1280"  # 9:16
    LANDSCAPE_4_3 = "1280*960"  # 4:3
    PORTRAIT_3_4 = "960*1280"  # 3:4
    # Tongyi Qwen-Image specific sizes
    QWEN_16_9 = "1664*928"
    QWEN_9_16 = "928*1664"
    QWEN_1_1 = "1328*1328"
    QWEN_4_3 = "1472*1104"
    QWEN_3_4 = "1104*1472"


@dataclass
class CharacterRef:
    """A character reference for scene composition."""
    name: str           # Character name/label (e.g., "小明", "Alice")
    image_url: str      # Front-view reference image URL or local path
    action: str = ""    # What the character is doing (e.g., "向女主角挥手")
    position: str = ""  # Optional spatial hint (e.g., "左侧", "中间")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "image_url": self.image_url,
            "action": self.action,
            "position": self.position,
        }


@dataclass
class ImageTask:
    """Represents an image generation task."""
    task_id: str
    provider: str
    status: ImageTaskStatus = ImageTaskStatus.PENDING
    image_urls: List[str] = field(default_factory=list)
    local_paths: List[str] = field(default_factory=list)  # Paths after download
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    def is_completed(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in (ImageTaskStatus.COMPLETED, ImageTaskStatus.FAILED)

    def is_successful(self) -> bool:
        """Check if task completed successfully."""
        return self.status == ImageTaskStatus.COMPLETED and len(self.image_urls) > 0

    @property
    def image_url(self) -> Optional[str]:
        """Get the first image URL (convenience property)."""
        return self.image_urls[0] if self.image_urls else None

    @property
    def local_path(self) -> Optional[str]:
        """Get the first local path (convenience property)."""
        return self.local_paths[0] if self.local_paths else None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "provider": self.provider,
            "status": self.status.value,
            "image_urls": self.image_urls,
            "image_url": self.image_url,
            "local_paths": self.local_paths,
            "local_path": self.local_path,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


class ImageProvider(ABC):
    """
    Abstract base class for image generation providers.

    All providers must implement:
    - text_to_image: Generate image from text prompt
    - edit_image: Edit an existing image with text instructions
    """

    # Style hints for prompt building
    STYLE_HINTS = {
        "realistic": "photorealistic, highly detailed, professional photography",
        "anime": "anime style, Japanese animation, detailed character design",
        "cartoon": "cartoon style, vibrant colors, clean lines",
        "3d": "3D rendered, Pixar style, high quality CG",
        "watercolor": "watercolor painting style, soft colors, artistic",
        "oil_painting": "oil painting style, rich colors, textured brushstrokes",
        "sketch": "pencil sketch, detailed linework, artistic",
        "pixel_art": "pixel art style, retro game aesthetic",
        "cinematic": "cinematic, film still, professional cinematography, dramatic lighting",
    }

    def __init__(self):
        self._config: Optional[ProviderConfig] = None
        self._name: str = ""

    @property
    def name(self) -> str:
        """Provider name."""
        return self._name

    @property
    def config(self) -> ProviderConfig:
        """Provider configuration."""
        if self._config is None:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        return self._config

    def initialize(self, config: Optional[ProviderConfig] = None):
        """Initialize the provider with configuration."""
        if config is not None:
            self._config = config
        else:
            self._config = get_config().get_provider_config(self._name)

    def is_configured(self) -> bool:
        """Check if provider has valid credentials."""
        return get_config().is_provider_configured(self._name)

    # ========== Core Methods (Abstract) ==========

    @abstractmethod
    def text_to_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1280*720",
        n: int = 1,
        **kwargs
    ) -> ImageTask:
        """
        Generate image(s) from text prompt.

        Args:
            prompt: Text description for image generation
            negative_prompt: Things to avoid in the image
            size: Image size in format "width*height"
            n: Number of images to generate
            **kwargs: Provider-specific parameters

        Returns:
            ImageTask with image URLs
        """
        pass

    @abstractmethod
    def edit_image(
        self,
        images: List[str],
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: Optional[str] = None,
        n: int = 1,
        **kwargs
    ) -> ImageTask:
        """
        Edit image(s) with text instructions.

        Args:
            images: List of image URLs or base64 data to edit
            prompt: Text instructions for editing
            negative_prompt: Things to avoid
            size: Output image size
            n: Number of output images
            **kwargs: Provider-specific parameters

        Returns:
            ImageTask with edited image URLs
        """
        pass

    # ========== Image Download Methods ==========

    def download_image(
        self,
        url: str,
        save_dir: str = "./output",
        filename: Optional[str] = None
    ) -> str:
        """
        Download image from URL and save locally.

        Args:
            url: Image URL to download
            save_dir: Directory to save the image
            filename: Optional custom filename (without extension)

        Returns:
            Path to the downloaded file
        """
        os.makedirs(save_dir, exist_ok=True)

        # Get original filename from URL
        original_name = PurePosixPath(unquote(urlparse(url).path)).parts[-1]

        if filename:
            # Keep the original extension
            ext = os.path.splitext(original_name)[1] or ".png"
            file_name = f"{filename}{ext}"
        else:
            file_name = original_name

        file_path = os.path.join(save_dir, file_name)

        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path

    def download_task_images(
        self,
        task: ImageTask,
        save_dir: str = "./output",
        prefix: Optional[str] = None
    ) -> List[str]:
        """
        Download all images from an ImageTask.

        Args:
            task: ImageTask containing image URLs
            save_dir: Directory to save images
            prefix: Optional prefix for filenames

        Returns:
            List of paths to downloaded files
        """
        if not task.is_successful():
            raise ValueError(f"Task not successful: {task.error_message}")

        downloaded = []
        for i, url in enumerate(task.image_urls):
            if prefix:
                filename = f"{prefix}_{i+1}" if len(task.image_urls) > 1 else prefix
            else:
                filename = None
            path = self.download_image(url, save_dir, filename)
            downloaded.append(path)

        # Update task with local paths
        task.local_paths = downloaded
        return downloaded

    # ========== Frame Generation Methods ==========

    def generate_frame(
        self,
        prompt: str,
        size: str = "1664*928",
        style: str = "cinematic",
        **kwargs
    ) -> ImageTask:
        """
        Generate a frame image for video (first/last frame) from text only.

        Args:
            prompt: Scene description
            size: Frame size (default 16:9)
            style: Visual style (default: cinematic)
            **kwargs: Additional parameters

        Returns:
            ImageTask with frame image
        """
        style_hint = self.STYLE_HINTS.get(style, style)
        enhanced_prompt = f"""{prompt}
Style: {style_hint}, high quality, detailed, film still."""

        return self.text_to_image(
            prompt=enhanced_prompt,
            size=size,
            n=1,
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
Style: {style_hint}, high quality, detailed, film still."""

        return self.edit_image(
            images=[character_reference],
            prompt=enhanced_prompt,
            size=size,
            n=1,
            **kwargs
        )

    # ========== Character Generation Methods ==========

    def generate_character_front_view(
        self,
        character_description: str,
        style: str = "realistic",
        size: str = "1328*1328",
        **kwargs
    ) -> ImageTask:
        """
        Generate a front view of a character (reference image).

        Args:
            character_description: Detailed character description
            style: Art style (realistic, anime, cartoon, etc.)
            size: Image size (square recommended)
            **kwargs: Additional parameters

        Returns:
            ImageTask with character front view image
        """
        prompt = self._build_single_view_prompt(character_description, "front", style)
        return self.text_to_image(
            prompt=prompt,
            size=size,
            n=1,
            **kwargs
        )

    def generate_character_side_view(
        self,
        character_reference: str,
        character_description: str,
        style: str = "realistic",
        size: str = "1328*1328",
        **kwargs
    ) -> ImageTask:
        """
        Generate a side view (profile) of a character.

        Args:
            character_reference: Character reference image URL
            character_description: Character description
            style: Art style
            size: Image size
            **kwargs: Additional parameters

        Returns:
            ImageTask with character side view image
        """
        prompt = self._build_single_view_prompt(character_description, "side", style)
        return self.edit_image(
            images=[character_reference],
            prompt=prompt,
            size=size,
            n=1,
            **kwargs
        )

    def generate_character_back_view(
        self,
        character_reference: str,
        character_description: str,
        style: str = "realistic",
        size: str = "1328*1328",
        **kwargs
    ) -> ImageTask:
        """
        Generate a back view of a character.

        Args:
            character_reference: Character reference image URL
            character_description: Character description
            style: Art style
            size: Image size
            **kwargs: Additional parameters

        Returns:
            ImageTask with character back view image
        """
        prompt = self._build_single_view_prompt(character_description, "back", style)
        return self.edit_image(
            images=[character_reference],
            prompt=prompt,
            size=size,
            n=1,
            **kwargs
        )

    def generate_character_three_views(
        self,
        character_reference: str,
        character_description: str,
        style: str = "realistic",
        size: str = "1328*1328",
        **kwargs
    ) -> ImageTask:
        """
        Generate three separate view images (side, front, back).

        This makes 3 separate API calls to ensure each image shows only one view.

        Args:
            character_reference: Character reference image URL
            character_description: Character description
            style: Art style
            size: Image size for each view
            **kwargs: Additional parameters

        Returns:
            ImageTask with 3 image URLs [side, front, back]
        """
        view_types = ["side", "front", "back"]
        all_image_urls = []
        last_task_id = ""

        for view_type in view_types:
            prompt = self._build_single_view_prompt(character_description, view_type, style)
            task = self.edit_image(
                images=[character_reference],
                prompt=prompt,
                size=size,
                n=1,
                **kwargs
            )
            if task.is_successful():
                all_image_urls.extend(task.image_urls)
                last_task_id = task.task_id
            else:
                return task  # Return failed task

        return ImageTask(
            task_id=last_task_id,
            provider=self._name,
            status=ImageTaskStatus.COMPLETED,
            image_urls=all_image_urls,
            completed_at=datetime.now(),
            metadata={
                "type": "three_separate_views",
                "views": view_types,
            }
        )

    def generate_character_sheet(
        self,
        character_reference: str,
        character_description: str,
        style: str = "realistic",
        size: str = "1664*928",
        **kwargs
    ) -> ImageTask:
        """
        Generate a single image containing three views (side, front, back).

        Args:
            character_reference: Character reference image URL
            character_description: Character description
            style: Art style
            size: Image size (wide format recommended)
            **kwargs: Additional parameters

        Returns:
            ImageTask with single image containing three views
        """
        prompt = self._build_character_sheet_prompt(character_description, style)
        return self.edit_image(
            images=[character_reference],
            prompt=prompt,
            size=size,
            n=1,
            **kwargs
        )

    def generate_character_turnaround(
        self,
        character_reference: str,
        character_description: str,
        style: str = "realistic",
        size: str = "1664*928",
        **kwargs
    ) -> ImageTask:
        """
        Generate a professional character turnaround sheet (game/animation style).

        Shows character from multiple angles: front, 3/4, side, 3/4 back, back.

        Args:
            character_reference: Character reference image URL
            character_description: Character description
            style: Art style
            size: Image size (wide format recommended)
            **kwargs: Additional parameters

        Returns:
            ImageTask with character turnaround sheet
        """
        prompt = self._build_turnaround_prompt(character_description, style)
        return self.edit_image(
            images=[character_reference],
            prompt=prompt,
            size=size,
            n=1,
            **kwargs
        )

    # ========== Scene Composition Methods ==========

    def composite_character_scene(
        self,
        characters: List[CharacterRef],
        scene_description: str,
        style: str = "cinematic",
        size: str = "1664*928",
        background_image: Optional[str] = None,
        n: int = 1,
        **kwargs
    ) -> ImageTask:
        """
        Compose a scene with 1-3 characters from their reference images.

        Each character's front-view reference image is passed as an input image.
        The prompt references characters as 图1, 图2, 图3 and describes
        the scene setting plus each character's action.

        Args:
            characters: List of 1-3 CharacterRef objects
            scene_description: Description of the scene/setting/background
            style: Visual style (cinematic, realistic, anime, etc.)
            size: Output image size (default 16:9 for cinematic)
            background_image: Optional background/scene image URL (only used
                             when len(characters) <= 2, since API max is 3 images)
            n: Number of output images
            **kwargs: Provider-specific parameters (model, seed, etc.)

        Returns:
            ImageTask with composed scene image(s)

        Raises:
            ValueError: If characters list is empty or exceeds 3
        """
        if not characters or len(characters) > 3:
            raise ValueError(
                f"Must provide 1-3 characters, got {len(characters) if characters else 0}"
            )

        # Build image list: characters first, then optional background
        images = [c.image_url for c in characters]

        use_bg = background_image and len(images) < 3
        if use_bg:
            images.append(background_image)

        # Build prompt
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

    # ========== Legacy Methods (for backward compatibility) ==========

    def generate_character_views(
        self,
        front_image_url: str,
        character_description: str,
        mode: CharacterViewMode = CharacterViewMode.SINGLE_IMAGE_THREE_VIEWS,
        style: str = "realistic",
        size: Optional[str] = None,
        **kwargs
    ) -> ImageTask:
        """
        Generate character views based on mode.

        DEPRECATED: Use specific methods instead:
        - generate_character_three_views() for THREE_SEPARATE_IMAGES
        - generate_character_sheet() for SINGLE_IMAGE_THREE_VIEWS
        - generate_character_turnaround() for TURNAROUND_SHEET

        Args:
            front_image_url: URL of the character's front view image
            character_description: Character description for reference
            mode: View generation mode
            style: Art style
            size: Image size
            **kwargs: Additional parameters

        Returns:
            ImageTask with character view images
        """
        if mode == CharacterViewMode.THREE_SEPARATE_IMAGES:
            return self.generate_character_three_views(
                character_reference=front_image_url,
                character_description=character_description,
                style=style,
                size=size or "1328*1328",
                **kwargs
            )
        elif mode == CharacterViewMode.SINGLE_IMAGE_THREE_VIEWS:
            return self.generate_character_sheet(
                character_reference=front_image_url,
                character_description=character_description,
                style=style,
                size=size or "1664*928",
                **kwargs
            )
        else:  # TURNAROUND_SHEET
            return self.generate_character_turnaround(
                character_reference=front_image_url,
                character_description=character_description,
                style=style,
                size=size or "1664*928",
                **kwargs
            )

    # ========== Prompt Building Methods ==========

    def _build_scene_composition_prompt(
        self,
        characters: List[CharacterRef],
        scene_description: str,
        style: str,
        has_background_image: bool,
        total_images: int,
    ) -> str:
        """Build prompt for multi-character scene composition."""
        style_hint = self.STYLE_HINTS.get(style, style)

        # Build character reference section
        char_parts = []
        for i, char in enumerate(characters):
            img_label = f"图{i + 1}"
            parts = [f"- {img_label}中的人物是「{char.name}」"]
            if char.position:
                parts.append(f"位于{char.position}")
            if char.action:
                parts.append(char.action)
            char_parts.append("，".join(parts))
        char_section = "\n".join(char_parts)

        # Background reference
        bg_section = ""
        if has_background_image:
            bg_idx = len(characters) + 1
            bg_section = f"\n场景背景参考图{bg_idx}中的环境。"

        # Interaction hint for multi-character
        interaction_hint = ""
        if len(characters) == 2:
            interaction_hint = "\n两个角色之间应有自然的空间关系和互动感。"
        elif len(characters) == 3:
            interaction_hint = "\n三个角色应合理布局在画面中，保持自然的空间关系。"

        prompt = f"""将以下角色组合到同一场景中，保持每个角色的外貌特征与参考图完全一致。

角色参考:
{char_section}

场景设定: {scene_description}{bg_section}{interaction_hint}

要求:
- 保持每个角色的面部特征、发型、服装与其参考图一致
- 所有角色出现在同一个连贯的场景中
- 构图协调，光影统一
- 风格: {style_hint}"""

        return prompt

    def _build_single_view_prompt(
        self,
        description: str,
        view_type: str,
        style: str
    ) -> str:
        """Build prompt for single view generation."""
        style_hint = self.STYLE_HINTS.get(style, style)

        prompts = {
            "front": f"""Character portrait, front view, facing camera directly.
{description}
Style: {style_hint}
Full body visible, centered composition, clean background, character design reference.""",

            "side": f"""Character portrait, side view (profile), looking left.
Show the character from a 90-degree side angle.
{description}
Style: {style_hint}
Full body visible, clean background, character design reference.
Keep exact same character appearance, clothing, and proportions.""",

            "back": f"""Character portrait, back view, facing away from camera.
Show the character from behind.
{description}
Style: {style_hint}
Full body visible, clean background, character design reference.
Keep exact same character appearance, clothing, and proportions.""",
        }

        return prompts.get(view_type, prompts["front"])

    def _build_character_sheet_prompt(self, description: str, style: str) -> str:
        """Build prompt for character sheet (three views in one image)."""
        style_hint = self.STYLE_HINTS.get(style, style)
        return f"""Generate a character reference sheet showing three views of the same character in one image:
- Left: Side view (profile)
- Center: Front view (facing camera)
- Right: Back view
Character: {description}
Style: {style_hint}, character design sheet, clean white background, professional reference art.
Keep exact same character appearance, clothing, and proportions in all views."""

    def _build_turnaround_prompt(self, description: str, style: str) -> str:
        """Build prompt for character turnaround sheet."""
        style_hint = self.STYLE_HINTS.get(style, style)
        return f"""Generate a professional character turnaround sheet showing the character from multiple angles:
Front view, 3/4 view, side view, 3/4 back view, back view.
All views in a single horizontal composition.
Character: {description}
Style: {style_hint}, character design turnaround, clean background, professional game/animation character asset.
Keep exact same character appearance, clothing, and proportions in all views."""

    # Legacy method for backward compatibility
    def _build_character_front_prompt(self, description: str, style: str) -> str:
        """Build prompt for character front view generation."""
        return self._build_single_view_prompt(description, "front", style)

    def _build_character_views_prompt(
        self,
        description: str,
        mode: CharacterViewMode,
        style: str,
        view_type: str = None
    ) -> str:
        """Build prompt for character multi-view generation (legacy)."""
        if mode == CharacterViewMode.SINGLE_IMAGE_THREE_VIEWS:
            return self._build_character_sheet_prompt(description, style)
        elif mode == CharacterViewMode.THREE_SEPARATE_IMAGES:
            if view_type:
                return self._build_single_view_prompt(description, view_type, style)
            return self._build_single_view_prompt(description, "front", style)
        else:  # TURNAROUND_SHEET
            return self._build_turnaround_prompt(description, style)

    # ========== Utility Methods ==========

    @staticmethod
    def get_available_models() -> dict:
        """Get list of available models. Override in subclass."""
        return {}

    @staticmethod
    def get_supported_sizes(model: str = None) -> List[str]:
        """Get supported sizes for a model. Override in subclass."""
        return []

    def test_connection(self) -> dict:
        """Test the connection to the provider."""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "Provider not configured. Please set API keys.",
                }
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
