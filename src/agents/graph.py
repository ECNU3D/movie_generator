"""
LangGraph Workflow

Defines the multi-agent workflow using LangGraph.
"""

from typing import Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, END

from .state import (
    AgentState,
    WorkflowPhase,
    InteractionMode,
    UserRequest,
    state_to_dict,
    dict_to_state,
    StateDict,
)
from .story_writer import StoryWriterAgent
from .director import DirectorAgent
from .video_producer import VideoProducerAgent


def create_workflow(api_key: Optional[str] = None) -> StateGraph:
    """
    Create the multi-agent workflow graph.

    The workflow follows this sequence:
    1. story_writer: Generate story outline, characters, episodes
    2. director: Create storyboard
    3. video_producer: Generate video prompts and videos
    4. review: Final review and completion

    Human-in-the-loop checkpoints are inserted at phase transitions.
    """
    # Initialize agents
    story_writer = StoryWriterAgent(api_key=api_key)
    director = DirectorAgent(api_key=api_key)
    video_producer = VideoProducerAgent(api_key=api_key)

    # Create the graph
    workflow = StateGraph(StateDict)

    # Define node functions
    def story_writer_node(state: StateDict) -> StateDict:
        agent_state = dict_to_state(state)
        result = story_writer.run(agent_state)
        return state_to_dict(result)

    def director_node(state: StateDict) -> StateDict:
        agent_state = dict_to_state(state)
        result = director.run(agent_state)
        return state_to_dict(result)

    def video_producer_node(state: StateDict) -> StateDict:
        agent_state = dict_to_state(state)
        result = video_producer.run(agent_state)
        return state_to_dict(result)

    def approval_node(state: StateDict) -> StateDict:
        """
        Human-in-the-loop approval checkpoint.

        In interactive mode, this node pauses execution.
        The workflow can be resumed by calling continue_workflow.
        """
        # Just pass through - actual approval is handled externally
        return state

    def review_node(state: StateDict) -> StateDict:
        """Final review node."""
        agent_state = dict_to_state(state)

        # Check video status
        if agent_state.video_tasks:
            status = video_producer.check_video_status(agent_state)
            all_complete = all(
                s.get('status') in ['completed', 'success']
                for s in status.values()
            )
            if all_complete:
                agent_state.phase = WorkflowPhase.COMPLETED

        return state_to_dict(agent_state)

    # Add nodes
    workflow.add_node("story_writer", story_writer_node)
    workflow.add_node("director", director_node)
    workflow.add_node("video_producer", video_producer_node)
    workflow.add_node("approval", approval_node)
    workflow.add_node("review", review_node)

    # Define routing logic
    def route_from_story_writer(state: StateDict) -> Literal["approval", "director", END]:
        phase = state.get("phase")
        pending = state.get("pending_approval", False)
        error = state.get("error")

        if error:
            return END
        if pending:
            return "approval"
        if phase == WorkflowPhase.STORYBOARD:
            return "director"
        # Still in story writing phases
        return "approval"

    def route_from_director(state: StateDict) -> Literal["approval", "video_producer", END]:
        pending = state.get("pending_approval", False)
        error = state.get("error")

        if error:
            return END
        if pending:
            return "approval"
        return "video_producer"

    def route_from_video_producer(state: StateDict) -> Literal["approval", "review", END]:
        phase = state.get("phase")
        pending = state.get("pending_approval", False)
        error = state.get("error")

        if error:
            return END
        if pending:
            return "approval"
        if phase == WorkflowPhase.REVIEW:
            return "review"
        return "approval"

    def route_from_approval(state: StateDict) -> Literal["story_writer", "director", "video_producer", "review", END]:
        """Route after approval based on current phase."""
        phase = state.get("phase")
        error = state.get("error")

        if error:
            return END

        # Route based on phase
        if phase in [WorkflowPhase.INIT, WorkflowPhase.STORY_OUTLINE,
                     WorkflowPhase.CHARACTER_DESIGN, WorkflowPhase.EPISODE_WRITING]:
            return "story_writer"
        elif phase == WorkflowPhase.STORYBOARD:
            return "director"
        elif phase in [WorkflowPhase.VIDEO_PROMPTS, WorkflowPhase.VIDEO_GENERATION]:
            return "video_producer"
        elif phase == WorkflowPhase.REVIEW:
            return "review"
        elif phase == WorkflowPhase.COMPLETED:
            return END
        else:
            return END

    def route_from_review(state: StateDict) -> Literal["approval", END]:
        phase = state.get("phase")
        if phase == WorkflowPhase.COMPLETED:
            return END
        return "approval"

    # Add edges
    workflow.set_entry_point("story_writer")

    workflow.add_conditional_edges("story_writer", route_from_story_writer)
    workflow.add_conditional_edges("director", route_from_director)
    workflow.add_conditional_edges("video_producer", route_from_video_producer)
    workflow.add_conditional_edges("approval", route_from_approval)
    workflow.add_conditional_edges("review", route_from_review)

    return workflow


