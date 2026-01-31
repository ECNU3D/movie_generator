"""
Videos Router

API endpoints for video generation management.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse

from ..schemas import (
    VideoStatusResponse,
    VideoTaskResponse,
    RetryVideoRequest,
    CompareVideoRequest,
    CompareVideoResponse,
)
from ..services import get_video_service

router = APIRouter()


@router.get("/{session_id}", response_model=VideoStatusResponse)
async def get_video_status(session_id: str):
    """Get video generation status for a session."""
    service = get_video_service()

    result = await service.get_video_status(session_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return VideoStatusResponse(
        session_id=result["session_id"],
        platform=result["platform"],
        tasks=[
            VideoTaskResponse(
                shot_id=t["shot_id"],
                task_id=t.get("task_id"),
                platform=t["platform"],
                status=t["status"],
                video_url=t.get("video_url"),
                error=t.get("error"),
                prompt=t.get("prompt"),
            )
            for t in result["tasks"]
        ],
        completed=result["completed"],
        total=result["total"],
        all_complete=result["all_complete"],
    )


@router.post("/{session_id}/refresh", response_model=VideoStatusResponse)
async def refresh_video_status(session_id: str):
    """Refresh video status by checking with providers."""
    # Same as get_video_status but explicitly refreshes
    return await get_video_status(session_id)


@router.post("/{session_id}/{shot_id}/retry", response_model=VideoTaskResponse)
async def retry_video(
    session_id: str,
    shot_id: str,
    request: Optional[RetryVideoRequest] = None,
):
    """
    Retry video generation for a specific shot.

    Supports:
    - Simple retry (no body)
    - Retry with different platform
    - Retry with modified prompt
    """
    service = get_video_service()

    platform = request.platform if request else None
    prompt = request.prompt if request else None

    result = await service.retry_video(
        session_id=session_id,
        shot_id=shot_id,
        platform=platform,
        prompt=prompt,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return VideoTaskResponse(
        shot_id=result["shot_id"],
        task_id=result.get("task_id"),
        platform=result["platform"],
        status=result["status"],
    )


@router.post("/{session_id}/compare", response_model=CompareVideoResponse)
async def compare_videos(session_id: str, request: CompareVideoRequest):
    """
    Generate videos on multiple platforms for comparison.

    Submits the same prompts to multiple platforms simultaneously.
    """
    service = get_video_service()

    result = await service.compare_videos(
        session_id=session_id,
        shot_ids=request.shot_ids,
        platforms=request.platforms,
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Convert to response format
    tasks = {}
    for shot_id, platforms in result["tasks"].items():
        tasks[shot_id] = {
            platform: VideoTaskResponse(
                shot_id=task["shot_id"],
                task_id=task.get("task_id"),
                platform=task["platform"],
                status=task["status"],
                error=task.get("error"),
            )
            for platform, task in platforms.items()
        }

    return CompareVideoResponse(tasks=tasks)


@router.get("/{session_id}/{shot_id}/download")
async def download_video(session_id: str, shot_id: str):
    """
    Download a single video by redirecting to the video URL.

    Returns a redirect to the actual video URL for direct download.
    """
    service = get_video_service()

    result = await service.get_video_status(session_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # Find the task with matching shot_id
    for task in result["tasks"]:
        if task["shot_id"] == shot_id:
            if task["status"] not in ["completed", "success"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Video not ready. Current status: {task['status']}"
                )

            video_url = task.get("video_url")
            if not video_url:
                raise HTTPException(status_code=404, detail="Video URL not available")

            # Redirect to the video URL for download
            return RedirectResponse(url=video_url, status_code=302)

    raise HTTPException(status_code=404, detail=f"Shot {shot_id} not found")


@router.get("/{session_id}/download")
async def download_all_videos(session_id: str):
    """
    Get download URLs for all completed videos.

    Returns a list of video URLs that can be downloaded.
    """
    service = get_video_service()

    result = await service.get_video_status(session_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    downloads = []
    for task in result["tasks"]:
        if task["status"] in ["completed", "success"] and task.get("video_url"):
            downloads.append({
                "shot_id": task["shot_id"],
                "platform": task["platform"],
                "video_url": task["video_url"],
                "filename": f"{session_id}_{task['shot_id']}.mp4",
            })

    if not downloads:
        raise HTTPException(status_code=404, detail="No completed videos available for download")

    return {
        "session_id": session_id,
        "total": len(downloads),
        "videos": downloads,
    }
