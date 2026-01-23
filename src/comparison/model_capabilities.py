"""
Model Capabilities Mapping for Video Generation Providers

This module defines the capabilities of each model across all providers,
including supported durations, resolutions, aspect ratios, and features.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class GenerationType(Enum):
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"
    FIRST_LAST_FRAME = "first_last_frame"
    SUBJECT_REFERENCE = "subject_reference"
    VIDEO_REFERENCE = "video_reference"


@dataclass
class ModelCapability:
    """Represents a model's capabilities."""
    provider: str
    model_id: str
    display_name: str
    generation_types: List[GenerationType]
    durations: List[int]  # in seconds
    resolutions: List[str]
    aspect_ratios: List[str]
    modes: List[str] = field(default_factory=list)  # e.g., ["std", "pro"]
    supports_audio: bool = False
    supports_camera_control: bool = False
    cost_per_second: float = 0.0  # Estimated cost in CNY
    description: str = ""


# All model capabilities
MODEL_CAPABILITIES: Dict[str, Dict[str, ModelCapability]] = {
    "kling": {
        "kling-video-o1": ModelCapability(
            provider="kling",
            model_id="kling-video-o1",
            display_name="Kling Omni-Video O1",
            generation_types=[
                GenerationType.TEXT_TO_VIDEO,
                GenerationType.IMAGE_TO_VIDEO,
                GenerationType.FIRST_LAST_FRAME,
                GenerationType.VIDEO_REFERENCE,
            ],
            durations=[5, 10],  # 3-10 for reference mode, but 5/10 for t2v/i2v
            resolutions=["720P", "1080P"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            modes=["std", "pro"],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.5,
            description="多功能视频生成模型，支持文生视频、图生视频、视频参考等"
        ),
    },
    "tongyi": {
        "wan2.6-t2v": ModelCapability(
            provider="tongyi",
            model_id="wan2.6-t2v",
            display_name="万相2.6 文生视频",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[5],
            resolutions=["720P", "1080P"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            modes=[],
            supports_audio=True,
            supports_camera_control=False,
            cost_per_second=0.4,
            description="最新文生视频模型，支持多镜头叙事和自动配音"
        ),
        "wan2.5-t2v-preview": ModelCapability(
            provider="tongyi",
            model_id="wan2.5-t2v-preview",
            display_name="万相2.5 Preview",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[5],
            resolutions=["720P", "1080P"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            modes=[],
            supports_audio=True,
            supports_camera_control=False,
            cost_per_second=0.35,
            description="万相2.5预览版，支持有声视频"
        ),
        "wan2.2-t2v-plus": ModelCapability(
            provider="tongyi",
            model_id="wan2.2-t2v-plus",
            display_name="万相2.2 专业版",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[5],
            resolutions=["720P", "1080P"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.3,
            description="万相2.2专业版，无声视频"
        ),
        "wanx2.1-t2v-turbo": ModelCapability(
            provider="tongyi",
            model_id="wanx2.1-t2v-turbo",
            display_name="万相2.1 极速版",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[5],
            resolutions=["720P"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.2,
            description="万相2.1极速版，快速生成"
        ),
        "wanx2.1-t2v-plus": ModelCapability(
            provider="tongyi",
            model_id="wanx2.1-t2v-plus",
            display_name="万相2.1 专业版",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[5],
            resolutions=["720P", "1080P"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.25,
            description="万相2.1专业版"
        ),
        "wan2.6-i2v": ModelCapability(
            provider="tongyi",
            model_id="wan2.6-i2v",
            display_name="万相2.6 图生视频",
            generation_types=[GenerationType.IMAGE_TO_VIDEO],
            durations=[5],
            resolutions=["720P", "1080P"],
            aspect_ratios=["16:9", "9:16", "1:1"],
            modes=[],
            supports_audio=True,
            supports_camera_control=False,
            cost_per_second=0.45,
            description="万相2.6图生视频，支持有声"
        ),
    },
    "jimeng": {
        "jimeng_t2v_v30": ModelCapability(
            provider="jimeng",
            model_id="jimeng_t2v_v30",
            display_name="即梦3.0 720P",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[5, 10],
            resolutions=["720P"],
            aspect_ratios=["16:9", "9:16", "4:3", "3:4", "1:1"],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.6,
            description="视频生成3.0标准版"
        ),
        "jimeng_t2v_v30_1080p": ModelCapability(
            provider="jimeng",
            model_id="jimeng_t2v_v30_1080p",
            display_name="即梦3.0 1080P",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[5, 10],
            resolutions=["1080P"],
            aspect_ratios=["16:9", "9:16", "4:3", "3:4", "1:1"],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.8,
            description="视频生成3.0高清版"
        ),
        "jimeng_t2v_v30_pro": ModelCapability(
            provider="jimeng",
            model_id="jimeng_t2v_v30_pro",
            display_name="即梦3.0 Pro",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[5, 10],
            resolutions=["720P", "1080P"],
            aspect_ratios=["16:9", "9:16", "4:3", "3:4", "1:1"],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=1.0,
            description="视频生成3.0 Pro，支持多镜头叙事"
        ),
        "jimeng_ti2v_v30_pro": ModelCapability(
            provider="jimeng",
            model_id="jimeng_ti2v_v30_pro",
            display_name="即梦3.0 Pro 图生视频",
            generation_types=[GenerationType.IMAGE_TO_VIDEO],
            durations=[5, 10],
            resolutions=["720P", "1080P"],
            aspect_ratios=["16:9", "9:16", "4:3", "3:4", "1:1"],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=1.0,
            description="视频生成3.0 Pro图生视频"
        ),
    },
    "hailuo": {
        "MiniMax-Hailuo-2.3": ModelCapability(
            provider="hailuo",
            model_id="MiniMax-Hailuo-2.3",
            display_name="海螺2.3",
            generation_types=[GenerationType.TEXT_TO_VIDEO, GenerationType.IMAGE_TO_VIDEO],
            durations=[6, 10],
            resolutions=["768P", "1080P"],
            aspect_ratios=[],  # Determined by input image for I2V
            modes=[],
            supports_audio=False,
            supports_camera_control=True,
            cost_per_second=0.5,
            description="最新模型，支持运镜控制"
        ),
        "MiniMax-Hailuo-02": ModelCapability(
            provider="hailuo",
            model_id="MiniMax-Hailuo-02",
            display_name="海螺02",
            generation_types=[
                GenerationType.TEXT_TO_VIDEO,
                GenerationType.IMAGE_TO_VIDEO,
                GenerationType.FIRST_LAST_FRAME,
            ],
            durations=[6, 10],
            resolutions=["768P", "1080P"],
            aspect_ratios=[],
            modes=[],
            supports_audio=False,
            supports_camera_control=True,
            cost_per_second=0.45,
            description="支持首尾帧生成和运镜控制"
        ),
        "MiniMax-Hailuo-2.3-Fast": ModelCapability(
            provider="hailuo",
            model_id="MiniMax-Hailuo-2.3-Fast",
            display_name="海螺2.3 Fast",
            generation_types=[GenerationType.IMAGE_TO_VIDEO],
            durations=[6, 10],
            resolutions=["768P", "1080P"],
            aspect_ratios=[],
            modes=[],
            supports_audio=False,
            supports_camera_control=True,
            cost_per_second=0.4,
            description="快速图生视频"
        ),
        "T2V-01-Director": ModelCapability(
            provider="hailuo",
            model_id="T2V-01-Director",
            display_name="T2V Director",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[6],
            resolutions=["720P"],
            aspect_ratios=[],
            modes=[],
            supports_audio=False,
            supports_camera_control=True,
            cost_per_second=0.35,
            description="导演模式文生视频"
        ),
        "T2V-01": ModelCapability(
            provider="hailuo",
            model_id="T2V-01",
            display_name="T2V Basic",
            generation_types=[GenerationType.TEXT_TO_VIDEO],
            durations=[6],
            resolutions=["720P"],
            aspect_ratios=[],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.3,
            description="基础文生视频模型"
        ),
        "I2V-01-Director": ModelCapability(
            provider="hailuo",
            model_id="I2V-01-Director",
            display_name="I2V Director",
            generation_types=[GenerationType.IMAGE_TO_VIDEO],
            durations=[6],
            resolutions=["720P"],
            aspect_ratios=[],
            modes=[],
            supports_audio=False,
            supports_camera_control=True,
            cost_per_second=0.35,
            description="导演模式图生视频"
        ),
        "I2V-01-live": ModelCapability(
            provider="hailuo",
            model_id="I2V-01-live",
            display_name="I2V Live",
            generation_types=[GenerationType.IMAGE_TO_VIDEO],
            durations=[6],
            resolutions=["720P"],
            aspect_ratios=[],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.3,
            description="实时图生视频"
        ),
        "I2V-01": ModelCapability(
            provider="hailuo",
            model_id="I2V-01",
            display_name="I2V Basic",
            generation_types=[GenerationType.IMAGE_TO_VIDEO],
            durations=[6],
            resolutions=["720P"],
            aspect_ratios=[],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.25,
            description="基础图生视频"
        ),
        "S2V-01": ModelCapability(
            provider="hailuo",
            model_id="S2V-01",
            display_name="S2V Subject Reference",
            generation_types=[GenerationType.SUBJECT_REFERENCE],
            durations=[6],
            resolutions=["720P"],
            aspect_ratios=[],
            modes=[],
            supports_audio=False,
            supports_camera_control=False,
            cost_per_second=0.4,
            description="主体参考视频生成"
        ),
    },
}


# Provider display names
PROVIDER_NAMES = {
    "kling": "可灵 (Kling)",
    "tongyi": "通义万相 (Tongyi)",
    "jimeng": "即梦 (Jimeng)",
    "hailuo": "海螺 (Hailuo)",
}


def get_all_models() -> List[ModelCapability]:
    """Get all models across all providers."""
    models = []
    for provider_models in MODEL_CAPABILITIES.values():
        models.extend(provider_models.values())
    return models


def get_models_by_provider(provider: str) -> List[ModelCapability]:
    """Get all models for a specific provider."""
    return list(MODEL_CAPABILITIES.get(provider, {}).values())


def get_model(provider: str, model_id: str) -> Optional[ModelCapability]:
    """Get a specific model by provider and model ID."""
    return MODEL_CAPABILITIES.get(provider, {}).get(model_id)


def filter_models(
    generation_type: Optional[GenerationType] = None,
    duration: Optional[int] = None,
    duration_range: Optional[Tuple[int, int]] = None,
    resolution: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
) -> List[ModelCapability]:
    """
    Filter models based on required capabilities.

    Returns models that support ALL specified parameters.

    Args:
        generation_type: Filter by generation type
        duration: Filter by exact duration (legacy)
        duration_range: Filter by duration range (min, max) - model must support at least one duration in range
        resolution: Filter by resolution
        aspect_ratio: Filter by aspect ratio
    """
    models = get_all_models()
    filtered = []

    for model in models:
        # Check generation type
        if generation_type and generation_type not in model.generation_types:
            continue

        # Check duration range (model must support at least one duration in the range)
        if duration_range:
            min_dur, max_dur = duration_range
            has_duration_in_range = any(min_dur <= d <= max_dur for d in model.durations)
            if not has_duration_in_range:
                continue
        elif duration and duration not in model.durations:
            continue

        # Check resolution
        if resolution and model.resolutions and resolution not in model.resolutions:
            continue

        # Check aspect ratio (empty means any aspect ratio is supported)
        if aspect_ratio and model.aspect_ratios and aspect_ratio not in model.aspect_ratios:
            continue

        filtered.append(model)

    return filtered


def get_available_durations(generation_type: Optional[GenerationType] = None) -> List[int]:
    """Get all available durations across models."""
    models = filter_models(generation_type=generation_type) if generation_type else get_all_models()
    durations = set()
    for model in models:
        durations.update(model.durations)
    return sorted(durations)


def get_available_resolutions(generation_type: Optional[GenerationType] = None) -> List[str]:
    """Get all available resolutions across models."""
    models = filter_models(generation_type=generation_type) if generation_type else get_all_models()
    resolutions = set()
    for model in models:
        resolutions.update(model.resolutions)
    # Sort by resolution value
    resolution_order = ["720P", "768P", "1080P"]
    return [r for r in resolution_order if r in resolutions]


def get_available_aspect_ratios(generation_type: Optional[GenerationType] = None) -> List[str]:
    """Get all available aspect ratios across models."""
    models = filter_models(generation_type=generation_type) if generation_type else get_all_models()
    ratios = set()
    for model in models:
        if model.aspect_ratios:
            ratios.update(model.aspect_ratios)
    # Common order
    ratio_order = ["16:9", "9:16", "4:3", "3:4", "1:1"]
    return [r for r in ratio_order if r in ratios]


def check_model_compatibility(
    model: ModelCapability,
    generation_type: Optional[GenerationType] = None,
    duration: Optional[int] = None,
    duration_range: Optional[Tuple[int, int]] = None,
    resolution: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Check if a model is compatible with the given parameters.

    Returns:
        (is_compatible, reason_if_not)
    """
    if generation_type and generation_type not in model.generation_types:
        return False, f"不支持 {generation_type.value}"

    if duration_range:
        min_dur, max_dur = duration_range
        has_duration_in_range = any(min_dur <= d <= max_dur for d in model.durations)
        if not has_duration_in_range:
            supported = ", ".join(f"{d}s" for d in model.durations)
            return False, f"时长范围不匹配 (支持: {supported})"
    elif duration and duration not in model.durations:
        return False, f"不支持 {duration}秒 时长"

    if resolution and model.resolutions and resolution not in model.resolutions:
        return False, f"不支持 {resolution} 分辨率"

    if aspect_ratio and model.aspect_ratios and aspect_ratio not in model.aspect_ratios:
        return False, f"不支持 {aspect_ratio} 画面比例"

    return True, ""


def get_model_duration_in_range(model: ModelCapability, duration_range: Tuple[int, int]) -> Optional[int]:
    """
    Get the best duration for a model within the given range.

    Prefers the maximum duration in range for better comparison.
    """
    min_dur, max_dur = duration_range
    valid_durations = [d for d in model.durations if min_dur <= d <= max_dur]
    if valid_durations:
        return max(valid_durations)  # Prefer longer duration
    return None
