"""
Content Router

API endpoints for editing session content (outline, characters, storyboard, prompts).
"""

from typing import Optional
from fastapi import APIRouter, HTTPException

from ..schemas import (
    StoryOutlineRequest,
    StoryOutlineResponse,
    CharacterRequest,
    CharacterResponse,
    CharacterListResponse,
    ShotRequest,
    ShotResponse,
    StoryboardResponse,
    VideoPromptRequest,
    VideoPromptsResponse,
)
from ..services import get_workflow_service

router = APIRouter()


# Story Outline endpoints

@router.get("/{session_id}/outline", response_model=StoryOutlineResponse)
async def get_outline(session_id: str):
    """Get the story outline for a session."""
    service = get_workflow_service()

    state = service.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    outline = state.get("story_outline")
    if not outline:
        raise HTTPException(status_code=404, detail="Story outline not found")

    return StoryOutlineResponse(
        title=outline.get("title", ""),
        genre=outline.get("genre", ""),
        theme=outline.get("theme", ""),
        synopsis=outline.get("synopsis", ""),
        setting=outline.get("setting", ""),
    )


@router.put("/{session_id}/outline", response_model=StoryOutlineResponse)
async def update_outline(session_id: str, request: StoryOutlineRequest):
    """Update the story outline for a session."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    outline_dict = {
        "title": request.title,
        "genre": request.genre,
        "theme": request.theme,
        "synopsis": request.synopsis,
        "setting": request.setting,
    }

    result = service.update_story_outline(session_id, outline_dict)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to update outline")

    return StoryOutlineResponse(**outline_dict)


# Character endpoints

@router.get("/{session_id}/characters", response_model=CharacterListResponse)
async def get_characters(session_id: str):
    """Get all characters for a session."""
    service = get_workflow_service()

    characters = service.get_characters(session_id)
    if characters is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return CharacterListResponse(
        characters=[
            CharacterResponse(
                name=c.get("name", ""),
                age=c.get("age"),
                personality=c.get("personality", ""),
                appearance=c.get("appearance", ""),
                visual_description=c.get("visual_description", ""),
                major_events=c.get("major_events"),
            )
            for c in characters
        ],
        total=len(characters),
    )


@router.put("/{session_id}/characters/{index}", response_model=CharacterResponse)
async def update_character(session_id: str, index: int, request: CharacterRequest):
    """Update a character by index."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    character_dict = {
        "name": request.name,
        "age": request.age,
        "personality": request.personality,
        "appearance": request.appearance,
        "visual_description": request.visual_description,
        "major_events": request.major_events,
    }

    result = service.update_character(session_id, index, character_dict)
    if not result:
        raise HTTPException(status_code=404, detail="Character not found")

    return CharacterResponse(**character_dict)


@router.post("/{session_id}/characters", response_model=CharacterResponse)
async def add_character(session_id: str, request: CharacterRequest):
    """Add a new character."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    character_dict = {
        "name": request.name,
        "age": request.age,
        "personality": request.personality,
        "appearance": request.appearance,
        "visual_description": request.visual_description,
        "major_events": request.major_events,
    }

    result = service.add_character(session_id, character_dict)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to add character")

    return CharacterResponse(**character_dict)


@router.delete("/{session_id}/characters/{index}")
async def delete_character(session_id: str, index: int):
    """Delete a character by index."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    success = service.delete_character(session_id, index)
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")

    return {"status": "deleted", "index": index}


# Storyboard endpoints

@router.get("/{session_id}/storyboard", response_model=StoryboardResponse)
async def get_storyboard(session_id: str):
    """Get the storyboard for a session."""
    service = get_workflow_service()

    shots = service.get_storyboard(session_id)
    if shots is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return StoryboardResponse(
        shots=[
            ShotResponse(
                shot_id=s.get("shot_id", f"shot_{i}"),
                visual_description=s.get("visual_description", ""),
                dialogue=s.get("dialogue"),
                camera_movement=s.get("camera_movement"),
                duration=s.get("duration", 5.0),
                shot_type=s.get("shot_type"),
            )
            for i, s in enumerate(shots)
        ],
        total=len(shots),
    )


@router.put("/{session_id}/storyboard/{index}", response_model=ShotResponse)
async def update_shot(session_id: str, index: int, request: ShotRequest):
    """Update a shot by index."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    shot_dict = {
        "shot_id": request.shot_id,
        "visual_description": request.visual_description,
        "dialogue": request.dialogue,
        "camera_movement": request.camera_movement,
        "duration": request.duration,
        "shot_type": request.shot_type,
    }

    result = service.update_shot(session_id, index, shot_dict)
    if not result:
        raise HTTPException(status_code=404, detail="Shot not found")

    return ShotResponse(**shot_dict)


# Video prompt endpoints

@router.get("/{session_id}/prompts", response_model=VideoPromptsResponse)
async def get_video_prompts(session_id: str):
    """Get all video prompts for a session."""
    service = get_workflow_service()

    prompts = service.get_video_prompts(session_id)
    if prompts is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return VideoPromptsResponse(prompts=prompts)


@router.put("/{session_id}/prompts/{shot_id}")
async def update_video_prompt(session_id: str, shot_id: str, request: VideoPromptRequest):
    """Update a video prompt for a shot."""
    service = get_workflow_service()

    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = service.update_video_prompt(session_id, shot_id, request.prompt)
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to update prompt")

    return {"shot_id": shot_id, "prompt": result}


# Videos endpoints (proxied from video service)

@router.get("/{session_id}/videos")
async def get_videos(session_id: str):
    """Get video tasks for a session."""
    service = get_workflow_service()

    tasks = service.get_video_tasks(session_id)
    if tasks is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return tasks


@router.post("/{session_id}/videos/refresh")
async def refresh_videos(session_id: str):
    """Refresh video task status."""
    from ..services import get_video_service

    video_service = get_video_service()
    result = await video_service.get_video_status(session_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # Convert to dict format
    tasks = {}
    for task in result.get("tasks", []):
        shot_id = task.get("shot_id")
        if shot_id:
            tasks[shot_id] = task

    return tasks


@router.get("/{session_id}/videos/download")
async def download_videos(session_id: str):
    """Download all completed videos."""
    # For now, return a placeholder response
    # In production, this would trigger a download or return a zip file
    return {"status": "not_implemented", "message": "Download endpoint coming soon"}


@router.post("/{session_id}/videos/{shot_id}/retry")
async def retry_video(session_id: str, shot_id: str, platform: Optional[str] = None):
    """Retry video generation for a specific shot."""
    from ..services import get_video_service

    video_service = get_video_service()
    result = await video_service.retry_video(
        session_id=session_id,
        shot_id=shot_id,
        platform=platform,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
