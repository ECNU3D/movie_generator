"""
Workflow Service

Wraps the existing PersistentWorkflowRunner for async API usage.
"""

import asyncio
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor

from agents import PersistentWorkflowRunner, SessionManager, InteractionMode
from agents.state import WorkflowPhase

# Thread pool for running sync workflow operations
_executor = ThreadPoolExecutor(max_workers=4)


class WorkflowService:
    """
    Service for managing workflow sessions.

    Wraps the synchronous PersistentWorkflowRunner for async API usage.
    """

    def __init__(self, db_path: str = "story_generator.db"):
        self.db_path = db_path
        self.session_manager = SessionManager(db_path)
        self._runners: Dict[str, PersistentWorkflowRunner] = {}

    def _get_runner(self, session_id: Optional[str] = None) -> PersistentWorkflowRunner:
        """Get or create a workflow runner."""
        if session_id and session_id in self._runners:
            return self._runners[session_id]

        runner = PersistentWorkflowRunner(db_path=self.db_path)
        if session_id:
            self._runners[session_id] = runner
        return runner

    async def create_session(
        self,
        idea: str,
        genre: str = "drama",
        style: str = "",
        num_episodes: int = 1,
        episode_duration: int = 60,
        num_characters: int = 3,
        target_platform: str = "kling",
        mode: str = "interactive",
    ) -> Dict[str, Any]:
        """Create a new workflow session."""
        runner = self._get_runner()

        interaction_mode = (
            InteractionMode.AUTONOMOUS if mode == "autonomous"
            else InteractionMode.INTERACTIVE
        )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: runner.start(
                idea=idea,
                genre=genre,
                style=style,
                num_episodes=num_episodes,
                episode_duration=episode_duration,
                num_characters=num_characters,
                target_platform=target_platform,
                mode=interaction_mode,
            )
        )

        session_id = result["session_id"]
        self._runners[session_id] = runner
        return result

    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused or failed session."""
        runner = self._get_runner(session_id)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: runner.resume(session_id)
        )

        self._runners[session_id] = runner
        return result

    async def approve_and_continue(
        self,
        session_id: str,
        approved: bool = True,
        feedback: str = "",
    ) -> Dict[str, Any]:
        """Approve or reject a checkpoint and continue."""
        runner = self._runners.get(session_id)

        if not runner:
            # Need to resume first
            await self.resume_session(session_id)
            runner = self._runners[session_id]

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: runner.approve_and_continue(approved, feedback)
        )
        return result

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session info."""
        session = self.session_manager.get_session(session_id)
        if not session:
            return None
        return session.to_dict()

    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get full session state."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None

        return {
            "story_outline": state.story_outline,
            "characters": state.characters,
            "episodes": state.episodes,
            "storyboard": state.storyboard,
            "video_prompts": state.video_prompts,
            "video_tasks": state.video_tasks,
            "phase": state.phase.value if isinstance(state.phase, WorkflowPhase) else state.phase,
            "pending_approval": state.pending_approval,
            "approval_type": state.approval_type,
            "error": state.error,
            "retry_count": state.retry_count,
            "project_name": state.project_name,
            "project_id": state.project_id,
        }

    def list_sessions(
        self,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List sessions."""
        from agents.session import SessionStatus

        status_enum = None
        if status:
            try:
                status_enum = SessionStatus(status)
            except ValueError:
                pass

        sessions = self.session_manager.list_sessions(status=status_enum, limit=limit)
        return [s.to_dict() for s in sessions]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        self.session_manager.delete_session(session_id)
        if session_id in self._runners:
            del self._runners[session_id]
        return True

    def update_story_outline(
        self, session_id: str, outline: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update story outline for a session."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None

        # Update story outline
        state.story_outline = outline
        self.session_manager.save_state(session_id, state)
        return outline

    def get_characters(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get characters for a session."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None
        return state.characters or []

    def update_character(
        self, session_id: str, index: int, character: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a character by index."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None

        if not state.characters or index >= len(state.characters):
            return None

        state.characters[index] = character
        self.session_manager.save_state(session_id, state)
        return character

    def add_character(
        self, session_id: str, character: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Add a new character."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None

        if state.characters is None:
            state.characters = []
        state.characters.append(character)
        self.session_manager.save_state(session_id, state)
        return character

    def delete_character(self, session_id: str, index: int) -> bool:
        """Delete a character by index."""
        state = self.session_manager.load_state(session_id)
        if not state or not state.characters or index >= len(state.characters):
            return False

        del state.characters[index]
        self.session_manager.save_state(session_id, state)
        return True

    def get_storyboard(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get storyboard for a session."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None
        return state.storyboard or []

    def update_shot(
        self, session_id: str, index: int, shot: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a shot by index."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None

        if not state.storyboard or index >= len(state.storyboard):
            return None

        state.storyboard[index] = shot
        self.session_manager.save_state(session_id, state)
        return shot

    def get_video_prompts(self, session_id: str) -> Optional[Dict[str, str]]:
        """Get video prompts for a session."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None
        return state.video_prompts or {}

    def update_video_prompt(
        self, session_id: str, shot_id: str, prompt: str
    ) -> Optional[str]:
        """Update a video prompt for a shot."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None

        if state.video_prompts is None:
            state.video_prompts = {}
        state.video_prompts[shot_id] = prompt
        self.session_manager.save_state(session_id, state)
        return prompt

    def get_video_tasks(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get video tasks for a session."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return None
        return state.video_tasks or {}


# Global service instance
_workflow_service: Optional[WorkflowService] = None


def get_workflow_service() -> WorkflowService:
    """Get the global workflow service instance."""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = WorkflowService()
    return _workflow_service
