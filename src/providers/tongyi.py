"""
Tongyi Wanxiang (通义万相) Video Generation Provider

API Documentation: https://help.aliyun.com/zh/dashscope/

Supported Models:
- wan2.6-t2v: 万相2.6（有声视频）- 支持多镜头叙事、自动配音
- wan2.6-i2v: 万相2.6 图生视频（有声视频）
- wan2.5-t2v-preview: 万相2.5 preview（有声视频）
- wan2.2-t2v-plus: 万相2.2专业版（无声视频）
- wanx2.1-t2v-turbo: 万相2.1极速版（无声视频）
- wanx2.1-t2v-plus: 万相2.1专业版（无声视频）
"""

import requests
from datetime import datetime
from typing import Optional, Literal
from dataclasses import dataclass

from .base import VideoProvider, VideoTask, TaskStatus
from .config import get_config


@dataclass
class TongyiModelInfo:
    """Information about a Tongyi model."""
    name: str
    description: str
    has_audio: bool
    resolutions: list[str]
    durations: list[int]
    supports_multi_shot: bool = False


# Model specifications based on official documentation
TONGYI_MODELS = {
    # Text-to-Video models
    "wan2.6-t2v": TongyiModelInfo(
        name="wan2.6-t2v",
        description="万相2.6（有声视频）- 支持多镜头叙事、自动配音",
        has_audio=True,
        resolutions=["720P", "1080P"],
        durations=[5, 10, 15],
        supports_multi_shot=True,
    ),
    "wan2.5-t2v-preview": TongyiModelInfo(
        name="wan2.5-t2v-preview",
        description="万相2.5 preview（有声视频）",
        has_audio=True,
        resolutions=["480P", "720P", "1080P"],
        durations=[5, 10],
        supports_multi_shot=False,
    ),
    "wan2.2-t2v-plus": TongyiModelInfo(
        name="wan2.2-t2v-plus",
        description="万相2.2专业版（无声视频）- 稳定性提升，速度提升50%",
        has_audio=False,
        resolutions=["480P", "1080P"],
        durations=[5],
        supports_multi_shot=False,
    ),
    "wanx2.1-t2v-turbo": TongyiModelInfo(
        name="wanx2.1-t2v-turbo",
        description="万相2.1极速版（无声视频）",
        has_audio=False,
        resolutions=["480P", "720P"],
        durations=[5],
        supports_multi_shot=False,
    ),
    "wanx2.1-t2v-plus": TongyiModelInfo(
        name="wanx2.1-t2v-plus",
        description="万相2.1专业版（无声视频）",
        has_audio=False,
        resolutions=["720P"],
        durations=[5],
        supports_multi_shot=False,
    ),
    # Image-to-Video models
    "wan2.6-i2v": TongyiModelInfo(
        name="wan2.6-i2v",
        description="万相2.6 图生视频（有声视频）- 支持自定义音频",
        has_audio=True,
        resolutions=["720P", "1080P"],
        durations=[5, 10, 15],
        supports_multi_shot=True,
    ),
}


