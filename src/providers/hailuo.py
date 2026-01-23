"""
Hailuo AI / MiniMax (海螺视频) Video Generation Provider

API Documentation: https://platform.minimaxi.com/docs/api-reference/video-generation-t2v
Base URL: https://api.minimaxi.com
"""

import time
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any

from .base import VideoProvider, VideoTask, TaskStatus
from .config import get_config


class HailuoProvider(VideoProvider):
    """
    Hailuo AI (MiniMax) video generation provider.

    Supports:
    - Text to Video (文生视频)
    - Image to Video (图生视频)
    - First/Last Frame Video (首尾帧生成视频)
    - Subject Reference Video (主体参考视频)

    Camera Control Instructions (运镜指令):
    Supports 15 camera movement instructions in prompt using [指令] syntax:
    - 左右移: [左移], [右移]
    - 左右摇: [左摇], [右摇]
    - 推拉: [推进], [拉远]
    - 升降: [上升], [下降]
    - 上下摇: [上摇], [下摇]
    - 变焦: [变焦推近], [变焦拉远]
    - 其他: [晃动], [跟随], [固定]
    """

    # Supported models
    MODELS = {
        # Text-to-Video models
        "MiniMax-Hailuo-2.3": {
            "name": "Hailuo 2.3",
            "type": "t2v",
            "description": "最新文生视频模型，支持运镜控制",
            "resolutions": {"6": ["768P", "1080P"], "10": ["768P"]},
            "default_resolution": "768P",
            "supports_camera_control": True
        },
        "MiniMax-Hailuo-02": {
            "name": "Hailuo 02",
            "type": "t2v",
            "description": "文生视频模型，支持运镜控制",
            "resolutions": {"6": ["768P", "1080P"], "10": ["768P"]},
            "default_resolution": "768P",
            "supports_camera_control": True
        },
        "T2V-01-Director": {
            "name": "T2V Director",
            "type": "t2v",
            "description": "导演模式文生视频",
            "resolutions": {"6": ["720P"]},
            "default_resolution": "720P",
            "supports_camera_control": True
        },
        "T2V-01": {
            "name": "T2V Basic",
            "type": "t2v",
            "description": "基础文生视频模型",
            "resolutions": {"6": ["720P"]},
            "default_resolution": "720P",
            "supports_camera_control": False
        },
        # Image-to-Video models
        "MiniMax-Hailuo-2.3-Fast": {
            "name": "Hailuo 2.3 Fast",
            "type": "i2v",
            "description": "快速图生视频模型",
            "resolutions": {"6": ["768P", "1080P"], "10": ["768P"]},
            "default_resolution": "768P",
            "supports_camera_control": True
        },
        "I2V-01-Director": {
            "name": "I2V Director",
            "type": "i2v",
            "description": "导演模式图生视频",
            "resolutions": {"6": ["720P"]},
            "default_resolution": "720P",
            "supports_camera_control": True
        },
        "I2V-01-live": {
            "name": "I2V Live",
            "type": "i2v",
            "description": "实时图生视频模型",
            "resolutions": {"6": ["720P"]},
            "default_resolution": "720P",
            "supports_camera_control": False
        },
        "I2V-01": {
            "name": "I2V Basic",
            "type": "i2v",
            "description": "基础图生视频模型",
            "resolutions": {"6": ["720P"]},
            "default_resolution": "720P",
            "supports_camera_control": False
        },
        # Subject Reference model
        "S2V-01": {
            "name": "Subject Reference",
            "type": "s2v",
            "description": "主体参考视频生成",
            "resolutions": {"6": ["720P"]},
            "default_resolution": "720P",
            "supports_camera_control": False
        }
    }

    def __init__(self):
        super().__init__()
        self._name = "hailuo"
        self.initialize()

    def _get_headers(self) -> dict:
        """Get request headers with authentication."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None) -> dict:
        """Make an API request to MiniMax."""
        url = f"{self.config.base_url}{endpoint}"
        headers = self._get_headers()

        if method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers, params=params)

        response.raise_for_status()
        result = response.json()

        # Check for API errors
        base_resp = result.get("base_resp", {})
        if base_resp.get("status_code", 0) != 0:
            raise Exception(f"Hailuo API Error [{base_resp.get('status_code')}]: {base_resp.get('status_msg')}")

        return result

    def list_models(self) -> List[Dict[str, Any]]:
        """List available Hailuo models."""
        return [
            {
                "model": model_id,
                **model_info
            }
            for model_id, model_info in self.MODELS.items()
        ]

    def submit_text_to_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        model: str = "MiniMax-Hailuo-2.3",
        **kwargs
    ) -> VideoTask:
        """
        Submit a text-to-video generation task.

        Args:
            prompt: Text description (max 2000 chars). Supports camera control [指令] syntax.
            duration: Video duration in seconds (6 or 10)
            resolution: Video resolution (720P, 768P, 1080P)
            model: Model name (default: MiniMax-Hailuo-2.3)
            **kwargs:
                - prompt_optimizer: Auto optimize prompt (default True)
                - fast_pretreatment: Speed up prompt optimization (default False)
                - aigc_watermark: Add watermark (default False)
                - callback_url: Callback URL for status updates
        """
        defaults = self.config.defaults

        data = {
            "model": model,
            "prompt": prompt,
        }

        # Duration (6 or 10 seconds)
        if duration:
            data["duration"] = duration
        elif defaults.get("duration"):
            data["duration"] = defaults.get("duration")

        # Resolution
        if resolution:
            data["resolution"] = resolution
        elif defaults.get("resolution"):
            data["resolution"] = defaults.get("resolution")

        # Optional parameters
        if "prompt_optimizer" in kwargs:
            data["prompt_optimizer"] = kwargs["prompt_optimizer"]

        if "fast_pretreatment" in kwargs:
            data["fast_pretreatment"] = kwargs["fast_pretreatment"]

        if "aigc_watermark" in kwargs:
            data["aigc_watermark"] = kwargs["aigc_watermark"]

        if "callback_url" in kwargs:
            data["callback_url"] = kwargs["callback_url"]

        result = self._make_request("POST", "/v1/video_generation", data)

        task_id = result.get("task_id", "")
        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=TaskStatus.PENDING,
            metadata={"prompt": prompt, "model": model, "params": data}
        )

    def submit_image_to_video(
        self,
        image_url: str,
        prompt: str,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        model: str = "MiniMax-Hailuo-2.3",
        **kwargs
    ) -> VideoTask:
        """
        Submit an image-to-video generation task.

        Args:
            image_url: First frame image URL or base64 data URL
            prompt: Text description (max 2000 chars)
            duration: Video duration in seconds (6 or 10)
            resolution: Video resolution
            model: Model name (default: MiniMax-Hailuo-2.3)
            **kwargs:
                - last_frame_image: End frame image URL (for MiniMax-Hailuo-02 only)
                - prompt_optimizer: Auto optimize prompt (default True)
                - fast_pretreatment: Speed up prompt optimization (default False)
                - aigc_watermark: Add watermark (default False)
        """
        defaults = self.config.defaults

        data = {
            "model": model,
            "first_frame_image": image_url,
        }

        # Prompt is optional for I2V
        if prompt:
            data["prompt"] = prompt

        # Duration
        if duration:
            data["duration"] = duration
        elif defaults.get("duration"):
            data["duration"] = defaults.get("duration")

        # Resolution
        if resolution:
            data["resolution"] = resolution
        elif defaults.get("resolution"):
            data["resolution"] = defaults.get("resolution")

        # Last frame for first-last frame video (MiniMax-Hailuo-02 only)
        if "last_frame_image" in kwargs:
            data["last_frame_image"] = kwargs["last_frame_image"]

        # Optional parameters
        if "prompt_optimizer" in kwargs:
            data["prompt_optimizer"] = kwargs["prompt_optimizer"]

        if "fast_pretreatment" in kwargs:
            data["fast_pretreatment"] = kwargs["fast_pretreatment"]

        if "aigc_watermark" in kwargs:
            data["aigc_watermark"] = kwargs["aigc_watermark"]

        result = self._make_request("POST", "/v1/video_generation", data)

        task_id = result.get("task_id", "")
        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=TaskStatus.PENDING,
            metadata={"prompt": prompt, "image_url": image_url, "model": model, "params": data}
        )

    def submit_subject_reference_video(
        self,
        subject_image_url: str,
        prompt: str,
        subject_type: str = "character",
        **kwargs
    ) -> VideoTask:
        """
        Submit a video generation task with subject reference.

        This maintains subject consistency (e.g., face) in the generated video.

        Args:
            subject_image_url: Subject reference image URL or base64
            prompt: Text description (max 2000 chars)
            subject_type: Subject type, currently only "character" supported
            **kwargs:
                - prompt_optimizer: Auto optimize prompt (default True)
                - aigc_watermark: Add watermark (default False)
        """
        data = {
            "model": "S2V-01",
            "prompt": prompt,
            "subject_reference": [
                {
                    "type": subject_type,
                    "image": [subject_image_url]
                }
            ]
        }

        if "prompt_optimizer" in kwargs:
            data["prompt_optimizer"] = kwargs["prompt_optimizer"]

        if "aigc_watermark" in kwargs:
            data["aigc_watermark"] = kwargs["aigc_watermark"]

        result = self._make_request("POST", "/v1/video_generation", data)

        task_id = result.get("task_id", "")
        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=TaskStatus.PENDING,
            metadata={"prompt": prompt, "subject_image": subject_image_url, "model": "S2V-01"}
        )

    def _map_status(self, status_str: str) -> TaskStatus:
        """Map MiniMax status string to TaskStatus enum."""
        status_map = {
            "Preparing": TaskStatus.PENDING,
            "Queueing": TaskStatus.PENDING,
            "Processing": TaskStatus.PROCESSING,
            "Success": TaskStatus.COMPLETED,
            "Fail": TaskStatus.FAILED,
        }
        return status_map.get(status_str, TaskStatus.PENDING)

    def get_file_download_url(self, file_id: str) -> str:
        """
        Get the download URL for a completed video file.

        Args:
            file_id: The file ID returned when task succeeds

        Returns:
            Download URL (valid for 1 hour)
        """
        result = self._make_request("GET", "/v1/files/retrieve", params={"file_id": file_id})
        file_info = result.get("file", {})
        return file_info.get("download_url", "")

    def get_task_status(self, task_id: str) -> VideoTask:
        """Query the status of a video generation task."""
        result = self._make_request("GET", "/v1/query/video_generation", params={"task_id": task_id})

        status_str = result.get("status", "Queueing")
        status = self._map_status(status_str)

        # Get video URL if completed
        video_url = None
        file_id = result.get("file_id")
        video_width = result.get("video_width")
        video_height = result.get("video_height")

        if status == TaskStatus.COMPLETED and file_id:
            # Need to retrieve file to get download URL
            video_url = self.get_file_download_url(file_id)

        error_message = None
        if status == TaskStatus.FAILED:
            base_resp = result.get("base_resp", {})
            error_message = base_resp.get("status_msg", "Unknown error")

        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=status,
            video_url=video_url,
            error_message=error_message,
            completed_at=datetime.now() if status in (TaskStatus.COMPLETED, TaskStatus.FAILED) else None,
            metadata={
                "task_data": result,
                "file_id": file_id,
                "video_width": video_width,
                "video_height": video_height
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
        """Test connection to MiniMax API."""
        base_result = super().test_connection()
        if not base_result.get("success"):
            return base_result

        try:
            # Verify API key format
            if not self.config.api_key:
                return {
                    "success": False,
                    "error": "API key is empty"
                }

            return {
                "success": True,
                "message": "API key configured",
                "key_preview": f"{self.config.api_key[:10]}..." if len(self.config.api_key) > 10 else "***",
                "base_url": self.config.base_url,
                "default_model": "MiniMax-Hailuo-2.3"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
