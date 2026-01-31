"""
Pydantic Schemas for Session API
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Request to create a new workflow session."""
    idea: str = Field(..., min_length=1, description="Story idea")
    genre: str = Field(default="drama", description="Story genre")
    style: str = Field(default="", description="Visual style description")
    num_episodes: int = Field(default=1, ge=1, le=10, description="Number of episodes")
    episode_duration: int = Field(default=60, ge=10, le=300, description="Episode duration in seconds")
    num_characters: int = Field(default=3, ge=1, le=10, description="Number of characters")
    target_platform: str = Field(default="kling", description="Video generation platform")
    mode: str = Field(default="interactive", description="Workflow mode: interactive or autonomous")


class SessionResponse(BaseModel):
    """Basic session information."""
    session_id: str
    status: str
    phase: str
    project_name: str
    created_at: str
    updated_at: str
    error: Optional[str] = None


class SessionDetailResponse(SessionResponse):
    """Detailed session information including workflow state."""
    story_outline: Optional[Dict[str, Any]] = None
    characters: List[Dict[str, Any]] = []
    episodes: List[Dict[str, Any]] = []
    storyboard: List[Dict[str, Any]] = []
    video_prompts: Dict[str, str] = {}
    video_tasks: Dict[str, Dict[str, Any]] = {}
    pending_approval: bool = False
    approval_type: str = ""
    retry_count: int = 0


class ApproveRequest(BaseModel):
    """Request to approve or reject a workflow checkpoint."""
    approved: bool = True
    feedback: str = ""
    edits: Optional[Dict[str, Any]] = None


class SessionListResponse(BaseModel):
    """List of sessions."""
    sessions: List[SessionResponse]
    total: int
