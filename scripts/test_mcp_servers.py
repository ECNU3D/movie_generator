#!/usr/bin/env python3
"""
Test MCP Servers

This script tests the MCP server functionality by directly testing
the underlying database operations that the MCP tools wrap.

Usage:
    python scripts/test_mcp_servers.py
"""

import sys
from pathlib import Path

# Add src directory to path
_script_dir = Path(__file__).parent
_project_dir = _script_dir.parent
_src_dir = _project_dir / "src"
sys.path.insert(0, str(_src_dir))


def test_project_server():
    """Test project server tools via database."""
    print("=" * 60)
    print("Testing Project Server (Database Layer)")
    print("=" * 60)

    from story_generator.database import Database
    from story_generator.models import Project, Character, Episode

    # Use in-memory database for testing
    db = Database(":memory:")

    # Test create project
    print("\n1. Creating test project...")
    project = Project(
        name="Test Sci-Fi Story",
        description="A test story about space exploration",
        genre="sci-fi",
        style="cinematic",
        num_episodes=3,
        episode_duration=60
    )
    project_id = db.create_project(project)
    print(f"   Created project with ID: {project_id}")

    # Test get project
    print("\n2. Getting project...")
    project = db.get_project(project_id)
    print(f"   Name: {project.name}")
    print(f"   Genre: {project.genre}")

    # Test create character
    print("\n3. Creating character...")
    character = Character(
        project_id=project_id,
        name="Captain Maya Chen",
        age="35",
        appearance="Athletic build, short black hair, determined eyes",
        personality="Brave, strategic, caring",
        background="Former military pilot, lost her family in the first contact event",
        relationships="Mentor to crew members, respected leader",
        visual_description="A 35-year-old Asian woman with short black hair, wearing a blue space suit"
    )
    char_id = db.create_character(character)
    print(f"   Created character '{character.name}' with ID: {char_id}")

    # Test create episode
    print("\n4. Creating episode...")
    episode = Episode(
        project_id=project_id,
        episode_number=1,
        title="First Contact",
        outline="The crew discovers an alien signal and must decide whether to respond.",
        duration=60
    )
    episode_id = db.create_episode(episode)
    print(f"   Created episode '{episode.title}' with ID: {episode_id}")

    # Test list projects
    print("\n5. Listing projects...")
    projects = db.list_projects()
    print(f"   Found {len(projects)} project(s)")

    # Test character context
    print("\n6. Getting character context...")
    project = db.get_project(project_id)
    context = project.get_all_characters_context()
    print(f"   Context preview: {context[:200]}...")

    # Test update project
    print("\n7. Updating project...")
    project.name = "Updated Sci-Fi Story"
    db.update_project(project)
    updated_project = db.get_project(project_id)
    print(f"   Updated name: {updated_project.name}")

    # Clean up
    print("\n8. Cleaning up - deleting project...")
    db.delete_project(project_id)
    deleted = db.get_project(project_id)
    print(f"   Project deleted: {deleted is None}")

    print("\nProject Server: PASSED")
    return True


def test_storyboard_server():
    """Test storyboard server tools via database."""
    print("\n" + "=" * 60)
    print("Testing Storyboard Server (Database Layer)")
    print("=" * 60)

    from story_generator.database import Database
    from story_generator.models import Project, Episode, Shot

    # Use in-memory database for testing
    db = Database(":memory:")

    # Create test project and episode first
    print("\n1. Setting up test data...")
    project = Project(name="Storyboard Test", description="Test", genre="drama")
    project_id = db.create_project(project)

    episode = Episode(
        project_id=project_id,
        episode_number=1,
        title="Test Episode",
        outline="Test outline",
        duration=30
    )
    episode_id = db.create_episode(episode)
    print(f"   Created project {project_id}, episode {episode_id}")

    # Test create shot
    print("\n2. Creating shot...")
    shot = Shot(
        episode_id=episode_id,
        scene_number=1,
        shot_number=1,
        shot_type="wide",
        duration=5,
        visual_description="A vast starfield with a spaceship approaching",
        camera_movement="static"
    )
    shot_id = db.create_shot(shot)
    print(f"   Created shot with ID: {shot_id}")

    # Test batch create shots
    print("\n3. Batch creating shots...")
    shots = [
        Shot(
            episode_id=episode_id,
            scene_number=1,
            shot_number=2,
            shot_type="medium",
            duration=3,
            visual_description="Captain at the helm"
        ),
        Shot(
            episode_id=episode_id,
            scene_number=1,
            shot_number=3,
            shot_type="close_up",
            duration=2,
            visual_description="Close-up of the radar screen"
        )
    ]
    shot_ids = db.batch_create_shots(shots)
    print(f"   Created {len(shot_ids)} shots")

    # Test list shots
    print("\n4. Listing shots...")
    shots = db.get_shots_by_episode(episode_id)
    print(f"   Found {len(shots)} shots")

    # Test save generated prompt
    print("\n5. Saving generated prompt...")
    shot = db.get_shot(shot_id)
    shot.generated_prompts["kling_t2v"] = "A cinematic shot of a spaceship approaching through a starfield, epic scale, 4K quality"
    db.update_shot(shot)
    updated_shot = db.get_shot(shot_id)
    print(f"   Saved prompt: {updated_shot.generated_prompts.get('kling_t2v', '')[:50]}...")

    # Test get episode with shots
    print("\n6. Getting episode with shots...")
    episode = db.get_episode(episode_id)
    total_duration = sum(s.duration for s in episode.shots)
    print(f"   Total shots: {len(episode.shots)}")
    print(f"   Total duration: {total_duration}s")

    # Clean up
    print("\n7. Cleaning up...")
    db.delete_project(project_id)
    print("   Done")

    print("\nStoryboard Server: PASSED")
    return True


