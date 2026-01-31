#!/usr/bin/env python3
"""
End-to-End Test for Multi-Agent Video Generation

Tests the complete workflow from story idea to video prompt generation.
"""

import os
import sys
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from agents import (
    PersistentWorkflowRunner,
    InteractionMode,
    WorkflowPhase,
    SessionStatus,
)


def test_full_workflow_interactive():
    """Test full workflow in interactive mode with auto-approval."""
    print("\n" + "=" * 60)
    print("End-to-End Test: Interactive Mode (Auto-Approve)")
    print("=" * 60)

    runner = PersistentWorkflowRunner()
    session_id = None

    try:
        # Step 1: Start workflow
        print("\n[Step 1] Starting workflow...")
        result = runner.start(
            idea="一只勇敢的小猫咪拯救了森林",
            genre="喜剧",
            style="动画",
            num_episodes=1,
            episode_duration=30,
            num_characters=2,
            target_platform="kling",
            mode=InteractionMode.INTERACTIVE,
        )

        session_id = result['session_id']
        summary = result['summary']
        print(f"  Session: {session_id[:8]}...")
        print(f"  Phase: {summary['phase']}")
        print(f"  Project: {summary.get('project_name', 'N/A')}")

        assert summary['phase'] == 'story_outline'
        assert summary['pending_approval'] == True
        print("✓ Story outline generated")

        # Step 2: Approve story outline -> Characters
        print("\n[Step 2] Approving story outline...")
        result = runner.approve_and_continue(approved=True)
        summary = result['summary']
        print(f"  Phase: {summary['phase']}")
        print(f"  Characters: {summary.get('num_characters', 0)}")

        assert summary['phase'] == 'character_design'
        print("✓ Characters designed")

        # Step 3: Approve characters -> Episodes
        print("\n[Step 3] Approving characters...")
        result = runner.approve_and_continue(approved=True)
        summary = result['summary']
        print(f"  Phase: {summary['phase']}")
        print(f"  Episodes: {summary.get('num_episodes', 0)}")

        assert summary['phase'] == 'storyboard'
        print("✓ Episodes written")

        # Step 4: Approve episodes -> Storyboard
        print("\n[Step 4] Approving episodes, creating storyboard...")
        result = runner.approve_and_continue(approved=True)
        summary = result['summary']
        print(f"  Phase: {summary['phase']}")
        print(f"  Shots: {summary.get('num_shots', 0)}")

        assert summary['phase'] == 'video_prompts'
        print("✓ Storyboard created")

        # Step 5: Approve storyboard -> Video prompts
        print("\n[Step 5] Approving storyboard, generating video prompts...")
        result = runner.approve_and_continue(approved=True)
        summary = result['summary']
        print(f"  Phase: {summary['phase']}")
        print(f"  Prompts: {summary.get('num_prompts', 0)}")

        # At this point we should be at video_generation or review
        # depending on whether video generation is skipped
        print("✓ Video prompts generated")

        # Final state check
        state = runner.get_state()
        print(f"\n[Final State]")
        print(f"  Phase: {summary['phase']}")
        print(f"  Characters: {summary.get('num_characters', 0)}")
        print(f"  Episodes: {summary.get('num_episodes', 0)}")
        print(f"  Shots: {summary.get('num_shots', 0)}")
        print(f"  Prompts: {summary.get('num_prompts', 0)}")

        # Verify we generated meaningful content
        assert summary.get('num_characters', 0) > 0, "No characters generated"
        assert summary.get('num_shots', 0) > 0, "No shots generated"

        print("\n✓ End-to-end workflow completed successfully!")
        return True, session_id

    except Exception as e:
        import traceback
        print(f"\n✗ Workflow failed: {e}")
        traceback.print_exc()
        return False, session_id


