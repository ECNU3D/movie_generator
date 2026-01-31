"""
Pydantic Schemas for Video API
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class VideoTaskResponse(BaseModel):
    """Video task status."""
    shot_id: str
    task_id: Optional[str] = None
    platform: str
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None
    prompt: Optional[str] = None


class VideoStatusResponse(BaseModel):
    """Video status for a session."""
    session_id: str
    platform: str
    tasks: List[VideoTaskResponse]
    completed: int
    total: int
    all_complete: bool


class RetryVideoRequest(BaseModel):
    """Request to retry video generation."""
    platform: Optional[str] = None  # If provided, switch to this platform
    prompt: Optional[str] = None  # If provided, use this prompt


class CompareVideoRequest(BaseModel):
    """Request to generate videos on multiple platforms for comparison."""
    shot_ids: List[str] = Field(..., min_length=1)
    platforms: List[str] = Field(..., min_length=1)


class CompareVideoResponse(BaseModel):
    """Response for multi-platform comparison."""
    tasks: Dict[str, Dict[str, VideoTaskResponse]]