class TongyiProvider(VideoProvider):
    """
    Tongyi Wanxiang (Aliyun DashScope) video generation provider.

    Supports:
    - Text to Video (wan2.6-t2v, wan2.5-t2v-preview, wan2.2-t2v-plus, wanx2.1-t2v-turbo/plus)
    - Image to Video (wan2.6-i2v)
    - Audio generation (for 2.5+ models)
    - Multi-shot narrative (for wan2.6 models)
    """

    # API endpoint for video synthesis
    VIDEO_SYNTHESIS_ENDPOINT = "/services/aigc/video-generation/video-synthesis"
    TASK_QUERY_ENDPOINT = "/tasks"

    def __init__(self):
        super().__init__()
        self._name = "tongyi"
        self.initialize()

    def _get_headers(self, async_mode: bool = True) -> dict:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }
        if async_mode:
            headers["X-DashScope-Async"] = "enable"
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        async_mode: bool = True
    ) -> dict:
        """Make an API request to DashScope."""
        url = f"{self.config.base_url}{endpoint}"
        headers = self._get_headers(async_mode)

        if method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            response = requests.get(url, headers=headers, timeout=30)

        response.raise_for_status()
        result = response.json()

        # Check for API errors
        if "code" in result and result["code"]:
            error_msg = result.get("message", "Unknown error")
            error_code = result.get("code", "")
            raise Exception(f"Tongyi API Error [{error_code}]: {error_msg}")

        return result

    @staticmethod
    def get_supported_models() -> dict[str, TongyiModelInfo]:
        """Get all supported models with their specifications."""
        return TONGYI_MODELS

    @staticmethod
    def get_model_info(model: str) -> Optional[TongyiModelInfo]:
        """Get information about a specific model."""
        return TONGYI_MODELS.get(model)

    def submit_text_to_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        **kwargs
    ) -> VideoTask:
        """
        Submit a text-to-video generation task.

        Args:
            prompt: Video description text
            duration: Video duration in seconds (5, 10, or 15 depending on model)
            resolution: Video resolution ("480P", "720P", "1080P")
            **kwargs:
                - model: Model name (default: wan2.6-t2v)
                - prompt_extend: Enable prompt enhancement (default: True)
                - audio: Enable audio generation for supported models (default: True)
                - shot_type: "multi" for multi-shot narrative (wan2.6 only)
                - size: Alternative size format like "1280*720"
                - seed: Random seed for reproducibility

        Returns:
            VideoTask with task_id and initial status
        """
        defaults = self.config.defaults
        model = kwargs.get("model", self.config.model) or "wan2.6-t2v"

        # Get model info for validation
        model_info = self.get_model_info(model)

        # Build input
        input_data = {
            "prompt": prompt,
        }

        # Build parameters
        parameters = {}

        # Resolution - support both "720P" format and "1280*720" format
        if resolution:
            if "*" in resolution:
                parameters["size"] = resolution
            else:
                parameters["resolution"] = resolution
        elif "size" in kwargs:
            parameters["size"] = kwargs["size"]
        else:
            parameters["resolution"] = defaults.get("resolution", "720P")

        # Duration
        if duration:
            parameters["duration"] = duration
        else:
            parameters["duration"] = defaults.get("duration", 5)

        # Prompt extend (default True)
        parameters["prompt_extend"] = kwargs.get("prompt_extend", True)

        # Audio support for 2.5+ models
        if model_info and model_info.has_audio:
            parameters["audio"] = kwargs.get("audio", True)

        # Multi-shot narrative for wan2.6
        if kwargs.get("shot_type") == "multi":
            if model_info and model_info.supports_multi_shot:
                parameters["shot_type"] = "multi"

        # Optional seed
        if "seed" in kwargs:
            parameters["seed"] = kwargs["seed"]

        data = {
            "model": model,
            "input": input_data,
            "parameters": parameters,
        }

        result = self._make_request("POST", self.VIDEO_SYNTHESIS_ENDPOINT, data)

        output = result.get("output", {})
        return VideoTask(
            task_id=output.get("task_id", ""),
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
        **kwargs
    ) -> VideoTask:
        """
        Submit an image-to-video generation task.

        Args:
            image_url: URL of the reference image
            prompt: Video description text
            duration: Video duration in seconds
            resolution: Video resolution
            **kwargs:
                - model: Model name (default: wan2.6-i2v)
                - audio_url: URL of custom audio file
                - prompt_extend: Enable prompt enhancement
                - audio: Enable audio generation
                - shot_type: "multi" for multi-shot narrative

        Returns:
            VideoTask with task_id and initial status
        """
        defaults = self.config.defaults
        model = kwargs.get("model", "wan2.6-i2v")

        # Get model info
        model_info = self.get_model_info(model)

        # Build input
        input_data = {
            "prompt": prompt,
            "img_url": image_url,
        }

        # Support custom audio
        if "audio_url" in kwargs:
            input_data["audio_url"] = kwargs["audio_url"]

        # Build parameters
        parameters = {}

        # Resolution
        if resolution:
            if "*" in resolution:
                parameters["size"] = resolution
            else:
                parameters["resolution"] = resolution
        else:
            parameters["resolution"] = defaults.get("resolution", "720P")

        # Duration
        parameters["duration"] = duration or defaults.get("duration", 10)

        # Prompt extend
        parameters["prompt_extend"] = kwargs.get("prompt_extend", True)

        # Audio support
        if model_info and model_info.has_audio:
            parameters["audio"] = kwargs.get("audio", True)

        # Multi-shot narrative
        if kwargs.get("shot_type") == "multi":
            if model_info and model_info.supports_multi_shot:
                parameters["shot_type"] = "multi"

        data = {
            "model": model,
            "input": input_data,
            "parameters": parameters,
        }

        result = self._make_request("POST", self.VIDEO_SYNTHESIS_ENDPOINT, data)

        output = result.get("output", {})
        return VideoTask(
            task_id=output.get("task_id", ""),
            provider=self._name,
            status=TaskStatus.PENDING,
            metadata={"prompt": prompt, "image_url": image_url, "model": model, "params": data}
        )

    def get_task_status(self, task_id: str) -> VideoTask:
        """Query the status of a video generation task."""
        url = f"{self.config.base_url}{self.TASK_QUERY_ENDPOINT}/{task_id}"
        headers = self._get_headers(async_mode=False)

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Check for API errors
        if "code" in result and result["code"]:
            error_msg = result.get("message", "Unknown error")
            raise Exception(f"Tongyi API Error: {error_msg}")

        output = result.get("output", {})
        status_str = output.get("task_status", "PENDING").upper()

        # Map DashScope status to our status
        status_map = {
            "PENDING": TaskStatus.PENDING,
            "RUNNING": TaskStatus.PROCESSING,
            "SUCCEEDED": TaskStatus.COMPLETED,
            "FAILED": TaskStatus.FAILED,
            "CANCELED": TaskStatus.CANCELLED,
            "UNKNOWN": TaskStatus.PENDING,
        }

        status = status_map.get(status_str, TaskStatus.PENDING)

        # Get video URL if completed
        video_url = None
        if status == TaskStatus.COMPLETED:
            # Try different result formats
            video_result = output.get("video_url")
            if video_result:
                video_url = video_result
            else:
                results = output.get("results", [])
                if results:
                    video_url = results[0].get("url")

        # Get error message if failed
        error_message = None
        if status == TaskStatus.FAILED:
            error_message = output.get("message") or output.get("task_status_msg")

        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=status,
            progress=output.get("progress", 0),
            video_url=video_url,
            error_message=error_message,
            completed_at=datetime.now() if status in (TaskStatus.COMPLETED, TaskStatus.FAILED) else None,
            metadata=output
        )

    def test_connection(self) -> dict:
        """
        Test connection to DashScope API by verifying the API key.

        Returns:
            dict with success status and message
        """
        base_result = super().test_connection()
        if not base_result.get("success"):
            return base_result

        try:
            # Check API key format
            if not self.config.api_key:
                return {
                    "success": False,
                    "error": "API key is empty"
                }

            if not self.config.api_key.startswith("sk-"):
                return {
                    "success": False,
                    "error": "Invalid API key format. DashScope keys should start with 'sk-'"
                }

            # Try to list models or make a simple request to verify the key
            # We'll use a minimal request to check authentication
            headers = self._get_headers(async_mode=False)

            # Try to query a non-existent task to verify auth
            # A 404 means auth worked, other errors mean auth failed
            url = f"{self.config.base_url}/tasks/test-connection-check"
            response = requests.get(url, headers=headers, timeout=10)

            # If we get a 404 or task not found, the API key is valid
            if response.status_code == 404:
                return {
                    "success": True,
                    "message": "API key validated successfully",
                    "key_preview": f"{self.config.api_key[:10]}...",
                    "supported_models": list(TONGYI_MODELS.keys()),
                }

            result = response.json()

            # Check if it's an auth error
            if result.get("code") in ["InvalidApiKey", "Unauthorized", "AuthenticationFailed"]:
                return {
                    "success": False,
                    "error": f"Authentication failed: {result.get('message', 'Invalid API key')}"
                }

            # If we get here with a valid response, the key works
            return {
                "success": True,
                "message": "API key validated",
                "key_preview": f"{self.config.api_key[:10]}...",
                "supported_models": list(TONGYI_MODELS.keys()),
            }

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_models(self) -> list[dict]:
        """List all supported models with their specifications."""
        models = []
        for name, info in TONGYI_MODELS.items():
            models.append({
                "name": name,
                "description": info.description,
                "has_audio": info.has_audio,
                "resolutions": info.resolutions,
                "durations": info.durations,
                "supports_multi_shot": info.supports_multi_shot,
            })
        return models
