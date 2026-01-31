"""
Project MCP Server

Provides MCP tools for project, character, and episode CRUD operations.
Wraps the existing database.py functionality.

Usage:
    python -m mcp_servers.project_server
    # or
    python src/mcp_servers/project_server.py
"""

import sys
from pathlib import Path
from typing import Optional, List

# Add parent directories to path for imports
_current_dir = Path(__file__).parent
_src_dir = _current_dir.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from fastmcp import FastMCP

from story_generator.database import Database
from story_generator.models import Project, Character, Episode

# Initialize MCP server and database
mcp = FastMCP("Project Server")
db = Database()


# ==================== Project Tools ====================

@mcp.tool()
def create_project(
    name: str,
    description: str,
    genre: str = "drama",
    style: str = "",
    num_episodes: int = 1,
    episode_duration: int = 60,
    max_video_duration: int = 10,
    target_audience: str = ""
) -> dict:
    """
    Create a new story project.

    Args:
        name: Project name/title
        description: Story concept/description
        genre: Story genre (romance, action, sci-fi, fantasy, comedy, drama, horror, thriller, documentary, animation, other)
        style: Visual/narrative style description
        num_episodes: Number of episodes
        episode_duration: Duration per episode in seconds
        max_video_duration: Maximum video clip duration in seconds (for calculating min shots)
        target_audience: Target audience description

    Returns:
        dict with project_id and name
    """
    project = Project(
        name=name,
        description=description,
        genre=genre,
        style=style,
        target_audience=target_audience,
        num_episodes=num_episodes,
        episode_duration=episode_duration,
        max_video_duration=max_video_duration
    )
    project_id = db.create_project(project)
    return {"project_id": project_id, "name": name}


@mcp.tool()
def get_project(project_id: int) -> dict:
    """
    Get project details including characters and episodes.

    Args:
        project_id: The project ID

    Returns:
        Project data as dict, or error dict if not found
    """
    project = db.get_project(project_id)
    if not project:
        return {"error": "Project not found", "project_id": project_id}
    return project.to_dict()


@mcp.tool()
def update_project(
    project_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    genre: Optional[str] = None,
    style: Optional[str] = None,
    target_audience: Optional[str] = None,
    num_episodes: Optional[int] = None,
    episode_duration: Optional[int] = None,
    max_video_duration: Optional[int] = None
) -> dict:
    """
    Update project information.

    Args:
        project_id: The project ID to update
        name: New project name (optional)
        description: New description (optional)
        genre: New genre (optional)
        style: New style (optional)
        target_audience: New target audience (optional)
        num_episodes: New episode count (optional)
        episode_duration: New episode duration (optional)
        max_video_duration: New max video duration (optional)

    Returns:
        Success status dict
    """
    project = db.get_project(project_id)
    if not project:
        return {"error": "Project not found", "project_id": project_id}

    # Update only provided fields
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    if genre is not None:
        project.genre = genre
    if style is not None:
        project.style = style
    if target_audience is not None:
        project.target_audience = target_audience
    if num_episodes is not None:
        project.num_episodes = num_episodes
    if episode_duration is not None:
        project.episode_duration = episode_duration
    if max_video_duration is not None:
        project.max_video_duration = max_video_duration

    db.update_project(project)
    return {"success": True, "project_id": project_id}


@mcp.tool()
def delete_project(project_id: int) -> dict:
    """
    Delete a project and all its associated data (characters, episodes, shots).

    Args:
        project_id: The project ID to delete

    Returns:
        Success status dict
    """
    project = db.get_project(project_id)
    if not project:
        return {"error": "Project not found", "project_id": project_id}

    db.delete_project(project_id)
    return {"success": True, "project_id": project_id}


@mcp.tool()
def list_projects() -> list:
    """
    List all projects (basic info only, without characters and episodes).

    Returns:
        List of project dicts with basic info
    """
    projects = db.list_projects()
    return [
        {
            "id": p.id,
            "name": p.name,
            "genre": p.genre,
            "num_episodes": p.num_episodes,
            "created_at": p.created_at.isoformat(),
            "updated_at": p.updated_at.isoformat(),
        }
        for p in projects
    ]


