"""
Agent State Definitions

Defines the shared state used across all agents in the workflow.
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Annotated
from dataclasses import dataclass, field
from datetime import datetime


class WorkflowPhase(Enum):
    """Current phase of the video generation workflow."""
    INIT = "init"
    STORY_OUTLINE = "story_outline"
    CHARACTER_DESIGN = "character_design"
    EPISODE_WRITING = "episode_writing"
    STORYBOARD = "storyboard"
    VIDEO_PROMPTS = "video_prompts"
    VIDEO_GENERATION = "video_generation"
    REVIEW = "review"
    COMPLETED = "completed"
    ERROR = "error"


class InteractionMode(Enum):
    """User interaction mode."""
    INTERACTIVE = "interactive"  # Pause at checkpoints for user approval
    AUTONOMOUS = "autonomous"    # Run fully automated


@dataclass
class UserRequest:
    """Original user request."""
    idea: str
    genre: str = "drama"
    style: str = ""
    num_episodes: int = 1
    episode_duration: int = 60
    num_characters: int = 3
    target_audience: str = ""
    target_platform: str = "kling"  # Default video platform


@dataclass
class AgentMessage:
    """Message from an agent."""
    agent: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


def merge_messages(left: List[AgentMessage], right: List[AgentMessage]) -> List[AgentMessage]:
    """Merge message lists (for LangGraph state updates)."""
    return left + right


@dataclass
class AgentState:
    """
    Shared state for the multi-agent workflow.

    This state is passed between agents and updated as the workflow progresses.
    """
    # User request
    request: Optional[UserRequest] = None

    # Workflow control
    phase: WorkflowPhase = WorkflowPhase.INIT
    mode: InteractionMode = InteractionMode.INTERACTIVE
    current_agent: str = ""
    next_agent: str = ""

    # Project data (IDs reference database)
    project_id: Optional[int] = None
    project_name: str = ""

    # Generated content
    story_outline: Optional[Dict[str, Any]] = None
    characters: List[Dict[str, Any]] = field(default_factory=list)
    episodes: List[Dict[str, Any]] = field(default_factory=list)
    current_episode_index: int = 0

    # Storyboard data
    storyboard: List[Dict[str, Any]] = field(default_factory=list)
    current_shot_index: int = 0

    # Video generation
    video_prompts: Dict[str, str] = field(default_factory=dict)  # shot_id -> prompt
    video_tasks: Dict[str, Dict] = field(default_factory=dict)   # shot_id -> task info

    # Agent communication
    messages: Annotated[List[AgentMessage], merge_messages] = field(default_factory=list)

    # Error handling
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    # Checkpoints for human-in-the-loop
    pending_approval: bool = False
    approval_type: str = ""  # "story_outline", "characters", "storyboard", etc.
    approval_data: Optional[Dict[str, Any]] = None

    def add_message(self, agent: str, content: str, **metadata):
        """Add a message from an agent."""
        self.messages.append(AgentMessage(
            agent=agent,
            content=content,
            metadata=metadata
        ))

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization."""
        return {
            "phase": self.phase.value,
            "mode": self.mode.value,
            "current_agent": self.current_agent,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "current_episode_index": self.current_episode_index,
            "current_shot_index": self.current_shot_index,
            "error": self.error,
            "pending_approval": self.pending_approval,
            "approval_type": self.approval_type,
        }


# Type alias for LangGraph
StateDict = Dict[str, Any]


def state_to_dict(state: AgentState) -> StateDict:
    """Convert AgentState to dict for LangGraph."""
    return {
        "request": state.request,
        "phase": state.phase,
        "mode": state.mode,
        "current_agent": state.current_agent,
        "next_agent": state.next_agent,
        "project_id": state.project_id,
        "project_name": state.project_name,
        "story_outline": state.story_outline,
        "characters": state.characters,
        "episodes": state.episodes,
        "current_episode_index": state.current_episode_index,
        "storyboard": state.storyboard,
        "current_shot_index": state.current_shot_index,
        "video_prompts": state.video_prompts,
        "video_tasks": state.video_tasks,
        "messages": state.messages,
        "error": state.error,
        "retry_count": state.retry_count,
        "pending_approval": state.pending_approval,
        "approval_type": state.approval_type,
        "approval_data": state.approval_data,
    }


def dict_to_state(d: StateDict) -> AgentState:
    """Convert dict back to AgentState."""
    state = AgentState()
    for key, value in d.items():
        if hasattr(state, key):
            setattr(state, key, value)
    return state