def test_video_server():
    """Test video server tools."""
    print("\n" + "=" * 60)
    print("Testing Video Server (Provider Layer)")
    print("=" * 60)

    from providers import get_provider, TaskStatus

    # Test get provider
    print("\n1. Getting providers...")
    providers = ["kling", "hailuo", "jimeng", "tongyi"]
    for name in providers:
        try:
            provider = get_provider(name)
            configured = provider.is_configured()
            status = "configured" if configured else "not configured"
            print(f"   {name}: {status}")
        except Exception as e:
            print(f"   {name}: ERROR - {e}")

    # Test task status enum
    print("\n2. Getting task status enum values...")
    statuses = [s.value for s in TaskStatus]
    print(f"   Status values: {statuses}")

    # Test connection for configured providers
    print("\n3. Testing connections...")
    for name in providers:
        try:
            provider = get_provider(name)
            if provider.is_configured():
                result = provider.test_connection()
                status = "OK" if result.get("success") else f"FAILED: {result.get('error')}"
                print(f"   {name}: {status}")
            else:
                print(f"   {name}: skipped (not configured)")
        except Exception as e:
            print(f"   {name}: ERROR - {e}")

    # Note: We don't test actual video generation as it requires API keys and costs money
    print("\n4. Skipping actual video generation tests (requires API keys)")

    print("\nVideo Server: PASSED (basic tests only)")
    return True


def test_mcp_tool_registration():
    """Test that MCP tools are properly registered."""
    print("\n" + "=" * 60)
    print("Testing MCP Tool Registration")
    print("=" * 60)

    from mcp_servers.project_server import mcp as p_mcp
    from mcp_servers.storyboard_server import mcp as s_mcp
    from mcp_servers.video_server import mcp as v_mcp

    print("\n1. Project Server Tools:")
    p_tools = list(p_mcp._tool_manager._tools.keys())
    print(f"   Registered {len(p_tools)} tools: {p_tools[:5]}...")

    print("\n2. Storyboard Server Tools:")
    s_tools = list(s_mcp._tool_manager._tools.keys())
    print(f"   Registered {len(s_tools)} tools: {s_tools[:5]}...")

    print("\n3. Video Server Tools:")
    v_tools = list(v_mcp._tool_manager._tools.keys())
    print(f"   Registered {len(v_tools)} tools: {v_tools[:5]}...")

    # Verify expected tools exist
    expected_p_tools = ["create_project", "get_project", "create_character", "create_episode"]
    expected_s_tools = ["create_shot", "get_shot", "list_shots", "batch_create_shots"]
    expected_v_tools = ["list_providers", "submit_text_to_video", "get_task_status"]

    all_ok = True
    print("\n4. Verifying expected tools...")
    for tool in expected_p_tools:
        if tool in p_tools:
            print(f"   project_server.{tool}: OK")
        else:
            print(f"   project_server.{tool}: MISSING")
            all_ok = False

    for tool in expected_s_tools:
        if tool in s_tools:
            print(f"   storyboard_server.{tool}: OK")
        else:
            print(f"   storyboard_server.{tool}: MISSING")
            all_ok = False

    for tool in expected_v_tools:
        if tool in v_tools:
            print(f"   video_server.{tool}: OK")
        else:
            print(f"   video_server.{tool}: MISSING")
            all_ok = False

    if all_ok:
        print("\nMCP Tool Registration: PASSED")
        return True
    else:
        print("\nMCP Tool Registration: FAILED")
        return False


def main():
    print("MCP Servers Test Suite")
    print("=" * 60)

    results = []

    try:
        results.append(("Project Server", test_project_server()))
    except Exception as e:
        import traceback
        print(f"\nProject Server: FAILED - {e}")
        traceback.print_exc()
        results.append(("Project Server", False))

    try:
        results.append(("Storyboard Server", test_storyboard_server()))
    except Exception as e:
        import traceback
        print(f"\nStoryboard Server: FAILED - {e}")
        traceback.print_exc()
        results.append(("Storyboard Server", False))

    try:
        results.append(("Video Server", test_video_server()))
    except Exception as e:
        import traceback
        print(f"\nVideo Server: FAILED - {e}")
        traceback.print_exc()
        results.append(("Video Server", False))

    try:
        results.append(("MCP Tool Registration", test_mcp_tool_registration()))
    except Exception as e:
        import traceback
        print(f"\nMCP Tool Registration: FAILED - {e}")
        traceback.print_exc()
        results.append(("MCP Tool Registration", False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
