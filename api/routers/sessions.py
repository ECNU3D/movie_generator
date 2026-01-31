"""
Sessions Router

API endpoints for workflow session management.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from ..schemas import (
    CreateSessionRequest,
    SessionResponse,
    SessionDetailResponse,
    ApproveRequest,
    SessionListResponse,
)
from ..services import get_workflow_service

router = APIRouter()


@router.post("", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new workflow session.

    Starts the multi-agent workflow with the provided story idea.
    """
    service = get_workflow_service()

    try:
        result = await service.create_session(
            idea=request.idea,
            genre=request.genre,
            style=request.style,
            num_episodes=request.num_episodes,
            episode_duration=request.episode_duration,
            num_characters=request.num_characters,
            target_platform=request.target_platform,
            mode=request.mode,
        )

        summary = result.get("summary", {})
        session = service.get_session(result["session_id"])

        return SessionResponse(
            session_id=result["session_id"],
            status=session.get("status", "running"),
            phase=summary.get("phase", "init"),
            project_name=summary.get("project_name", ""),
            created_at=session.get("created_at", ""),
            updated_at=session.get("updated_at", ""),
            error=summary.get("error"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of sessions"),
):
    """List all workflow sessions."""
    service = get_workflow_service()

    sessions = service.list_sessions(status=status, limit=limit)

    return SessionListResponse(
        sessions=[
            SessionResponse(
                session_id=s["session_id"],
                status=s["status"],
                phase=s["current_phase"],
                project_name="",  # Will be loaded from state if needed
                created_at=s["created_at"],
                updated_at=s["updated_at"],
                error=s.get("error_message"),
            )
            for s in sessions
        ],
        total=len(sessions),
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str):
    """Get detailed session information."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    state = service.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session state not found")

    return SessionDetailResponse(
        session_id=session_id,
        status=session["status"],
        phase=state["phase"],
        project_name=state.get("project_name", ""),
        created_at=session["created_at"],
        updated_at=session["updated_at"],
        error=state.get("error"),
        story_outline=state.get("story_outline"),
        characters=state.get("characters", []),
        episodes=state.get("episodes", []),
        storyboard=state.get("storyboard", []),
        video_prompts=state.get("video_prompts", {}),
        video_tasks=state.get("video_tasks", {}),
        pending_approval=state.get("pending_approval", False),
        approval_type=state.get("approval_type", ""),
        retry_count=state.get("retry_count", 0),
    )


@router.post("/{session_id}/resume", response_model=SessionDetailResponse)
async def resume_session(session_id: str):
    """Resume a paused or failed session."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        result = await service.resume_session(session_id)
        state = result.get("state", {})
        summary = result.get("summary", {})

        return SessionDetailResponse(
            session_id=session_id,
            status="running",
            phase=summary.get("phase", ""),
            project_name=summary.get("project_name", ""),
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            error=summary.get("error"),
            story_outline=state.get("story_outline"),
            characters=state.get("characters", []),
            episodes=state.get("episodes", []),
            storyboard=state.get("storyboard", []),
            video_prompts=state.get("video_prompts", {}),
            video_tasks=state.get("video_tasks", {}),
            pending_approval=state.get("pending_approval", False),
            approval_type=state.get("approval_type", ""),
            retry_count=state.get("retry_count", 0),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/approve", response_model=SessionDetailResponse)
async def approve_session(session_id: str, request: ApproveRequest):
    """Approve or reject a workflow checkpoint."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        result = await service.approve_and_continue(
            session_id=session_id,
            approved=request.approved,
            feedback=request.feedback,
        )

        state = result.get("state", {})
        summary = result.get("summary", {})

        # Reload session for updated timestamps
        session = service.get_session(session_id)

        return SessionDetailResponse(
            session_id=session_id,
            status=session.get("status", "running"),
            phase=summary.get("phase", ""),
            project_name=summary.get("project_name", ""),
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            error=summary.get("error"),
            story_outline=state.get("story_outline"),
            characters=state.get("characters", []),
            episodes=state.get("episodes", []),
            storyboard=state.get("storyboard", []),
            video_prompts=state.get("video_prompts", {}),
            video_tasks=state.get("video_tasks", {}),
            pending_approval=state.get("pending_approval", False),
            approval_type=state.get("approval_type", ""),
            retry_count=state.get("retry_count", 0),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    service.delete_session(session_id)
    return {"status": "deleted", "session_id": session_id}
