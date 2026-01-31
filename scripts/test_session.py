#!/usr/bin/env python3
"""
Test Script for Session Management

Validates session persistence and recovery functionality.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def test_session_manager():
    """Test SessionManager basic operations."""
    print("\n=== Test 1: SessionManager Operations ===")

    try:
        from agents import SessionManager, SessionStatus, InteractionMode

        manager = SessionManager()
        print("✓ SessionManager created")

        # Create session
        session = manager.create_session(
            user_request="Test story about robots",
            mode=InteractionMode.INTERACTIVE,
        )
        print(f"✓ Session created: {session.session_id[:8]}...")

        # Get session
        retrieved = manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
        print("✓ Session retrieved")

        # Update session
        session.current_phase = "story_outline"
        session.status = SessionStatus.PAUSED
        manager.update_session(session)

        updated = manager.get_session(session.session_id)
        assert updated.current_phase == "story_outline"
        assert updated.status == SessionStatus.PAUSED
        print("✓ Session updated")

        # Create checkpoint
        checkpoint = manager.create_checkpoint(
            session_id=session.session_id,
            step_name="test_step",
            phase="story_outline",
            input_data={"idea": "test"},
            output_data={"title": "Test Story"},
        )
        print(f"✓ Checkpoint created: {checkpoint.id}")

        # Get checkpoints
        checkpoints = manager.get_checkpoints(session.session_id)
        assert len(checkpoints) > 0
        print(f"✓ Retrieved {len(checkpoints)} checkpoint(s)")

        # List sessions
        sessions = manager.list_sessions(limit=5)
        assert len(sessions) > 0
        print(f"✓ Listed {len(sessions)} session(s)")

        # Delete session
        manager.delete_session(session.session_id)
        deleted = manager.get_session(session.session_id)
        assert deleted is None
        print("✓ Session deleted")

        return True

    except Exception as e:
        import traceback
        print(f"✗ SessionManager error: {e}")
        traceback.print_exc()
        return False


def test_state_serialization():
    """Test state serialization and deserialization."""
    print("\n=== Test 2: State Serialization ===")

    try:
        from agents import (
            SessionManager, AgentState, WorkflowPhase,
            InteractionMode, UserRequest
        )

        manager = SessionManager()

        # Create a session
        session = manager.create_session(
            user_request="Serialization test",
            mode=InteractionMode.INTERACTIVE,
        )

        # Create a state with data
        request = UserRequest(
            idea="A robot learns to love",
            genre="sci-fi",
            num_episodes=2,
        )

        state = AgentState(
            request=request,
            phase=WorkflowPhase.STORY_OUTLINE,
            mode=InteractionMode.INTERACTIVE,
            project_id=123,
            project_name="Test Project",
            story_outline={"title": "Love Machine", "theme": "AI emotions"},
            characters=[{"name": "Robot", "personality": "curious"}],
            pending_approval=True,
            approval_type="story_outline",
        )

        # Save state
        manager.save_state(session.session_id, state)
        print("✓ State saved")

        # Load state
        loaded = manager.load_state(session.session_id)
        assert loaded is not None
        assert loaded.project_id == 123
        assert loaded.project_name == "Test Project"
        assert loaded.phase == WorkflowPhase.STORY_OUTLINE
        assert loaded.request.idea == "A robot learns to love"
        assert len(loaded.characters) == 1
        print("✓ State loaded and verified")

        # Clean up
        manager.delete_session(session.session_id)

        return True

    except Exception as e:
        import traceback
        print(f"✗ Serialization error: {e}")
        traceback.print_exc()
        return False


def test_persistent_workflow_runner():
    """Test PersistentWorkflowRunner."""
    print("\n=== Test 3: PersistentWorkflowRunner ===")

    try:
        from agents import PersistentWorkflowRunner, InteractionMode

        runner = PersistentWorkflowRunner()
        print("✓ PersistentWorkflowRunner created")

        # Start workflow
        print("  Starting workflow (this may take a moment)...")
        result = runner.start(
            idea="一个勇敢的小猫",
            genre="喜剧",
            num_episodes=1,
            episode_duration=30,
            mode=InteractionMode.INTERACTIVE,
        )

        session_id = result.get("session_id")
        assert session_id is not None
        print(f"✓ Workflow started, session: {session_id[:8]}...")

        summary = result.get("summary", {})
        print(f"  Phase: {summary.get('phase')}")
        print(f"  Pending: {summary.get('pending_approval')}")

        # List sessions
        sessions = runner.list_sessions(limit=5)
        assert len(sessions) > 0
        print(f"✓ Found {len(sessions)} session(s)")

        # Get session info
        info = runner.get_session_info(session_id)
        assert info['session']['session_id'] == session_id
        print(f"✓ Session info retrieved")

        # Test resume (simulate pause and resume)
        if summary.get("pending_approval"):
            print("  Testing resume functionality...")
            resumed = runner.resume(session_id)
            assert resumed['session_id'] == session_id
            print("✓ Session resumed successfully")

        return True

    except Exception as e:
        import traceback
        print(f"✗ PersistentWorkflowRunner error: {e}")
        traceback.print_exc()
        return False


def test_resume_from_error():
    """Test resuming a failed session."""
    print("\n=== Test 4: Resume From Error ===")

    try:
        from agents import (
            SessionManager, SessionStatus, AgentState, WorkflowPhase,
            InteractionMode, UserRequest, PersistentWorkflowRunner
        )

        manager = SessionManager()

        # Create a session and simulate failure
        session = manager.create_session(
            user_request="Test resume from error",
            mode=InteractionMode.INTERACTIVE,
        )
        session_id = session.session_id
        print(f"✓ Session created: {session_id[:8]}...")

        # Create a state with error
        request = UserRequest(
            idea="Test idea",
            genre="drama",
            num_episodes=1,
        )

        state = AgentState(
            request=request,
            phase=WorkflowPhase.VIDEO_GENERATION,
            mode=InteractionMode.INTERACTIVE,
            project_id=999,
            project_name="Error Test",
            error="SSL connection failed",
            video_prompts={"ep1_shot1": "Test prompt"},
            video_tasks={"ep1_shot1": {"status": "failed"}},
        )

        # Save the failed state
        manager.save_state(session_id, state)
        print("✓ Failed state saved")

        # Verify session is marked as failed
        session = manager.get_session(session_id)
        assert session.status == SessionStatus.FAILED
        print("✓ Session marked as FAILED")

        # Now try to resume
        runner = PersistentWorkflowRunner()
        result = runner.resume(session_id, retry_on_error=True)

        # Verify resume worked
        assert result.get('resumed_from_error') == True
        assert result['state'].get('error') is None
        print("✓ Session resumed from error state")

        # Verify session is no longer FAILED (could be RUNNING or PAUSED after workflow continues)
        session = manager.get_session(session_id)
        assert session.status != SessionStatus.FAILED, f"Session still FAILED: {session.status}"
        print(f"✓ Session status changed to {session.status.value}")

        # Verify retry count incremented
        assert result['state'].get('retry_count', 0) >= 1
        print(f"✓ Retry count: {result['state'].get('retry_count')}")

        # Clean up
        manager.delete_session(session_id)

        return True

    except Exception as e:
        import traceback
        print(f"✗ Resume from error test failed: {e}")
        traceback.print_exc()
        return False


def test_cli_import():
    """Test CLI module can be imported."""
    print("\n=== Test 5: CLI Import ===")

    try:
        # This tests that the CLI script can be imported without errors
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "run_workflow",
            os.path.join(os.path.dirname(__file__), "run_workflow.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert hasattr(module, 'WorkflowCLI')
        print("✓ CLI module imported successfully")

        cli = module.WorkflowCLI()
        assert cli.runner is not None
        print("✓ WorkflowCLI instantiated")

        return True

    except Exception as e:
        import traceback
        print(f"✗ CLI import error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Session Management Test Suite")
    print("=" * 60)

    results = []

    # Test 1: SessionManager
    results.append(("SessionManager", test_session_manager()))

    # Test 2: State Serialization
    results.append(("State Serialization", test_state_serialization()))

    # Test 3: PersistentWorkflowRunner
    results.append(("PersistentWorkflowRunner", test_persistent_workflow_runner()))

    # Test 4: Resume From Error
    results.append(("Resume From Error", test_resume_from_error()))

    # Test 5: CLI Import
    results.append(("CLI Import", test_cli_import()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
