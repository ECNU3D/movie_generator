"""
Video Service

Handles video generation, status checking, and downloads.
"""

import asyncio
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agents import SessionManager, VideoProducerAgent
from agents.state import AgentState

_executor = ThreadPoolExecutor(max_workers=4)


class VideoService:
    """Service for video generation operations."""

    def __init__(self, db_path: str = "story_generator.db"):
        self.db_path = db_path
        self.session_manager = SessionManager(db_path)
        self._producer = VideoProducerAgent()

    def _get_provider(self, platform: str):
        """Get video provider for platform."""
        return self._producer._get_provider(platform)

    async def get_video_status(self, session_id: str) -> Dict[str, Any]:
        """Get video generation status for a session."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return {"error": "Session not found"}

        if not state.video_tasks:
            return {"error": "No video tasks found"}

        platform = state.request.target_platform if state.request else "kling"
        tasks = []
        completed = 0

        for shot_id, task_info in state.video_tasks.items():
            task_id = task_info.get("task_id")
            current_status = task_info.get("status", "unknown")

            # Check status from provider if not terminal
            if task_id and current_status not in ["completed", "success", "failed"]:
                try:
                    provider = self._get_provider(platform)
                    task = provider.get_task_status(task_id)
                    status = task.status.value if hasattr(task.status, 'value') else str(task.status)
                    video_url = task.video_url
                    error = task.error_message

                    # Update state
                    state.video_tasks[shot_id].update({
                        "status": status,
                        "video_url": video_url,
                        "error": error,
                    })
                except Exception as e:
                    status = "error"
                    video_url = None
                    error = str(e)
            else:
                status = current_status
                video_url = task_info.get("video_url")
                error = task_info.get("error")

            if status in ["completed", "success"]:
                completed += 1

            tasks.append({
                "shot_id": shot_id,
                "task_id": task_id,
                "platform": platform,
                "status": status,
                "video_url": video_url,
                "error": error,
                "prompt": task_info.get("prompt"),
            })

        return {
            "session_id": session_id,
            "platform": platform,
            "tasks": tasks,
            "completed": completed,
            "total": len(tasks),
            "all_complete": completed == len(tasks),
        }

    async def retry_video(
        self,
        session_id: str,
        shot_id: str,
        platform: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate or retry video generation for a specific shot."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return {"error": "Session not found"}

        # Check if shot_id exists in video_tasks or video_prompts
        has_task = state.video_tasks and shot_id in state.video_tasks
        has_prompt = state.video_prompts and shot_id in state.video_prompts

        if not has_task and not has_prompt:
            return {"error": f"Shot {shot_id} not found in tasks or prompts"}

        # Use provided platform or original
        target_platform = platform or (state.request.target_platform if state.request else "kling")

        # Use provided prompt, or prompt from task, or prompt from video_prompts
        target_prompt = prompt
        if not target_prompt and has_task:
            target_prompt = state.video_tasks[shot_id].get("prompt")
        if not target_prompt and has_prompt:
            target_prompt = state.video_prompts.get(shot_id, "")

        if not target_prompt:
            return {"error": "No prompt available for this shot"}

        # Submit new task
        try:
            provider = self._get_provider(target_platform)

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                _executor,
                lambda p=provider, pr=target_prompt: p.submit_text_to_video(pr)
            )

            # Initialize video_tasks if not exists
            if not state.video_tasks:
                state.video_tasks = {}

            # Update state
            state.video_tasks[shot_id] = {
                "task_id": result.task_id,
                "status": "submitted",
                "platform": target_platform,
                "prompt": target_prompt,
            }

            # Save state
            self.session_manager.save_state(session_id, state)

            return {
                "shot_id": shot_id,
                "task_id": result.task_id,
                "platform": target_platform,
                "status": "submitted",
            }

        except Exception as e:
            # Save error state
            if not state.video_tasks:
                state.video_tasks = {}
            state.video_tasks[shot_id] = {
                "task_id": None,
                "status": "failed",
                "platform": target_platform,
                "prompt": target_prompt,
                "error": str(e),
            }
            self.session_manager.save_state(session_id, state)
            return {"error": str(e)}

    async def compare_videos(
        self,
        session_id: str,
        shot_ids: List[str],
        platforms: List[str],
    ) -> Dict[str, Any]:
        """Generate videos on multiple platforms for comparison."""
        state = self.session_manager.load_state(session_id)
        if not state:
            return {"error": "Session not found"}

        results = {}

        for shot_id in shot_ids:
            prompt = state.video_prompts.get(shot_id)
            if not prompt:
                continue

            results[shot_id] = {}

            for platform in platforms:
                try:
                    provider = self._get_provider(platform)

                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        _executor,
                        lambda p=provider, pr=prompt: p.submit_text_to_video(pr)
                    )

                    results[shot_id][platform] = {
                        "shot_id": shot_id,
                        "task_id": result.task_id,
                        "platform": platform,
                        "status": "submitted",
                    }

                except Exception as e:
                    results[shot_id][platform] = {
                        "shot_id": shot_id,
                        "task_id": None,
                        "platform": platform,
                        "status": "error",
                        "error": str(e),
                    }

        return {"tasks": results}


# Global service instance
_video_service: Optional[VideoService] = None


def get_video_service() -> VideoService:
    """Get the global video service instance."""
    global _video_service
    if _video_service is None:
        _video_service = VideoService()
    return _video_service
