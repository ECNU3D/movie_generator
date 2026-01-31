"""
Video MCP Server

Provides MCP tools for video generation via multiple providers.
Wraps the existing providers/* functionality (Kling, Hailuo, Jimeng, Tongyi).

Usage:
    python -m mcp_servers.video_server
    # or
    python src/mcp_servers/video_server.py
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directories to path for imports
_current_dir = Path(__file__).parent
_src_dir = _current_dir.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from fastmcp import FastMCP

from providers import (
    KlingProvider,
    HailuoProvider,
    JimengProvider,
    TongyiProvider,
    TaskStatus,
    get_provider,
)

# Initialize MCP server
mcp = FastMCP("Video Server")

# Initialize providers (lazy loading - actual API calls happen when tools are used)
_providers: Dict[str, Any] = {}


def _get_provider(name: str):
    """Get or initialize a provider by name."""
    if name not in _providers:
        _providers[name] = get_provider(name)
    return _providers[name]


def _get_all_provider_names() -> List[str]:
    """Get list of all available provider names."""
    return ["kling", "hailuo", "jimeng", "tongyi"]


# ==================== Query Tools ====================

@mcp.tool()
def list_providers() -> list:
    """
    List all available video generation providers and their configuration status.

    Returns:
        List of provider info dicts with name, configured status
    """
    result = []
    for name in _get_all_provider_names():
        provider = _get_provider(name)
        result.append({
            "name": name,
            "configured": provider.is_configured(),
        })
    return result


@mcp.tool()
def get_provider_status(provider_name: str) -> dict:
    """
    Get detailed status of a specific provider.

    Args:
        provider_name: Provider name (kling, hailuo, jimeng, tongyi)

    Returns:
        Provider status dict with configuration and connection test result
    """
    if provider_name not in _get_all_provider_names():
        return {"error": f"Unknown provider: {provider_name}"}

    provider = _get_provider(provider_name)
    test_result = provider.test_connection()

    return {
        "name": provider_name,
        "configured": provider.is_configured(),
        "connection_test": test_result,
    }


# ==================== Text-to-Video Tools ====================

@mcp.tool()
def submit_text_to_video(
    provider_name: str,
    prompt: str,
    duration: int = 5,
    resolution: Optional[str] = None,
    model: Optional[str] = None,
    negative_prompt: Optional[str] = None,
    cfg_scale: Optional[float] = None,
) -> dict:
    """
    Submit a text-to-video generation task.

    Args:
        provider_name: Provider name (kling, hailuo, jimeng, tongyi)
        prompt: Text description for video generation
        duration: Video duration in seconds (provider-specific limits apply)
        resolution: Video resolution (e.g., "1080p", "720p", "16:9", "9:16")
        model: Specific model to use (provider-specific)
        negative_prompt: What to avoid in the video (not all providers support this)
        cfg_scale: Guidance scale (not all providers support this)

    Returns:
        dict with task_id and initial status, or error
    """
    if provider_name not in _get_all_provider_names():
        return {"error": f"Unknown provider: {provider_name}"}

    provider = _get_provider(provider_name)

    if not provider.is_configured():
        return {"error": f"Provider {provider_name} not configured. Please set API keys."}

    # Build kwargs for provider-specific parameters
    kwargs = {}
    if model:
        kwargs["model"] = model
    if negative_prompt:
        kwargs["negative_prompt"] = negative_prompt
    if cfg_scale:
        kwargs["cfg_scale"] = cfg_scale

    try:
        task = provider.submit_text_to_video(
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            **kwargs
        )
        return task.to_dict()
    except Exception as e:
        return {"error": str(e), "provider": provider_name}


@mcp.tool()
def text_to_video_sync(
    provider_name: str,
    prompt: str,
    duration: int = 5,
    resolution: Optional[str] = None,
    timeout: int = 300,
    model: Optional[str] = None,
) -> dict:
    """
    Generate a video from text and wait for completion (synchronous).

    Args:
        provider_name: Provider name (kling, hailuo, jimeng, tongyi)
        prompt: Text description for video generation
        duration: Video duration in seconds
        resolution: Video resolution
        timeout: Maximum time to wait in seconds
        model: Specific model to use

    Returns:
        dict with final task status and video_url if successful, or error
    """
    if provider_name not in _get_all_provider_names():
        return {"error": f"Unknown provider: {provider_name}"}

    provider = _get_provider(provider_name)

    if not provider.is_configured():
        return {"error": f"Provider {provider_name} not configured. Please set API keys."}

    kwargs = {}
    if model:
        kwargs["model"] = model

    try:
        task = provider.text_to_video(
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            wait=True,
            **kwargs
        )
        return task.to_dict()
    except TimeoutError as e:
        return {"error": f"Timeout: {e}", "provider": provider_name}
    except Exception as e:
        return {"error": str(e), "provider": provider_name}


# ==================== Image-to-Video Tools ====================

@mcp.tool()
def submit_image_to_video(
    provider_name: str,
    image_url: str,
    prompt: str,
    duration: int = 5,
    resolution: Optional[str] = None,
    end_frame_url: Optional[str] = None,
    model: Optional[str] = None,
) -> dict:
    """
    Submit an image-to-video generation task.

    Args:
        provider_name: Provider name (kling, hailuo, jimeng, tongyi)
        image_url: URL of the first frame / reference image
        prompt: Text description for motion/action
        duration: Video duration in seconds
        resolution: Video resolution
        end_frame_url: URL of the last frame (for first-last frame generation, supported by some providers)
        model: Specific model to use

    Returns:
        dict with task_id and initial status, or error
    """
    if provider_name not in _get_all_provider_names():
        return {"error": f"Unknown provider: {provider_name}"}

    provider = _get_provider(provider_name)

    if not provider.is_configured():
        return {"error": f"Provider {provider_name} not configured. Please set API keys."}

    kwargs = {}
    if end_frame_url:
        kwargs["end_frame_url"] = end_frame_url
    if model:
        kwargs["model"] = model

    try:
        task = provider.submit_image_to_video(
            image_url=image_url,
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            **kwargs
        )
        return task.to_dict()
    except Exception as e:
        return {"error": str(e), "provider": provider_name}


@mcp.tool()
def image_to_video_sync(
    provider_name: str,
    image_url: str,
    prompt: str,
    duration: int = 5,
    resolution: Optional[str] = None,
    timeout: int = 300,
    end_frame_url: Optional[str] = None,
    model: Optional[str] = None,
) -> dict:
    """
    Generate a video from image and wait for completion (synchronous).

    Args:
        provider_name: Provider name (kling, hailuo, jimeng, tongyi)
        image_url: URL of the first frame / reference image
        prompt: Text description for motion/action
        duration: Video duration in seconds
        resolution: Video resolution
        timeout: Maximum time to wait in seconds
        end_frame_url: URL of the last frame
        model: Specific model to use

    Returns:
        dict with final task status and video_url if successful, or error
    """
    if provider_name not in _get_all_provider_names():
        return {"error": f"Unknown provider: {provider_name}"}

    provider = _get_provider(provider_name)

    if not provider.is_configured():
        return {"error": f"Provider {provider_name} not configured. Please set API keys."}

    kwargs = {}
    if end_frame_url:
        kwargs["end_frame_url"] = end_frame_url
    if model:
        kwargs["model"] = model

    try:
        task = provider.image_to_video(
            image_url=image_url,
            prompt=prompt,
            duration=duration,
            resolution=resolution,
            wait=True,
            **kwargs
        )
        return task.to_dict()
    except TimeoutError as e:
        return {"error": f"Timeout: {e}", "provider": provider_name}
    except Exception as e:
        return {"error": str(e), "provider": provider_name}


# ==================== Task Status Tools ====================

@mcp.tool()
def get_task_status(provider_name: str, task_id: str) -> dict:
    """
    Query the status of a video generation task.

    Args:
        provider_name: Provider name (kling, hailuo, jimeng, tongyi)
        task_id: The task ID returned from submit methods

    Returns:
        dict with current task status
    """
    if provider_name not in _get_all_provider_names():
        return {"error": f"Unknown provider: {provider_name}"}

    provider = _get_provider(provider_name)

    try:
        task = provider.get_task_status(task_id)
        return task.to_dict()
    except Exception as e:
        return {"error": str(e), "provider": provider_name, "task_id": task_id}


@mcp.tool()
def wait_for_task(
    provider_name: str,
    task_id: str,
    timeout: int = 300,
    poll_interval: int = 5
) -> dict:
    """
    Wait for a video generation task to complete.

    Args:
        provider_name: Provider name (kling, hailuo, jimeng, tongyi)
        task_id: The task ID to wait for
        timeout: Maximum time to wait in seconds
        poll_interval: Time between status checks in seconds

    Returns:
        dict with final task status
    """
    if provider_name not in _get_all_provider_names():
        return {"error": f"Unknown provider: {provider_name}"}

    provider = _get_provider(provider_name)

    try:
        task = provider.wait_for_completion(task_id, timeout, poll_interval)
        return task.to_dict()
    except TimeoutError as e:
        return {"error": f"Timeout: {e}", "provider": provider_name, "task_id": task_id}
    except Exception as e:
        return {"error": str(e), "provider": provider_name, "task_id": task_id}


# ==================== Batch Tools ====================

@mcp.tool()
def batch_submit_text_to_video(
    provider_name: str,
    tasks: List[dict]
) -> dict:
    """
    Submit multiple text-to-video tasks at once.

    Args:
        provider_name: Provider name (kling, hailuo, jimeng, tongyi)
        tasks: List of task dicts, each containing:
            - prompt: str (required)
            - duration: int (optional, default 5)
            - resolution: str (optional)
            - model: str (optional)

    Returns:
        dict with list of submitted task results
    """
    if provider_name not in _get_all_provider_names():
        return {"error": f"Unknown provider: {provider_name}"}

    provider = _get_provider(provider_name)

    if not provider.is_configured():
        return {"error": f"Provider {provider_name} not configured. Please set API keys."}

    results = []
    for i, task_data in enumerate(tasks):
        prompt = task_data.get("prompt")
        if not prompt:
            results.append({"error": "Missing prompt", "index": i})
            continue

        kwargs = {}
        if task_data.get("model"):
            kwargs["model"] = task_data["model"]

        try:
            task = provider.submit_text_to_video(
                prompt=prompt,
                duration=task_data.get("duration", 5),
                resolution=task_data.get("resolution"),
                **kwargs
            )
            results.append({"index": i, **task.to_dict()})
        except Exception as e:
            results.append({"error": str(e), "index": i})

    return {"provider": provider_name, "results": results, "submitted": len([r for r in results if "task_id" in r])}


# ==================== Utility Tools ====================

@mcp.tool()
def get_task_status_enum_values() -> list:
    """
    Get all possible task status values.

    Returns:
        List of status strings
    """
    return [s.value for s in TaskStatus]


# ==================== Resources ====================

@mcp.resource("video_task://{provider_name}/{task_id}")
def get_video_task_resource(provider_name: str, task_id: str) -> dict:
    """Get video task status as a resource."""
    return get_task_status(provider_name, task_id)


@mcp.resource("providers://list")
def get_providers_list_resource() -> list:
    """Get list of all providers as a resource."""
    return list_providers()


if __name__ == "__main__":
    mcp.run(transport="stdio")