def compile_workflow(api_key: Optional[str] = None):
    """Compile the workflow for execution."""
    workflow = create_workflow(api_key)
    return workflow.compile()


class WorkflowRunner:
    """
    High-level runner for the multi-agent workflow.

    Provides a simple interface for starting and managing workflows.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.workflow = compile_workflow(api_key)
        self._current_state: Optional[StateDict] = None

    def start(
        self,
        idea: str,
        genre: str = "drama",
        style: str = "",
        num_episodes: int = 1,
        episode_duration: int = 60,
        num_characters: int = 3,
        target_audience: str = "",
        target_platform: str = "kling",
        mode: InteractionMode = InteractionMode.INTERACTIVE,
    ) -> StateDict:
        """
        Start a new workflow.

        Args:
            idea: Story idea
            genre: Story genre
            style: Visual style
            num_episodes: Number of episodes
            episode_duration: Duration per episode (seconds)
            num_characters: Number of main characters
            target_audience: Target audience
            target_platform: Video generation platform
            mode: Interactive or autonomous mode

        Returns:
            Initial state after first step
        """
        request = UserRequest(
            idea=idea,
            genre=genre,
            style=style,
            num_episodes=num_episodes,
            episode_duration=episode_duration,
            num_characters=num_characters,
            target_audience=target_audience,
            target_platform=target_platform,
        )

        initial_state: StateDict = {
            "request": request,
            "phase": WorkflowPhase.INIT,
            "mode": mode,
            "current_agent": "",
            "next_agent": "",
            "project_id": None,
            "project_name": "",
            "story_outline": None,
            "characters": [],
            "episodes": [],
            "current_episode_index": 0,
            "storyboard": [],
            "current_shot_index": 0,
            "video_prompts": {},
            "video_tasks": {},
            "messages": [],
            "error": None,
            "retry_count": 0,
            "pending_approval": False,
            "approval_type": "",
            "approval_data": None,
        }

        # Run until first approval checkpoint
        result = self._run_until_checkpoint(initial_state)
        self._current_state = result
        return result

    def approve_and_continue(self, approved: bool = True) -> StateDict:
        """
        Approve current checkpoint and continue.

        Args:
            approved: Whether to approve (True) or reject (False)

        Returns:
            State after continuing
        """
        if not self._current_state:
            raise ValueError("No active workflow")

        if not self._current_state.get("pending_approval"):
            raise ValueError("No pending approval")

        if approved:
            self._current_state["pending_approval"] = False
            self._current_state["approval_data"] = None
            result = self._run_until_checkpoint(self._current_state)
            self._current_state = result
            return result
        else:
            self._current_state["error"] = f"User rejected {self._current_state.get('approval_type')}"
            self._current_state["phase"] = WorkflowPhase.ERROR
            return self._current_state

    def _run_until_checkpoint(self, state: StateDict) -> StateDict:
        """Run workflow until next approval checkpoint or completion."""
        result = state

        for step in self.workflow.stream(state):
            # Get the latest state from the step
            for node_name, node_result in step.items():
                if node_result:
                    result = node_result

            # Check for approval checkpoint or completion
            if result.get("pending_approval") or result.get("phase") == WorkflowPhase.COMPLETED:
                break

            if result.get("error"):
                break

        return result

    def get_state(self) -> Optional[StateDict]:
        """Get current workflow state."""
        return self._current_state

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current workflow state."""
        if not self._current_state:
            return {"status": "no_active_workflow"}

        state = self._current_state
        return {
            "phase": state.get("phase", WorkflowPhase.INIT).value if isinstance(state.get("phase"), WorkflowPhase) else state.get("phase"),
            "project_name": state.get("project_name", ""),
            "pending_approval": state.get("pending_approval", False),
            "approval_type": state.get("approval_type", ""),
            "error": state.get("error"),
            "num_characters": len(state.get("characters", [])),
            "num_episodes": len(state.get("episodes", [])),
            "num_shots": len(state.get("storyboard", [])),
            "num_prompts": len(state.get("video_prompts", {})),
        }


