"""
Kling AI (可灵) Video Generation Provider - Omni-Video (O1) API

API Documentation: https://app.klingai.com/cn/dev/document-api
Model: kling-video-o1 (Omni-Video)
"""

import jwt
import time
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any

from ..base import VideoProvider, VideoTask, TaskStatus
from ..config import get_config


class KlingProvider(VideoProvider):
    """
    Kling AI video generation provider using Omni-Video (O1) API.

    Supports:
    - Text to Video (文生视频)
    - Image to Video with first/end frame (图生视频首尾帧)
    - Image/Element Reference (图片/主体参考)
    - Video Reference (视频参考)
    - Video Editing (指令变换)
    """

    # Supported models
    MODELS = {
        "kling-video-o1": {
            "name": "Omni-Video O1",
            "description": "多功能视频生成模型，支持文生视频、图生视频、视频编辑等",
            "modes": ["std", "pro"],
            "aspect_ratios": ["16:9", "9:16", "1:1"],
            "durations": {
                "text_to_video": ["5", "10"],
                "image_to_video": ["5", "10"],
                "with_reference": ["3", "4", "5", "6", "7", "8", "9", "10"]
            }
        }
    }

    def __init__(self):
        super().__init__()
        self._name = "kling"
        self.initialize()

    def _generate_jwt_token(self) -> str:
        """Generate JWT token for API authentication."""
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }

        now = int(time.time())
        payload = {
            "iss": self.config.access_key,
            "exp": now + 1800,  # 30 minutes expiry
            "nbf": now - 5
        }

        token = jwt.encode(
            payload,
            self.config.secret_key,
            algorithm="HS256",
            headers=headers
        )
        return token

    def _get_headers(self) -> dict:
        """Get request headers with authentication."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._generate_jwt_token()}"
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Make an API request to Kling."""
        url = f"{self.config.base_url}{endpoint}"
        headers = self._get_headers()

        if method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)

        response.raise_for_status()
        result = response.json()

        if result.get("code") != 0:
            raise Exception(f"Kling API Error: {result.get('message', 'Unknown error')}")

        return result

    def list_models(self) -> List[Dict[str, Any]]:
        """List available Kling models."""
        return [
            {
                "model_name": model_id,
                **model_info
            }
            for model_id, model_info in self.MODELS.items()
        ]

    def submit_text_to_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        model: str = "kling-video-o1",
        **kwargs
    ) -> VideoTask:
        """
        Submit a text-to-video generation task using Omni-Video API.

        Args:
            prompt: Text description for video generation (max 2500 chars)
            duration: Video duration in seconds (5 or 10 for text-to-video)
            model: Model name (default: kling-video-o1)
            **kwargs:
                - mode: "std" (standard) or "pro" (high quality), default "std"
                - aspect_ratio: "16:9", "9:16", or "1:1", required for text-to-video
        """
        defaults = self.config.defaults

        # Duration must be 5 or 10 for text-to-video
        video_duration = str(duration) if duration in [5, 10] else defaults.get("duration", "5")

        data = {
            "model_name": model,
            "prompt": prompt,
            "mode": kwargs.get("mode", defaults.get("mode", "std")),
            "aspect_ratio": kwargs.get("aspect_ratio", defaults.get("aspect_ratio", "16:9")),
            "duration": video_duration
        }

        # Optional callback URL
        if "callback_url" in kwargs:
            data["callback_url"] = kwargs["callback_url"]

        result = self._make_request("POST", "/v1/videos/omni-video", data)

        task_data = result.get("data", {})
        return VideoTask(
            task_id=task_data.get("task_id", ""),
            provider=self._name,
            status=self._map_status(task_data.get("task_status", "submitted")),
            metadata={"prompt": prompt, "params": data}
        )

    def submit_image_to_video(
        self,
        image_url: str,
        prompt: str,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        model: str = "kling-video-o1",
        **kwargs
    ) -> VideoTask:
        """
        Submit an image-to-video generation task using Omni-Video API.

        Args:
            image_url: URL of the first frame image
            prompt: Text description for video generation
            duration: Video duration in seconds (5 or 10)
            model: Model name (default: kling-video-o1)
            **kwargs:
                - mode: "std" or "pro"
                - end_frame_url: URL of the end frame image (optional)
        """
        defaults = self.config.defaults

        # Build image_list
        image_list = [
            {
                "image_url": image_url,
                "type": "first_frame"
            }
        ]

        # Add end frame if provided
        if "end_frame_url" in kwargs:
            image_list.append({
                "image_url": kwargs["end_frame_url"],
                "type": "end_frame"
            })

        # Duration must be 5 or 10 for image-to-video
        video_duration = str(duration) if duration in [5, 10] else defaults.get("duration", "5")

        data = {
            "model_name": model,
            "prompt": prompt,
            "image_list": image_list,
            "mode": kwargs.get("mode", defaults.get("mode", "std")),
            "duration": video_duration
        }

        # Note: aspect_ratio is not supported for image-to-video

        result = self._make_request("POST", "/v1/videos/omni-video", data)

        task_data = result.get("data", {})
        return VideoTask(
            task_id=task_data.get("task_id", ""),
            provider=self._name,
            status=self._map_status(task_data.get("task_status", "submitted")),
            metadata={"prompt": prompt, "image_url": image_url, "params": data}
        )

    def submit_with_reference(
        self,
        prompt: str,
        image_list: Optional[List[Dict[str, str]]] = None,
        element_list: Optional[List[Dict[str, int]]] = None,
        video_list: Optional[List[Dict[str, str]]] = None,
        duration: Optional[int] = None,
        model: str = "kling-video-o1",
        **kwargs
    ) -> VideoTask:
        """
        Submit a video generation task with image/element/video references.

        This is the full Omni-Video API that supports all reference types.

        Args:
            prompt: Text prompt with reference placeholders like <<<image_1>>>, <<<element_1>>>, <<<video_1>>>
            image_list: List of image references [{"image_url": "..."}, ...]
            element_list: List of element references [{"element_id": 123}, ...]
            video_list: List of video references [{"video_url": "...", "refer_type": "feature|base", "keep_original_sound": "yes|no"}]
            duration: Video duration (3-10 seconds when using references)
            model: Model name (default: kling-video-o1)
            **kwargs:
                - mode: "std" or "pro"
                - aspect_ratio: "16:9", "9:16", "1:1" (not supported for video editing or image-to-video)
        """
        defaults = self.config.defaults

        data = {
            "model_name": model,
            "prompt": prompt,
            "mode": kwargs.get("mode", defaults.get("mode", "pro"))
        }

        if image_list:
            data["image_list"] = image_list

        if element_list:
            data["element_list"] = element_list

        if video_list:
            data["video_list"] = video_list

        # Duration can be 3-10 when using references
        if duration:
            data["duration"] = str(duration)

        # aspect_ratio only supported in certain cases
        if "aspect_ratio" in kwargs:
            data["aspect_ratio"] = kwargs["aspect_ratio"]

        result = self._make_request("POST", "/v1/videos/omni-video", data)

        task_data = result.get("data", {})
        return VideoTask(
            task_id=task_data.get("task_id", ""),
            provider=self._name,
            status=self._map_status(task_data.get("task_status", "submitted")),
            metadata={"prompt": prompt, "params": data}
        )

    def _map_status(self, status_str: str) -> TaskStatus:
        """Map Kling status string to TaskStatus enum."""
        status_map = {
            "submitted": TaskStatus.PENDING,
            "processing": TaskStatus.PROCESSING,
            "succeed": TaskStatus.COMPLETED,
            "failed": TaskStatus.FAILED,
        }
        return status_map.get(status_str.lower(), TaskStatus.PENDING)

    def get_task_status(self, task_id: str) -> VideoTask:
        """Query the status of a video generation task."""
        result = self._make_request("GET", f"/v1/videos/omni-video/{task_id}")

        task_data = result.get("data", {})
        status = self._map_status(task_data.get("task_status", "submitted"))

        # Get video URL if completed
        video_url = None
        video_duration = None
        if status == TaskStatus.COMPLETED:
            videos = task_data.get("task_result", {}).get("videos", [])
            if videos:
                video_url = videos[0].get("url")
                video_duration = videos[0].get("duration")

        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=status,
            video_url=video_url,
            error_message=task_data.get("task_status_msg") if status == TaskStatus.FAILED else None,
            completed_at=datetime.now() if status in (TaskStatus.COMPLETED, TaskStatus.FAILED) else None,
            metadata={
                "task_data": task_data,
                "video_duration": video_duration
            }
        )

    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 10
    ) -> VideoTask:
        """
        Wait for a task to complete.

        Args:
            task_id: The task ID to wait for
            timeout: Maximum time to wait in seconds (default 300)
            poll_interval: Time between status checks in seconds (default 10)
        """
        start_time = time.time()

        while True:
            task = self.get_task_status(task_id)

            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                return task

            elapsed = time.time() - start_time
            if elapsed > timeout:
                task.status = TaskStatus.FAILED
                task.error_message = f"Timeout after {timeout} seconds"
                return task

            time.sleep(poll_interval)

    def test_connection(self) -> dict:
        """Test connection to Kling API."""
        base_result = super().test_connection()
        if not base_result.get("success"):
            return base_result

        try:
            # Try to generate a JWT token
            token = self._generate_jwt_token()
            return {
                "success": True,
                "message": "JWT token generated successfully",
                "token_preview": token[:50] + "...",
                "base_url": self.config.base_url,
                "model": "kling-video-o1"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
