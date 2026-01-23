"""
Story Generator - AI驱动的故事剧本生成器

基于Google Gemini的智能故事和分镜脚本生成工具
"""

from .models import (
    Project,
    Character,
    Episode,
    Shot,
    MajorEvent,
    EditHistory,
    ConsistencyIssue,
    Genre,
    ShotType,
    CameraMovement,
    ShotDensity,
    EditType,
    SHOT_TYPE_NAMES,
    CAMERA_MOVEMENT_NAMES,
    GENRE_NAMES,
)

from .database import Database
from .gemini_client import GeminiClient, GeminiConfig

__all__ = [
    # Models
    "Project",
    "Character",
    "Episode",
    "Shot",
    "MajorEvent",
    "EditHistory",
    "ConsistencyIssue",
    "Genre",
    "ShotType",
    "CameraMovement",
    "ShotDensity",
    "EditType",
    "SHOT_TYPE_NAMES",
    "CAMERA_MOVEMENT_NAMES",
    "GENRE_NAMES",
    # Database
    "Database",
    # Gemini
    "GeminiClient",
    "GeminiConfig",
]
