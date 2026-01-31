"""
Storyboard MCP Server

Provides MCP tools for shot/storyboard CRUD operations.
Wraps the existing database.py functionality.

Usage:
    python -m mcp_servers.storyboard_server
    # or
    python src/mcp_servers/storyboard_server.py
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict

# Add parent directories to path for imports
_current_dir = Path(__file__).parent
_src_dir = _current_dir.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from fastmcp import FastMCP

from story_generator.database import Database
from story_generator.models import Shot, SHOT_TYPE_NAMES, CAMERA_MOVEMENT_NAMES

# Initialize MCP server and database
mcp = FastMCP("Storyboard Server")
db = Database()


# ==================== Shot Tools ====================

@mcp.tool()
def create_shot(
    episode_id: int,
    scene_number: int,
    shot_number: int,
    shot_type: str = "medium",
    duration: int = 5,
    visual_description: str = "",
    dialogue: str = "",
    sound_music: str = "",
    camera_movement: str = "static",
    notes: str = ""
) -> dict:
    """
    Create a new shot for an episode.

    Args:
        episode_id: The episode ID
        scene_number: Scene number (1-indexed)
        shot_number: Shot number within scene (1-indexed)
        shot_type: Shot type (extreme_wide, wide, full, medium, medium_close, close_up, extreme_close_up, pov, over_shoulder, two_shot)
        duration: Shot duration in seconds
        visual_description: Visual/scene description
        dialogue: Character dialogue
        sound_music: Sound effects/music description
        camera_movement: Camera movement (static, pan_left, pan_right, tilt_up, tilt_down, zoom_in, zoom_out, dolly_in, dolly_out, tracking, crane_up, crane_down, handheld)
        notes: Additional notes

    Returns:
        dict with shot_id
    """
    # Verify episode exists
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found", "episode_id": episode_id}

    shot = Shot(
        episode_id=episode_id,
        scene_number=scene_number,
        shot_number=shot_number,
        shot_type=shot_type,
        duration=duration,
        visual_description=visual_description,
        dialogue=dialogue,
        sound_music=sound_music,
        camera_movement=camera_movement,
        notes=notes
    )
    shot_id = db.create_shot(shot)
    return {"shot_id": shot_id, "scene_number": scene_number, "shot_number": shot_number}


@mcp.tool()
def get_shot(shot_id: int) -> dict:
    """
    Get shot details.

    Args:
        shot_id: The shot ID

    Returns:
        Shot data as dict, or error dict if not found
    """
    shot = db.get_shot(shot_id)
    if not shot:
        return {"error": "Shot not found", "shot_id": shot_id}
    return shot.to_dict()


@mcp.tool()
def update_shot(
    shot_id: int,
    scene_number: Optional[int] = None,
    shot_number: Optional[int] = None,
    shot_type: Optional[str] = None,
    duration: Optional[int] = None,
    visual_description: Optional[str] = None,
    dialogue: Optional[str] = None,
    sound_music: Optional[str] = None,
    camera_movement: Optional[str] = None,
    notes: Optional[str] = None
) -> dict:
    """
    Update shot information.

    Args:
        shot_id: The shot ID to update
        scene_number: New scene number (optional)
        shot_number: New shot number (optional)
        shot_type: New shot type (optional)
        duration: New duration (optional)
        visual_description: New visual description (optional)
        dialogue: New dialogue (optional)
        sound_music: New sound/music (optional)
        camera_movement: New camera movement (optional)
        notes: New notes (optional)

    Returns:
        Success status dict
    """
    shot = db.get_shot(shot_id)
    if not shot:
        return {"error": "Shot not found", "shot_id": shot_id}

    if scene_number is not None:
        shot.scene_number = scene_number
    if shot_number is not None:
        shot.shot_number = shot_number
    if shot_type is not None:
        shot.shot_type = shot_type
    if duration is not None:
        shot.duration = duration
    if visual_description is not None:
        shot.visual_description = visual_description
    if dialogue is not None:
        shot.dialogue = dialogue
    if sound_music is not None:
        shot.sound_music = sound_music
    if camera_movement is not None:
        shot.camera_movement = camera_movement
    if notes is not None:
        shot.notes = notes

    db.update_shot(shot)
    return {"success": True, "shot_id": shot_id}


@mcp.tool()
def delete_shot(shot_id: int) -> dict:
    """
    Delete a shot.

    Args:
        shot_id: The shot ID to delete

    Returns:
        Success status dict
    """
    shot = db.get_shot(shot_id)
    if not shot:
        return {"error": "Shot not found", "shot_id": shot_id}

    db.delete_shot(shot_id)
    return {"success": True, "shot_id": shot_id}


@mcp.tool()
def list_shots(episode_id: int) -> list:
    """
    List all shots for an episode, ordered by scene and shot number.

    Args:
        episode_id: The episode ID

    Returns:
        List of shot dicts
    """
    shots = db.get_shots_by_episode(episode_id)
    return [s.to_dict() for s in shots]


@mcp.tool()
def batch_create_shots(episode_id: int, shots_data: List[dict]) -> dict:
    """
    Create multiple shots at once.

    Args:
        episode_id: The episode ID
        shots_data: List of shot data dicts, each containing:
            - scene_number: int
            - shot_number: int
            - shot_type: str (optional, default "medium")
            - duration: int (optional, default 5)
            - visual_description: str
            - dialogue: str (optional)
            - sound_music: str (optional)
            - camera_movement: str (optional, default "static")
            - notes: str (optional)

    Returns:
        dict with list of created shot_ids
    """
    # Verify episode exists
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found", "episode_id": episode_id}

    shots = []
    for data in shots_data:
        shot = Shot(
            episode_id=episode_id,
            scene_number=data.get("scene_number", 1),
            shot_number=data.get("shot_number", 1),
            shot_type=data.get("shot_type", "medium"),
            duration=data.get("duration", 5),
            visual_description=data.get("visual_description", ""),
            dialogue=data.get("dialogue", ""),
            sound_music=data.get("sound_music", ""),
            camera_movement=data.get("camera_movement", "static"),
            notes=data.get("notes", "")
        )
        shots.append(shot)

    shot_ids = db.batch_create_shots(shots)
    return {"success": True, "shot_ids": shot_ids, "count": len(shot_ids)}


@mcp.tool()
def delete_all_shots(episode_id: int) -> dict:
    """
    Delete all shots for an episode (useful before regenerating storyboard).

    Args:
        episode_id: The episode ID

    Returns:
        Success status dict
    """
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found", "episode_id": episode_id}

    db.delete_shots_by_episode(episode_id)
    return {"success": True, "episode_id": episode_id}


@mcp.tool()
def save_generated_prompt(
    shot_id: int,
    platform: str,
    prompt_type: str,
    prompt: str
) -> dict:
    """
    Save a generated video prompt for a shot.

    Args:
        shot_id: The shot ID
        platform: Platform name (kling, hailuo, jimeng, tongyi)
        prompt_type: Prompt type (t2v, i2v, i2v_fl)
        prompt: The generated prompt text

    Returns:
        Success status dict
    """
    shot = db.get_shot(shot_id)
    if not shot:
        return {"error": "Shot not found", "shot_id": shot_id}

    key = f"{platform}_{prompt_type}"
    shot.generated_prompts[key] = prompt
    db.update_shot(shot)
    return {"success": True, "shot_id": shot_id, "prompt_key": key}


@mcp.tool()
def get_generated_prompt(
    shot_id: int,
    platform: str,
    prompt_type: str
) -> dict:
    """
    Get a generated video prompt for a shot.

    Args:
        shot_id: The shot ID
        platform: Platform name (kling, hailuo, jimeng, tongyi)
        prompt_type: Prompt type (t2v, i2v, i2v_fl)

    Returns:
        dict with prompt or null if not found
    """
    shot = db.get_shot(shot_id)
    if not shot:
        return {"error": "Shot not found", "shot_id": shot_id}

    key = f"{platform}_{prompt_type}"
    prompt = shot.generated_prompts.get(key)
    return {"shot_id": shot_id, "prompt_key": key, "prompt": prompt}


@mcp.tool()
def get_storyboard_summary(episode_id: int) -> dict:
    """
    Get a summary of the storyboard for an episode.

    Args:
        episode_id: The episode ID

    Returns:
        Summary dict with shot count, total duration, scenes breakdown
    """
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found", "episode_id": episode_id}

    shots = episode.shots
    total_duration = sum(s.duration for s in shots)

    # Group by scene
    scenes = {}
    for shot in shots:
        scene_num = shot.scene_number
        if scene_num not in scenes:
            scenes[scene_num] = {"shot_count": 0, "duration": 0, "shots": []}
        scenes[scene_num]["shot_count"] += 1
        scenes[scene_num]["duration"] += shot.duration
        scenes[scene_num]["shots"].append({
            "shot_number": shot.shot_number,
            "shot_type": shot.shot_type,
            "duration": shot.duration,
        })

    return {
        "episode_id": episode_id,
        "episode_title": episode.title,
        "target_duration": episode.duration,
        "total_shot_count": len(shots),
        "total_duration": total_duration,
        "duration_diff": total_duration - episode.duration,
        "scene_count": len(scenes),
        "scenes": scenes
    }


@mcp.tool()
def get_shot_type_names() -> dict:
    """
    Get the mapping of shot type codes to Chinese names.

    Returns:
        dict mapping shot_type codes to Chinese names
    """
    return SHOT_TYPE_NAMES


@mcp.tool()
def get_camera_movement_names() -> dict:
    """
    Get the mapping of camera movement codes to Chinese names.

    Returns:
        dict mapping camera_movement codes to Chinese names
    """
    return CAMERA_MOVEMENT_NAMES


# ==================== Resources ====================

@mcp.resource("storyboard://{episode_id}")
def get_storyboard_resource(episode_id: int) -> dict:
    """Get full storyboard data for an episode as a resource."""
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found"}
    return {
        "episode": {
            "id": episode.id,
            "episode_number": episode.episode_number,
            "title": episode.title,
            "outline": episode.outline,
            "duration": episode.duration,
            "status": episode.status,
        },
        "shots": [s.to_dict() for s in episode.shots],
        "total_duration": episode.get_total_duration()
    }


@mcp.resource("shot://{shot_id}")
def get_shot_resource(shot_id: int) -> dict:
    """Get shot data as a resource."""
    return get_shot(shot_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
