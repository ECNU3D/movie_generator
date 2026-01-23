"""
JiMeng AI (即梦AI) Video Generation Provider

API Documentation: https://www.volcengine.com/docs/85621

Supported Models (req_key):
- jimeng_t2v_v30: 视频生成3.0 (720P) - 文生视频
- jimeng_t2v_v30_1080p: 视频生成3.0 (1080P) - 文生视频
- jimeng_t2v_v30_pro: 视频生成3.0 Pro - 文生视频，支持多镜头叙事
- jimeng_ti2v_v30_pro: 视频生成3.0 Pro - 图生视频（首帧）
"""

import base64
import hashlib
import hmac
import json
import requests
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass
from urllib.parse import quote

from .base import VideoProvider, VideoTask, TaskStatus
from .config import get_config


@dataclass
class JimengModelInfo:
    """Information about a Jimeng model."""
    req_key: str
    name: str
    description: str
    type: str  # "t2v" or "i2v"
    resolutions: list[str]
    durations: list[int]  # in seconds
    frames_map: dict[int, int]  # duration -> frames
    aspect_ratios: list[str]


# Model specifications based on official documentation
JIMENG_MODELS = {
    "jimeng_t2v_v30": JimengModelInfo(
        req_key="jimeng_t2v_v30",
        name="视频生成3.0 (720P)",
        description="文生视频 - 720P标准版，支持5秒/10秒视频",
        type="t2v",
        resolutions=["720P"],
        durations=[5, 10],
        frames_map={5: 121, 10: 241},
        aspect_ratios=["16:9", "9:16", "4:3", "3:4", "1:1"],
    ),
    "jimeng_t2v_v30_1080p": JimengModelInfo(
        req_key="jimeng_t2v_v30_1080p",
        name="视频生成3.0 (1080P)",
        description="文生视频 - 1080P高清版，支持5秒/10秒视频",
        type="t2v",
        resolutions=["1080P"],
        durations=[5, 10],
        frames_map={5: 121, 10: 241},
        aspect_ratios=["16:9", "9:16", "4:3", "3:4", "1:1"],
    ),
    "jimeng_t2v_v30_pro": JimengModelInfo(
        req_key="jimeng_t2v_v30_pro",
        name="视频生成3.0 Pro",
        description="文生视频Pro版 - 支持多镜头叙事，精准指令遵循",
        type="t2v",
        resolutions=["720P", "1080P"],
        durations=[5, 10],
        frames_map={5: 121, 10: 241},
        aspect_ratios=["16:9", "9:16", "4:3", "3:4", "1:1"],
    ),
    "jimeng_ti2v_v30_pro": JimengModelInfo(
        req_key="jimeng_ti2v_v30_pro",
        name="视频生成3.0 Pro (图生视频)",
        description="图生视频Pro版 - 首帧图片+文本提示词生成视频",
        type="i2v",
        resolutions=["720P", "1080P"],
        durations=[5, 10],
        frames_map={5: 121, 10: 241},
        aspect_ratios=["16:9", "9:16", "4:3", "3:4", "1:1"],
    ),
}


