"""
Base classes for video generation providers.

All provider implementations should inherit from VideoProvider
and implement the required abstract methods.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from .config import get_config, ProviderConfig


class TaskStatus(Enum):
    """Video generation task status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class VideoTask:
    """Represents a video generation task."""
    task_id: str
    provider: str
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)

    def is_completed(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)

    def is_successful(self) -> bool:
        """Check if task completed successfully."""
        return self.status == TaskStatus.COMPLETED and self.video_url is not None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "provider": self.provider,
            "status": self.status.value,
            "progress": self.progress,
            "video_url": self.video_url,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }


class VideoProvider(ABC):
    """
    Abstract base class for video generation providers.

    All providers must implement:
    - submit_text_to_video: Submit a text-to-video generation task
    - submit_image_to_video: Submit an image-to-video generation task
    - get_task_status: Query the status of a task
    """

    def __init__(self):
        self._config: Optional[ProviderConfig] = None
        self._name: str = ""

    @property
    def name(self) -> str:
        """Provider name."""
        return self._name

    @property
    def config(self) -> ProviderConfig:
        """Provider configuration."""
        if self._config is None:
            raise RuntimeError("Provider not initialized. Call initialize() first.")
        return self._config

    def initialize(self, config: Optional[ProviderConfig] = None):
        """Initialize the provider with configuration."""
        if config is not None:
            self._config = config
        else:
            self._config = get_config().get_provider_config(self._name)

    def is_configured(self) -> bool:
        """Check if provider has valid credentials."""
        return get_config().is_provider_configured(self._name)

    @abstractmethod
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
            prompt: Text description for video generation
            duration: Video duration in seconds
            resolution: Video resolution (e.g., "1080p", "720p")
            **kwargs: Provider-specific parameters

        Returns:
            VideoTask with task_id and initial status
        """
        pass

    @abstractmethod
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
            prompt: Text description for motion/action
            duration: Video duration in seconds
            resolution: Video resolution
            **kwargs: Provider-specific parameters

        Returns:
            VideoTask with task_id and initial status
        """
        pass

    @abstractmethod
    def get_task_status(self, task_id: str) -> VideoTask:
        """
        Query the status of a video generation task.

        Args:
            task_id: The task ID returned from submit methods

        Returns:
            VideoTask with current status and video_url if completed
        """
        pass

    def wait_for_completion(
        self,
        task_id: str,
        timeout: Optional[int] = None,
        poll_interval: int = 5
    ) -> VideoTask:
        """
        Wait for a task to complete.

        Args:
            task_id: The task ID to wait for
            timeout: Maximum time to wait in seconds (default from config)
            poll_interval: Time between status checks in seconds

        Returns:
            VideoTask with final status

        Raises:
            TimeoutError: If task doesn't complete within timeout
        """
        if timeout is None:
            timeout = get_config().global_config.timeout

        start_time = time.time()
        while time.time() - start_time < timeout:
            task = self.get_task_status(task_id)

            if task.is_completed():
                return task

            time.sleep(poll_interval)

        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")

    def text_to_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        wait: bool = True,
        **kwargs
    ) -> VideoTask:
        """
        Generate a video from text prompt.

        This is a convenience method that submits the task and optionally
        waits for completion.

        Args:
            prompt: Text description for video generation
            duration: Video duration in seconds
            resolution: Video resolution
            wait: If True, wait for task completion
            **kwargs: Provider-specific parameters

        Returns:
            VideoTask with final status (if wait=True) or initial status
        """
        task = self.submit_text_to_video(prompt, duration, resolution, **kwargs)

        if wait:
            return self.wait_for_completion(task.task_id)

        return task

    def image_to_video(
        self,
        image_url: str,
        prompt: str,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        wait: bool = True,
        **kwargs
    ) -> VideoTask:
        """
        Generate a video from reference image.

        This is a convenience method that submits the task and optionally
        waits for completion.

        Args:
            image_url: URL of the reference image
            prompt: Text description for motion/action
            duration: Video duration in seconds
            resolution: Video resolution
            wait: If True, wait for task completion
            **kwargs: Provider-specific parameters

        Returns:
            VideoTask with final status (if wait=True) or initial status
        """
        task = self.submit_image_to_video(image_url, prompt, duration, resolution, **kwargs)

        if wait:
            return self.wait_for_completion(task.task_id)

        return task

    def test_connection(self) -> dict:
        """
        Test the connection to the provider.

        Returns:
            dict with "success" boolean and optional "error" message
        """
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "Provider not configured. Please set API keys.",
                }
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
