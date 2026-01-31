"""
Agents Package

Multi-agent system for automated AI video generation.

Agents:
- SupervisorAgent: Orchestrates the workflow and delegates tasks
- StoryWriterAgent: Creates story outlines, characters, and episodes
- DirectorAgent: Generates storyboards and shot descriptions
- VideoProducerAgent: Generates video prompts and manages video generation

Architecture:
- Agents use Skills for knowledge/guidance
- Agents call MCP Tools for data operations
- LangGraph orchestrates the workflow
"""

from .state import AgentState, WorkflowPhase, InteractionMode, UserRequest
from .base import BaseAgent
from .story_writer import StoryWriterAgent
from .director import DirectorAgent
from .video_producer import VideoProducerAgent
from .supervisor import SupervisorAgent
from .graph import create_workflow, compile_workflow, WorkflowRunner, PersistentWorkflowRunner
from .session import SessionManager, Session, Checkpoint, SessionStatus

__all__ = [
    # State
    "AgentState",
    "WorkflowPhase",
    "InteractionMode",
    "UserRequest",
    # Agents
    "BaseAgent",
    "StoryWriterAgent",
    "DirectorAgent",
    "VideoProducerAgent",
    "SupervisorAgent",
    # Workflow
    "create_workflow",
    "compile_workflow",
    "WorkflowRunner",
    "PersistentWorkflowRunner",
    # Session Management
    "SessionManager",
    "Session",
    "Checkpoint",
    "SessionStatus",
]