class JimengProvider(VideoProvider):
    """
    JiMeng AI (Volcengine) video generation provider.

    Supports:
    - Text to Video (720P, 1080P, Pro)
    - Image to Video (Pro - first frame reference)
    - Multiple aspect ratios
    - 5s and 10s video durations
    """

    API_VERSION = "2022-08-31"
    DEFAULT_MODEL = "jimeng_t2v_v30_1080p"

    def __init__(self):
        super().__init__()
        self._name = "jimeng"
        self.initialize()

    def _sign_request(self, method: str, params: dict, body: str) -> dict:
        """
        Generate Volcengine API signature (HMAC-SHA256).
        """
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y%m%dT%H%M%SZ")
        date_short = now.strftime("%Y%m%d")

        host = "visual.volcengineapi.com"
        uri = "/"

        # Sort and encode query parameters
        sorted_params = sorted(params.items())
        query_string = "&".join(f"{quote(str(k), safe='')}={quote(str(v), safe='')}" for k, v in sorted_params)

        # Calculate body hash
        body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()

        # Headers to sign
        headers_to_sign = {
            "host": host,
            "x-date": date_str,
            "x-content-sha256": body_hash,
            "content-type": "application/json",
        }

        signed_headers = ";".join(sorted(headers_to_sign.keys()))
        canonical_headers = "\n".join(f"{k}:{v}" for k, v in sorted(headers_to_sign.items()))

        # Canonical request
        canonical_request = "\n".join([
            method,
            uri,
            query_string,
            canonical_headers + "\n",
            signed_headers,
            body_hash
        ])

        # String to sign
        region = self.config.region or "cn-north-1"
        service = self.config.service or "cv"
        credential_scope = f"{date_short}/{region}/{service}/request"

        string_to_sign = "\n".join([
            "HMAC-SHA256",
            date_str,
            credential_scope,
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        ])

        # Calculate signature
        def hmac_sha256(key: bytes, msg: str) -> bytes:
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

        k_date = hmac_sha256(self.config.secret_key.encode('utf-8'), date_short)
        k_region = hmac_sha256(k_date, region)
        k_service = hmac_sha256(k_region, service)
        k_signing = hmac_sha256(k_service, "request")
        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # Build authorization header
        authorization = (
            f"HMAC-SHA256 "
            f"Credential={self.config.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )

        return {
            "Host": host,
            "X-Date": date_str,
            "X-Content-Sha256": body_hash,
            "Content-Type": "application/json",
            "Authorization": authorization,
        }

    def _make_request(self, action: str, body: dict) -> dict:
        """Make an API request to Volcengine Visual API."""
        params = {
            "Action": action,
            "Version": self.API_VERSION,
        }

        body_str = json.dumps(body)
        headers = self._sign_request("POST", params, body_str)

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{self.config.base_url}?{query_string}"

        response = requests.post(url, data=body_str, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Check for API errors
        if "ResponseMetadata" in result:
            error = result["ResponseMetadata"].get("Error")
            if error:
                code = error.get("Code", "Unknown")
                message = error.get("Message", "Unknown error")
                raise Exception(f"JiMeng API Error [{code}]: {message}")

        return result

    @staticmethod
    def get_supported_models() -> dict[str, JimengModelInfo]:
        """Get all supported models with their specifications."""
        return JIMENG_MODELS

    @staticmethod
    def get_model_info(model: str) -> Optional[JimengModelInfo]:
        """Get information about a specific model."""
        return JIMENG_MODELS.get(model)

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
            prompt: Video description (max 800 chars recommended)
            duration: Video duration in seconds (5 or 10)
            resolution: Not used directly - select model instead
            **kwargs:
                - model: Model req_key (default: jimeng_t2v_v30_1080p)
                - aspect_ratio: "16:9", "9:16", "4:3", "3:4", "1:1"
                - seed: Random seed (-1 for random)
                - frames: Override frame count (121=5s, 241=10s)

        Returns:
            VideoTask with task_id and initial status
        """
        model = kwargs.get("model", self.config.model) or self.DEFAULT_MODEL
        model_info = self.get_model_info(model)

        if not model_info:
            raise ValueError(f"Unknown model: {model}. Available: {list(JIMENG_MODELS.keys())}")

        # Determine frames from duration
        duration = duration or 5
        if duration not in model_info.frames_map:
            duration = 5  # Default to 5 seconds
        frames = kwargs.get("frames", model_info.frames_map[duration])

        # Build request body
        body = {
            "req_key": model_info.req_key,
            "prompt": prompt[:800],  # Limit prompt length
            "frames": frames,
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "seed": kwargs.get("seed", -1),
        }

        result = self._make_request("CVSync2AsyncSubmitTask", body)

        # Extract task_id from response
        data = result.get("data", {})
        task_id = data.get("task_id", "")

        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=TaskStatus.PENDING,
            metadata={
                "prompt": prompt,
                "model": model,
                "frames": frames,
                "duration": duration,
                "params": body
            }
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
            image_url: URL of the first frame image, or local file path
            prompt: Motion/action description
            duration: Video duration in seconds (5 or 10)
            resolution: Not used directly
            **kwargs:
                - model: Model req_key (default: jimeng_ti2v_v30_pro)
                - aspect_ratio: "16:9", "9:16", etc.
                - seed: Random seed (-1 for random)

        Returns:
            VideoTask with task_id and initial status
        """
        model = kwargs.get("model", "jimeng_ti2v_v30_pro")
        model_info = self.get_model_info(model)

        if not model_info:
            model_info = JIMENG_MODELS["jimeng_ti2v_v30_pro"]

        # Determine frames from duration
        duration = duration or 5
        if duration not in model_info.frames_map:
            duration = 5
        frames = kwargs.get("frames", model_info.frames_map[duration])

        # Handle image input
        if image_url.startswith("http"):
            image_urls = [image_url]
            binary_data = None
        else:
            # Local file - convert to base64
            with open(image_url, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            image_urls = None
            binary_data = [image_data]

        # Build request body
        body = {
            "req_key": model_info.req_key,
            "prompt": prompt[:800],
            "frames": frames,
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "seed": kwargs.get("seed", -1),
        }

        if image_urls:
            body["image_urls"] = image_urls
        if binary_data:
            body["binary_data_base64"] = binary_data

        result = self._make_request("CVSync2AsyncSubmitTask", body)

        data = result.get("data", {})
        task_id = data.get("task_id", "")

        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=TaskStatus.PENDING,
            metadata={
                "prompt": prompt,
                "image_url": image_url,
                "model": model,
                "duration": duration,
            }
        )

    def get_task_status(self, task_id: str) -> VideoTask:
        """Query the status of a video generation task."""
        body = {
            "req_key": self.config.model or self.DEFAULT_MODEL,
            "task_id": task_id,
        }

        result = self._make_request("CVSync2AsyncGetResult", body)

        data = result.get("data", {})
        status_str = data.get("status", "pending").lower()

        # Map Jimeng status to our status
        status_map = {
            "not_start": TaskStatus.PENDING,
            "pending": TaskStatus.PENDING,
            "running": TaskStatus.PROCESSING,
            "done": TaskStatus.COMPLETED,
            "success": TaskStatus.COMPLETED,
            "failed": TaskStatus.FAILED,
            "fail": TaskStatus.FAILED,
        }

        status = status_map.get(status_str, TaskStatus.PENDING)

        # Get video URL if completed
        video_url = None
        if status == TaskStatus.COMPLETED:
            video_url = data.get("video_url")
            # Alternative field names
            if not video_url:
                resp_data = data.get("resp_data", {})
                if isinstance(resp_data, str):
                    try:
                        resp_data = json.loads(resp_data)
                    except:
                        resp_data = {}
                video_url = resp_data.get("video_url") or resp_data.get("url")

        # Get error message
        error_message = None
        if status == TaskStatus.FAILED:
            error_message = data.get("message") or data.get("error_msg")

        return VideoTask(
            task_id=task_id,
            provider=self._name,
            status=status,
            progress=data.get("progress", 0),
            video_url=video_url,
            error_message=error_message,
            completed_at=datetime.now() if status in (TaskStatus.COMPLETED, TaskStatus.FAILED) else None,
            metadata=data
        )

    def test_connection(self) -> dict:
        """Test connection to Volcengine API."""
        base_result = super().test_connection()
        if not base_result.get("success"):
            return base_result

        try:
            # Verify credentials are present
            if not self.config.access_key or not self.config.secret_key:
                return {
                    "success": False,
                    "error": "Access key or secret key is missing"
                }

            # Try to sign a request to verify credentials format
            test_body = json.dumps({"test": "connection"})
            headers = self._sign_request(
                "POST",
                {"Action": "Test", "Version": self.API_VERSION},
                test_body
            )

            return {
                "success": True,
                "message": "Credentials configured, signature generation successful",
                "access_key_preview": f"{self.config.access_key[:12]}...",
                "supported_models": list(JIMENG_MODELS.keys()),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_models(self) -> list[dict]:
        """List all supported models with their specifications."""
        models = []
        for name, info in JIMENG_MODELS.items():
            models.append({
                "req_key": info.req_key,
                "name": info.name,
                "description": info.description,
                "type": info.type,
                "resolutions": info.resolutions,
                "durations": info.durations,
                "aspect_ratios": info.aspect_ratios,
            })
        return models