# ==================== Character Tools ====================

@mcp.tool()
def create_character(
    project_id: int,
    name: str,
    age: str = "",
    appearance: str = "",
    personality: str = "",
    background: str = "",
    relationships: str = "",
    visual_description: str = ""
) -> dict:
    """
    Create a new character for a project.

    Args:
        project_id: The project ID
        name: Character name
        age: Age (can be specific or descriptive like "middle-aged")
        appearance: Physical appearance description
        personality: Personality traits
        background: Character backstory
        relationships: Relationships with other characters
        visual_description: Visual description for consistent image/video generation

    Returns:
        dict with character_id and name
    """
    # Verify project exists
    project = db.get_project(project_id)
    if not project:
        return {"error": "Project not found", "project_id": project_id}

    character = Character(
        project_id=project_id,
        name=name,
        age=age,
        appearance=appearance,
        personality=personality,
        background=background,
        relationships=relationships,
        visual_description=visual_description
    )
    char_id = db.create_character(character)
    return {"character_id": char_id, "name": name}


@mcp.tool()
def get_character(character_id: int) -> dict:
    """
    Get character details.

    Args:
        character_id: The character ID

    Returns:
        Character data as dict, or error dict if not found
    """
    character = db.get_character(character_id)
    if not character:
        return {"error": "Character not found", "character_id": character_id}
    return character.to_dict()


@mcp.tool()
def update_character(
    character_id: int,
    name: Optional[str] = None,
    age: Optional[str] = None,
    appearance: Optional[str] = None,
    personality: Optional[str] = None,
    background: Optional[str] = None,
    relationships: Optional[str] = None,
    visual_description: Optional[str] = None
) -> dict:
    """
    Update character information.

    Args:
        character_id: The character ID to update
        name: New name (optional)
        age: New age (optional)
        appearance: New appearance (optional)
        personality: New personality (optional)
        background: New background (optional)
        relationships: New relationships (optional)
        visual_description: New visual description (optional)

    Returns:
        Success status dict
    """
    character = db.get_character(character_id)
    if not character:
        return {"error": "Character not found", "character_id": character_id}

    if name is not None:
        character.name = name
    if age is not None:
        character.age = age
    if appearance is not None:
        character.appearance = appearance
    if personality is not None:
        character.personality = personality
    if background is not None:
        character.background = background
    if relationships is not None:
        character.relationships = relationships
    if visual_description is not None:
        character.visual_description = visual_description

    db.update_character(character)
    return {"success": True, "character_id": character_id}


@mcp.tool()
def delete_character(character_id: int) -> dict:
    """
    Delete a character.

    Args:
        character_id: The character ID to delete

    Returns:
        Success status dict
    """
    character = db.get_character(character_id)
    if not character:
        return {"error": "Character not found", "character_id": character_id}

    db.delete_character(character_id)
    return {"success": True, "character_id": character_id}


@mcp.tool()
def add_character_event(
    character_id: int,
    episode_number: int,
    description: str,
    impact: str
) -> dict:
    """
    Add a major event to a character's history.

    Args:
        character_id: The character ID
        episode_number: Episode number where the event occurs
        description: Description of the event
        impact: Impact on the character

    Returns:
        Success status dict
    """
    character = db.get_character(character_id)
    if not character:
        return {"error": "Character not found", "character_id": character_id}

    character.add_major_event(episode_number, description, impact)
    db.update_character(character)
    return {"success": True, "character_id": character_id}


@mcp.tool()
def get_character_context(
    project_id: int,
    up_to_episode: Optional[int] = None
) -> str:
    """
    Get character knowledge context for maintaining story consistency.

    Args:
        project_id: The project ID
        up_to_episode: Only include events up to this episode (to avoid spoilers)

    Returns:
        Character context string for LLM prompts
    """
    project = db.get_project(project_id)
    if not project:
        return ""
    return project.get_all_characters_context(up_to_episode)