class PersistentWorkflowRunner:
    """
    Workflow runner with session persistence and recovery.

    Provides:
    - Session management with database persistence
    - Checkpoint creation at each approval point
    - Session recovery from last checkpoint
    - Session listing and management
    """

    def __init__(self, api_key: Optional[str] = None, db_path: str = "data/workflow_sessions.db"):
        from .session import SessionManager, SessionStatus

        self.api_key = api_key
        self.workflow = compile_workflow(api_key)
        self.session_manager = SessionManager(db_path)
        self._current_session_id: Optional[str] = None
        self._current_state: Optional[StateDict] = None

    def start(
        self,
        idea: str,
        genre: str = "drama",
        style: str = "",
        num_episodes: int = 1,
        episode_duration: int = 60,
        num_characters: int = 3,
        target_audience: str = "",
        target_platform: str = "kling",
        mode: InteractionMode = InteractionMode.INTERACTIVE,
    ) -> Dict[str, Any]:
        """
        Start a new workflow with session persistence.

        Returns:
            Dict with session_id and initial state
        """
        from .session import SessionStatus

        # Create session
        session = self.session_manager.create_session(
            user_request=idea,
            mode=mode,
        )
        self._current_session_id = session.session_id

        # Create initial state
        request = UserRequest(
            idea=idea,
            genre=genre,
            style=style,
            num_episodes=num_episodes,
            episode_duration=episode_duration,
            num_characters=num_characters,
            target_audience=target_audience,
            target_platform=target_platform,
        )

        initial_state: StateDict = {
            "request": request,
            "phase": WorkflowPhase.INIT,
            "mode": mode,
            "current_agent": "",
            "next_agent": "",
            "project_id": None,
            "project_name": "",
            "story_outline": None,
            "characters": [],
            "episodes": [],
            "current_episode_index": 0,
            "storyboard": [],
            "current_shot_index": 0,
            "video_prompts": {},
            "video_tasks": {},
            "messages": [],
            "error": None,
            "retry_count": 0,
            "pending_approval": False,
            "approval_type": "",
            "approval_data": None,
        }

        # Run until first checkpoint
        result = self._run_until_checkpoint(initial_state)
        self._current_state = result

        # Save state and create checkpoint
        self._save_checkpoint("start", result)

        return {
            "session_id": session.session_id,
            "state": result,
            "summary": self.get_summary(),
        }

    def resume(self, session_id: str, retry_on_error: bool = True) -> Dict[str, Any]:
        """
        Resume a paused or failed session.

        Args:
            session_id: The session ID to resume
            retry_on_error: If True, allow resuming failed sessions by clearing error

        Returns:
            Dict with session info and current state
        """
        from .session import SessionStatus

        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.status == SessionStatus.COMPLETED:
            raise ValueError("Session already completed")

        # Load state
        state = self.session_manager.load_state(session_id)
        if not state:
            raise ValueError("No state found for session")

        self._current_session_id = session_id
        self._current_state = state_to_dict(state)

        # Handle failed sessions - allow retry
        resumed_from_error = False
        if session.status == SessionStatus.FAILED or self._current_state.get("error"):
            if not retry_on_error:
                raise ValueError(f"Session failed: {session.error_message}")

            resumed_from_error = True

            # Clear the error to allow retry
            self._current_state["error"] = None

            # Determine the correct phase to resume from based on workflow state
            # If we have video_prompts but failed during generation, resume at VIDEO_GENERATION
            if self._current_state.get("video_prompts"):
                self._current_state["phase"] = WorkflowPhase.VIDEO_GENERATION
                self._current_state["pending_approval"] = False  # Will continue automatically
            elif self._current_state.get("storyboard"):
                self._current_state["phase"] = WorkflowPhase.VIDEO_PROMPTS
                self._current_state["pending_approval"] = False
            elif self._current_state.get("episodes"):
                self._current_state["phase"] = WorkflowPhase.STORYBOARD
                self._current_state["pending_approval"] = False
            elif self._current_state.get("characters"):
                self._current_state["phase"] = WorkflowPhase.CHARACTER_DESIGN
                self._current_state["pending_approval"] = False
            elif self._current_state.get("story_outline"):
                self._current_state["phase"] = WorkflowPhase.STORY_OUTLINE
                self._current_state["pending_approval"] = False

            # Update session status back to running
            self.session_manager.update_session_status(
                session_id,
                SessionStatus.RUNNING,
                error_message=None
            )

            # Increment retry count
            self._current_state["retry_count"] = self._current_state.get("retry_count", 0) + 1

            # Run the workflow to continue from the recovered phase
            result = self._run_until_checkpoint(self._current_state)
            self._current_state = result

            # Save checkpoint after resuming
            self._save_checkpoint("resume_from_error", result)

        return {
            "session_id": session_id,
            "state": self._current_state,
            "summary": self.get_summary(),
            "resumed_from_error": resumed_from_error,
        }

    def approve_and_continue(self, approved: bool = True, feedback: str = "") -> Dict[str, Any]:
        """
        Approve current checkpoint and continue.

        Args:
            approved: Whether to approve
            feedback: Optional feedback for modifications

        Returns:
            Dict with updated state
        """
        from .session import SessionStatus

        if not self._current_state:
            raise ValueError("No active workflow")

        if not self._current_state.get("pending_approval"):
            raise ValueError("No pending approval")

        if approved:
            # Clear approval and continue
            self._current_state["pending_approval"] = False
            self._current_state["approval_data"] = None

            result = self._run_until_checkpoint(self._current_state)
            self._current_state = result

            # Save checkpoint
            self._save_checkpoint("continue", result)

            return {
                "session_id": self._current_session_id,
                "state": result,
                "summary": self.get_summary(),
            }
        else:
            # User rejected
            self._current_state["error"] = f"User rejected {self._current_state.get('approval_type')}"
            if feedback:
                self._current_state["error"] += f": {feedback}"
            self._current_state["phase"] = WorkflowPhase.ERROR

            self._save_checkpoint("rejected", self._current_state)

            return {
                "session_id": self._current_session_id,
                "state": self._current_state,
                "summary": self.get_summary(),
            }

    def list_sessions(self, status: Optional[str] = None, limit: int = 20) -> list:
        """List sessions."""
        from .session import SessionStatus

        status_enum = None
        if status:
            try:
                status_enum = SessionStatus(status)
            except ValueError:
                pass

        sessions = self.session_manager.list_sessions(status=status_enum, limit=limit)
        return [s.to_dict() for s in sessions]

    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get detailed session information."""
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        checkpoints = self.session_manager.get_checkpoints(session_id)

        return {
            "session": session.to_dict(),
            "checkpoints": [c.to_dict() for c in checkpoints],
        }

    def delete_session(self, session_id: str):
        """Delete a session."""
        self.session_manager.delete_session(session_id)
        if self._current_session_id == session_id:
            self._current_session_id = None
            self._current_state = None

    def _run_until_checkpoint(self, state: StateDict) -> StateDict:
        """Run workflow until next approval checkpoint or completion."""
        result = state

        for step in self.workflow.stream(state):
            for node_name, node_result in step.items():
                if node_result:
                    result = node_result

            if result.get("pending_approval") or result.get("phase") == WorkflowPhase.COMPLETED:
                break

            if result.get("error"):
                break

        return result

    def _save_checkpoint(self, step_name: str, state: StateDict):
        """Save current state as checkpoint."""
        if not self._current_session_id:
            return

        # Convert state to AgentState for serialization
        agent_state = dict_to_state(state)
        self.session_manager.save_state(self._current_session_id, agent_state)

        # Create checkpoint
        phase = state.get("phase")
        phase_str = phase.value if isinstance(phase, WorkflowPhase) else str(phase)

        self.session_manager.create_checkpoint(
            session_id=self._current_session_id,
            step_name=step_name,
            phase=phase_str,
            input_data={"approval_type": state.get("approval_type", "")},
            output_data={
                "project_id": state.get("project_id"),
                "project_name": state.get("project_name"),
                "pending_approval": state.get("pending_approval"),
            },
        )

    def get_state(self) -> Optional[StateDict]:
        """Get current workflow state."""
        return self._current_state

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current workflow state."""
        if not self._current_state:
            return {"status": "no_active_workflow"}

        state = self._current_state
        phase = state.get("phase", WorkflowPhase.INIT)
        return {
            "session_id": self._current_session_id,
            "phase": phase.value if isinstance(phase, WorkflowPhase) else phase,
            "project_name": state.get("project_name", ""),
            "pending_approval": state.get("pending_approval", False),
            "approval_type": state.get("approval_type", ""),
            "error": state.get("error"),
            "retry_count": state.get("retry_count", 0),
            "num_characters": len(state.get("characters", [])),
            "num_episodes": len(state.get("episodes", [])),
            "num_shots": len(state.get("storyboard", [])),
            "num_prompts": len(state.get("video_prompts", {})),
        }