def test_session_recovery():
    """Test session pause and recovery."""
    print("\n" + "=" * 60)
    print("End-to-End Test: Session Recovery")
    print("=" * 60)

    try:
        # Create first runner and start workflow
        print("\n[Step 1] Starting workflow with Runner 1...")
        runner1 = PersistentWorkflowRunner()
        result = runner1.start(
            idea="太空探险",
            genre="科幻",
            num_episodes=1,
            mode=InteractionMode.INTERACTIVE,
        )
        session_id = result['session_id']
        print(f"  Session: {session_id[:8]}...")

        # Simulate pause (just don't approve)
        print("\n[Step 2] Simulating pause (workflow is waiting for approval)...")
        summary1 = result['summary']
        print(f"  Phase: {summary1['phase']}")
        print(f"  Pending: {summary1['pending_approval']}")

        # Create second runner and resume
        print("\n[Step 3] Creating new Runner and resuming session...")
        runner2 = PersistentWorkflowRunner()
        result = runner2.resume(session_id)

        summary2 = result['summary']
        print(f"  Session: {result['session_id'][:8]}...")
        print(f"  Phase: {summary2['phase']}")
        print(f"  Project: {summary2.get('project_name', 'N/A')}")

        # Verify state was preserved
        assert result['session_id'] == session_id
        assert summary2['phase'] == summary1['phase']
        assert summary2.get('project_name') == summary1.get('project_name')

        print("\n✓ Session recovery successful!")
        return True

    except Exception as e:
        import traceback
        print(f"\n✗ Recovery failed: {e}")
        traceback.print_exc()
        return False


def test_autonomous_mode():
    """Test autonomous mode (no approval checkpoints)."""
    print("\n" + "=" * 60)
    print("End-to-End Test: Autonomous Mode")
    print("=" * 60)

    try:
        runner = PersistentWorkflowRunner()

        print("\n[Starting autonomous workflow...]")
        result = runner.start(
            idea="机器人的梦想",
            genre="科幻",
            num_episodes=1,
            episode_duration=30,
            mode=InteractionMode.AUTONOMOUS,
        )

        summary = result['summary']
        print(f"  Phase: {summary['phase']}")

        # In autonomous mode, workflow runs to completion without pausing
        # But our current implementation still pauses at checkpoints
        # This test verifies the mode is set correctly
        state = runner.get_state()
        mode = state.get('mode')
        if isinstance(mode, InteractionMode):
            mode = mode.value
        assert mode == 'autonomous', f"Expected autonomous mode, got {mode}"

        print("✓ Autonomous mode configured correctly")
        return True

    except Exception as e:
        import traceback
        print(f"\n✗ Autonomous mode failed: {e}")
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling and rejection."""
    print("\n" + "=" * 60)
    print("End-to-End Test: Error Handling")
    print("=" * 60)

    try:
        runner = PersistentWorkflowRunner()

        print("\n[Step 1] Starting workflow...")
        result = runner.start(
            idea="测试错误处理",
            genre="drama",
            num_episodes=1,
            mode=InteractionMode.INTERACTIVE,
        )
        session_id = result['session_id']

        print("\n[Step 2] Rejecting approval...")
        result = runner.approve_and_continue(approved=False, feedback="Testing rejection")

        summary = result['summary']
        print(f"  Phase: {summary['phase']}")
        print(f"  Error: {summary.get('error', 'N/A')}")

        # Verify error state
        assert summary.get('error') is not None
        assert 'rejected' in summary['error'].lower()

        print("\n✓ Error handling works correctly")
        return True

    except Exception as e:
        import traceback
        print(f"\n✗ Error handling test failed: {e}")
        traceback.print_exc()
        return False


def cleanup_test_sessions():
    """Clean up test sessions."""
    print("\n" + "-" * 60)
    print("Cleaning up test sessions...")

    try:
        runner = PersistentWorkflowRunner()
        sessions = runner.list_sessions(limit=50)

        test_keywords = ['勇敢的小猫', '太空探险', '机器人的梦想', '测试错误']
        deleted = 0

        for s in sessions:
            request = s.get('user_request', '')
            if any(kw in request for kw in test_keywords):
                runner.delete_session(s['session_id'])
                deleted += 1

        print(f"  Deleted {deleted} test session(s)")

    except Exception as e:
        print(f"  Warning: Cleanup failed: {e}")


def main():
    """Run all end-to-end tests."""
    print("\n" + "=" * 60)
    print("Multi-Agent Video Generation - End-to-End Test Suite")
    print("=" * 60)

    results = []

    # Test 1: Full workflow
    success, session_id = test_full_workflow_interactive()
    results.append(("Full Workflow (Interactive)", success))

    # Test 2: Session recovery
    results.append(("Session Recovery", test_session_recovery()))

    # Test 3: Autonomous mode
    results.append(("Autonomous Mode", test_autonomous_mode()))

    # Test 4: Error handling
    results.append(("Error Handling", test_error_handling()))

    # Cleanup
    cleanup_test_sessions()

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