@mcp.tool()
def list_characters(project_id: int) -> list:
    """
    List all characters for a project.

    Args:
        project_id: The project ID

    Returns:
        List of character dicts
    """
    characters = db.get_characters_by_project(project_id)
    return [c.to_dict() for c in characters]


# ==================== Episode Tools ====================

@mcp.tool()
def create_episode(
    project_id: int,
    episode_number: int,
    title: str,
    outline: str,
    duration: int = 60
) -> dict:
    """
    Create a new episode for a project.

    Args:
        project_id: The project ID
        episode_number: Episode number (1-indexed)
        title: Episode title
        outline: Episode outline/summary
        duration: Target duration in seconds

    Returns:
        dict with episode_id and title
    """
    # Verify project exists
    project = db.get_project(project_id)
    if not project:
        return {"error": "Project not found", "project_id": project_id}

    episode = Episode(
        project_id=project_id,
        episode_number=episode_number,
        title=title,
        outline=outline,
        duration=duration
    )
    ep_id = db.create_episode(episode)
    return {"episode_id": ep_id, "title": title}


@mcp.tool()
def get_episode(episode_id: int) -> dict:
    """
    Get episode details including shots.

    Args:
        episode_id: The episode ID

    Returns:
        Episode data as dict, or error dict if not found
    """
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found", "episode_id": episode_id}
    return episode.to_dict()


@mcp.tool()
def update_episode(
    episode_id: int,
    episode_number: Optional[int] = None,
    title: Optional[str] = None,
    outline: Optional[str] = None,
    duration: Optional[int] = None,
    status: Optional[str] = None
) -> dict:
    """
    Update episode information.

    Args:
        episode_id: The episode ID to update
        episode_number: New episode number (optional)
        title: New title (optional)
        outline: New outline (optional)
        duration: New duration (optional)
        status: New status: outline, in_progress, completed (optional)

    Returns:
        Success status dict
    """
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found", "episode_id": episode_id}

    if episode_number is not None:
        episode.episode_number = episode_number
    if title is not None:
        episode.title = title
    if outline is not None:
        episode.outline = outline
    if duration is not None:
        episode.duration = duration
    if status is not None:
        episode.status = status

    db.update_episode(episode)
    return {"success": True, "episode_id": episode_id}


@mcp.tool()
def delete_episode(episode_id: int) -> dict:
    """
    Delete an episode and all its shots.

    Args:
        episode_id: The episode ID to delete

    Returns:
        Success status dict
    """
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found", "episode_id": episode_id}

    db.delete_episode(episode_id)
    return {"success": True, "episode_id": episode_id}


@mcp.tool()
def list_episodes(project_id: int) -> list:
    """
    List all episodes for a project.

    Args:
        project_id: The project ID

    Returns:
        List of episode dicts (without shots for brevity)
    """
    episodes = db.get_episodes_by_project(project_id)
    return [
        {
            "id": e.id,
            "episode_number": e.episode_number,
            "title": e.title,
            "outline": e.outline,
            "duration": e.duration,
            "status": e.status,
            "shot_count": len(e.shots),
            "total_duration": e.get_total_duration(),
        }
        for e in episodes
    ]


# ==================== Resources ====================

@mcp.resource("project://{project_id}")
def get_project_resource(project_id: int) -> dict:
    """Get full project data as a resource."""
    return get_project(project_id)


@mcp.resource("project://{project_id}/characters")
def get_project_characters_resource(project_id: int) -> list:
    """Get all characters for a project as a resource."""
    return list_characters(project_id)


@mcp.resource("project://{project_id}/episodes")
def get_project_episodes_resource(project_id: int) -> list:
    """Get all episodes for a project as a resource."""
    return list_episodes(project_id)


@mcp.resource("character://{character_id}")
def get_character_resource(character_id: int) -> dict:
    """Get character data as a resource."""
    return get_character(character_id)


@mcp.resource("episode://{episode_id}")
def get_episode_resource(episode_id: int) -> dict:
    """Get episode data as a resource."""
    return get_episode(episode_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
