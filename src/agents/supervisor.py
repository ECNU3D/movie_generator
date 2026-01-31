"""
Supervisor Agent

Orchestrates the multi-agent workflow and manages state transitions.
"""

from typing import Dict, Any, Optional, Callable
from .base import BaseAgent
from .state import AgentState, WorkflowPhase, InteractionMode, UserRequest
from .story_writer import StoryWriterAgent
from .director import DirectorAgent
from .video_producer import VideoProducerAgent


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Orchestrates the video generation workflow.

    Responsibilities:
    - Route tasks to appropriate worker agents
    - Manage workflow state transitions
    - Handle human-in-the-loop checkpoints
    - Coordinate between agents
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="Supervisor", api_key=api_key)

        # Initialize worker agents
        self.story_writer = StoryWriterAgent(api_key=api_key)
        self.director = DirectorAgent(api_key=api_key)
        self.video_producer = VideoProducerAgent(api_key=api_key)

        # Phase to agent mapping
        self.phase_agents = {
            WorkflowPhase.INIT: self.story_writer,
            WorkflowPhase.STORY_OUTLINE: self.story_writer,
            WorkflowPhase.CHARACTER_DESIGN: self.story_writer,
            WorkflowPhase.EPISODE_WRITING: self.story_writer,
            WorkflowPhase.STORYBOARD: self.director,
            WorkflowPhase.VIDEO_PROMPTS: self.video_producer,
            WorkflowPhase.VIDEO_GENERATION: self.video_producer,
        }

        # Approval callback
        self._approval_callback: Optional[Callable] = None

    def set_approval_callback(self, callback: Callable[[AgentState], bool]):
        """Set callback for human-in-the-loop approval."""
        self._approval_callback = callback

    def run(self, state: AgentState) -> AgentState:
        """
        Execute supervisor logic - route to appropriate agent.
        """
        state.current_agent = self.name

        # Check for completion or error
        if state.phase == WorkflowPhase.COMPLETED:
            self.log("Workflow completed!", state)
            return state

        if state.phase == WorkflowPhase.ERROR:
            self.log(f"Workflow in error state: {state.error}", state)
            return state

        # Handle pending approvals
        if state.pending_approval:
            return self._handle_approval(state)

        # Route to appropriate agent
        return self._route_to_agent(state)

    def start_workflow(
        self,
        idea: str,
        genre: str = "drama",
        style: str = "",
        num_episodes: int = 1,
        episode_duration: int = 60,
        num_characters: int = 3,
        target_audience: str = "",
        target_platform: str = "kling",
        mode: InteractionMode = InteractionMode.INTERACTIVE
    ) -> AgentState:
        """
        Start a new video generation workflow.

        Args:
            idea: The story idea
            genre: Story genre
            style: Visual style
            num_episodes: Number of episodes
            episode_duration: Duration per episode in seconds
            num_characters: Number of main characters
            target_audience: Target audience
            target_platform: Video generation platform
            mode: Interaction mode (interactive or autonomous)

        Returns:
            Initial workflow state
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

        state = AgentState(
            request=request,
            phase=WorkflowPhase.INIT,
            mode=mode,
        )

        self.log(f"Starting workflow for: {idea}", state)
        return self.run(state)

    def continue_workflow(self, state: AgentState) -> AgentState:
        """Continue workflow from current state."""
        return self.run(state)

    def approve_and_continue(self, state: AgentState, approved: bool = True) -> AgentState:
        """
        Handle user approval and continue workflow.

        Args:
            state: Current state with pending approval
            approved: Whether user approved

        Returns:
            Updated state
        """
        if not state.pending_approval:
            self.log("No pending approval", state)
            return state

        if approved:
            state.pending_approval = False
            state.approval_data = None
            self.log(f"Approved: {state.approval_type}", state)
            return self.run(state)
        else:
            # User rejected - could implement revision logic
            self.log(f"Rejected: {state.approval_type}", state)
            state.error = f"User rejected {state.approval_type}"
            state.phase = WorkflowPhase.ERROR
            return state

    def _handle_approval(self, state: AgentState) -> AgentState:
        """Handle pending approval checkpoint."""
        if state.mode == InteractionMode.AUTONOMOUS:
            # Auto-approve in autonomous mode
            state.pending_approval = False
            state.approval_data = None
            return self._route_to_agent(state)

        if self._approval_callback:
            approved = self._approval_callback(state)
            return self.approve_and_continue(state, approved)

        # Return state with pending approval for external handling
        self.log(f"Waiting for approval: {state.approval_type}", state)
        return state

    def _route_to_agent(self, state: AgentState) -> AgentState:
        """Route to appropriate agent based on phase."""
        agent = self.phase_agents.get(state.phase)

        if not agent:
            # Check if we're in review phase
            if state.phase == WorkflowPhase.REVIEW:
                return self._handle_review(state)
            self.log(f"No agent for phase: {state.phase}", state)
            return state

        self.log(f"Routing to {agent.name} for phase {state.phase.value}", state)
        return agent.run(state)

    def _handle_review(self, state: AgentState) -> AgentState:
        """Handle the review phase."""
        self.log("Entering review phase...", state)

        # Check video generation status
        if state.video_tasks:
            status = self.video_producer.check_video_status(state)
            all_complete = all(
                s.get('status') in ['completed', 'success']
                for s in status.values()
            )
            all_failed = all(
                s.get('status') in ['failed', 'error']
                for s in status.values()
            )

            if all_failed:
                return self.set_error("All video generation tasks failed", state)

            if not all_complete:
                # Still waiting for videos
                state.pending_approval = True
                state.approval_type = "video_status"
                state.approval_data = {"status": status}
                return state

        # All done!
        state.phase = WorkflowPhase.COMPLETED
        self.log("Workflow completed successfully!", state)
        return state

    def get_workflow_summary(self, state: AgentState) -> Dict[str, Any]:
        """Get a summary of the workflow state."""
        return {
            "phase": state.phase.value,
            "project_id": state.project_id,
            "project_name": state.project_name,
            "pending_approval": state.pending_approval,
            "approval_type": state.approval_type,
            "error": state.error,
            "story_outline": bool(state.story_outline),
            "num_characters": len(state.characters),
            "num_episodes": len(state.episodes),
            "num_shots": len(state.storyboard),
            "num_prompts": len(state.video_prompts),
            "num_video_tasks": len(state.video_tasks),
            "messages": [
                {"agent": m.agent, "content": m.content[:100]}
                for m in state.messages[-5:]  # Last 5 messages
            ]
        }
