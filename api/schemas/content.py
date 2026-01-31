"""
Pydantic Schemas for Content Editing API
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StoryOutlineRequest(BaseModel):
    """Story outline data."""
    title: str = Field(..., min_length=1, description="Story title")
    genre: str = Field(default="drama", description="Story genre")
    theme: str = Field(default="", description="Story theme")
    synopsis: str = Field(default="", description="Story synopsis")
    setting: str = Field(default="", description="Story setting")


class StoryOutlineResponse(BaseModel):
    """Story outline response."""
    title: str
    genre: str
    theme: str
    synopsis: str
    setting: str


class CharacterRequest(BaseModel):
    """Character data."""
    name: str = Field(..., min_length=1, description="Character name")
    age: Optional[str] = Field(default=None, description="Character age")
    personality: str = Field(default="", description="Character personality")
    appearance: str = Field(default="", description="Character appearance")
    visual_description: str = Field(default="", description="Visual description for AI")
    major_events: Optional[List[str]] = Field(default=None, description="Major life events")


class CharacterResponse(BaseModel):
    """Character response."""
    name: str
    age: Optional[str] = None
    personality: str
    appearance: str
    visual_description: str
    major_events: Optional[List[str]] = None


class CharacterListResponse(BaseModel):
    """List of characters."""
    characters: List[CharacterResponse]
    total: int


class ShotRequest(BaseModel):
    """Shot/storyboard data."""
    shot_id: str = Field(..., description="Shot identifier")
    visual_description: str = Field(default="", description="Visual description")
    dialogue: Optional[str] = Field(default=None, description="Dialogue text")
    camera_movement: Optional[str] = Field(default=None, description="Camera movement type")
    duration: float = Field(default=5.0, ge=1, le=60, description="Shot duration in seconds")
    shot_type: Optional[str] = Field(default=None, description="Type of shot")


class ShotResponse(BaseModel):
    """Shot response."""
    shot_id: str
    visual_description: str
    dialogue: Optional[str] = None
    camera_movement: Optional[str] = None
    duration: float
    shot_type: Optional[str] = None


class StoryboardResponse(BaseModel):
    """Storyboard response."""
    shots: List[ShotResponse]
    total: int


class VideoPromptRequest(BaseModel):
    """Video prompt data."""
    shot_id: str = Field(..., description="Shot identifier")
    prompt: str = Field(..., min_length=1, description="Video generation prompt")


class VideoPromptsResponse(BaseModel):
    """Video prompts response."""
    prompts: Dict[str, str]


class ConsistencyCheckRequest(BaseModel):
    """Request for consistency check."""
    auto_fix: bool = Field(default=False, description="Automatically fix issues")


class ConsistencyCheckResponse(BaseModel):
    """Consistency check result."""
    is_consistent: bool
    issues: List[Dict[str, Any]]
    fixes_applied: List[Dict[str, Any]] = []


class EditHistoryEntry(BaseModel):
    """Edit history entry."""
    timestamp: str
    field: str
    old_value: Any
    new_value: Any
    entity_type: str
    entity_id: Optional[str] = None


class EditHistoryResponse(BaseModel):
    """Edit history response."""
    entries: List[EditHistoryEntry]
    can_undo: bool
    can_redo: bool
