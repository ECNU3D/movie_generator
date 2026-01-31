#!/usr/bin/env python3
"""
Test Script for Multi-Agent System

Validates that agents work correctly with LLM calls and state management.
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
    pass  # dotenv not required if env vars are set


def test_imports():
    """Test that all agent imports work."""
    print("\n=== Test 1: Import Agents ===")
    try:
        from agents import (
            AgentState,
            WorkflowPhase,
            InteractionMode,
            UserRequest,
            BaseAgent,
            StoryWriterAgent,
            DirectorAgent,
            VideoProducerAgent,
            SupervisorAgent,
            WorkflowRunner,
        )
        print("✓ All agent imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_state_creation():
    """Test AgentState creation."""
    print("\n=== Test 2: State Creation ===")
    try:
        from agents import AgentState, WorkflowPhase, UserRequest

        request = UserRequest(
            idea="A robot discovers emotions",
            genre="sci-fi",
            num_episodes=1,
            episode_duration=60,
        )

        state = AgentState(
            request=request,
            phase=WorkflowPhase.INIT,
        )

        assert state.request == request
        assert state.phase == WorkflowPhase.INIT
        assert state.pending_approval == False
        assert len(state.characters) == 0

        print(f"✓ State created: phase={state.phase.value}")
        return True
    except Exception as e:
        print(f"✗ State creation error: {e}")
        return False


def test_story_writer_outline():
    """Test StoryWriterAgent generates story outline."""
    print("\n=== Test 3: Story Writer - Generate Outline ===")
    try:
        from agents import StoryWriterAgent, AgentState, WorkflowPhase, UserRequest

        agent = StoryWriterAgent()
        print(f"  Agent: {agent.name}, Model: {agent.model}")

        request = UserRequest(
            idea="一个机器人学会了爱",
            genre="科幻",
            num_episodes=1,
            episode_duration=30,
            num_characters=2,
        )

        state = AgentState(
            request=request,
            phase=WorkflowPhase.INIT,
        )

        print("  Generating story outline (this may take a moment)...")
        result = agent.run(state)

        assert result.phase == WorkflowPhase.STORY_OUTLINE
        assert result.story_outline is not None
        assert result.project_id is not None
        assert result.pending_approval == True

        print(f"✓ Story outline generated")
        print(f"  Project: {result.project_name} (ID: {result.project_id})")
        print(f"  Outline keys: {list(result.story_outline.keys()) if isinstance(result.story_outline, dict) else 'text'}")
        return True, result

    except Exception as e:
        import traceback
        print(f"✗ Story writer error: {e}")
        traceback.print_exc()
        return False, None


def test_story_writer_characters(state):
    """Test StoryWriterAgent designs characters."""
    print("\n=== Test 4: Story Writer - Design Characters ===")
    try:
        from agents import StoryWriterAgent, WorkflowPhase

        agent = StoryWriterAgent()

        # Clear approval for next phase
        state.pending_approval = False

        print("  Designing characters...")
        result = agent.run(state)

        assert result.phase == WorkflowPhase.CHARACTER_DESIGN
        assert len(result.characters) > 0

        print(f"✓ Characters designed: {len(result.characters)}")
        for char in result.characters[:3]:
            name = char.get('name', 'Unknown')
            print(f"  - {name}")
        return True, result

    except Exception as e:
        import traceback
        print(f"✗ Character design error: {e}")
        traceback.print_exc()
        return False, state


def test_supervisor_workflow():
    """Test SupervisorAgent orchestration."""
    print("\n=== Test 5: Supervisor Workflow ===")
    try:
        from agents import SupervisorAgent, InteractionMode

        supervisor = SupervisorAgent()
        print(f"  Supervisor: {supervisor.name}")

        # Start workflow
        print("  Starting workflow...")
        state = supervisor.start_workflow(
            idea="一只猫咪的冒险",
            genre="喜剧",
            num_episodes=1,
            episode_duration=30,
            num_characters=2,
            mode=InteractionMode.INTERACTIVE,
        )

        print(f"  Phase: {state.phase.value}")
        print(f"  Pending approval: {state.pending_approval}")
        print(f"  Approval type: {state.approval_type}")

        if state.pending_approval:
            print("  (Workflow paused at checkpoint)")
            summary = supervisor.get_workflow_summary(state)
            print(f"  Summary: {summary}")

        print("✓ Supervisor workflow started successfully")
        return True

    except Exception as e:
        import traceback
        print(f"✗ Supervisor error: {e}")
        traceback.print_exc()
        return False


def test_workflow_runner():
    """Test WorkflowRunner with LangGraph."""
    print("\n=== Test 6: LangGraph Workflow Runner ===")
    try:
        from agents import WorkflowRunner, InteractionMode

        runner = WorkflowRunner()
        print("  WorkflowRunner created")

        # Start workflow
        print("  Starting workflow...")
        state = runner.start(
            idea="未来城市的一天",
            genre="科幻",
            num_episodes=1,
            episode_duration=30,
            num_characters=2,
            mode=InteractionMode.INTERACTIVE,
        )

        summary = runner.get_summary()
        print(f"  Summary: {summary}")

        if state.get("pending_approval"):
            print("  (Workflow paused at first checkpoint)")
            print(f"  Approval type: {state.get('approval_type')}")

        print("✓ WorkflowRunner test passed")
        return True

    except ImportError as e:
        print(f"! LangGraph not installed, skipping: {e}")
        return True  # Not a failure
    except Exception as e:
        import traceback
        print(f"✗ WorkflowRunner error: {e}")
        traceback.print_exc()
        return False


def test_chinese_character_design():
    """Test character design with Chinese input."""
    print("\n=== Test 7: Chinese Character Design ===")
    try:
        from agents import StoryWriterAgent, AgentState, WorkflowPhase, UserRequest

        agent = StoryWriterAgent()

        # Create state with Chinese story outline
        request = UserRequest(
            idea="机甲对抗外星虫族",
            genre="科幻",
            num_episodes=1,
            num_characters=3,
        )

        state = AgentState(
            request=request,
            phase=WorkflowPhase.STORY_OUTLINE,
            project_id=999,  # Fake ID to skip DB save
            story_outline={
                "title": "钢铁黎明",
                "theme": "人类抵抗外星入侵",
                "premise": "地球遭遇外星虫族入侵，人类研发机甲科技抵御",
            },
        )

        print("  Designing characters for Chinese story...")
        result = agent._design_characters(state)

        # Check results
        assert len(result.characters) > 0, "No characters generated"

        # Check first character has Chinese name
        first_char = result.characters[0]
        name = first_char.get('name', '')
        print(f"  First character: {name}")

        # Verify character has proper attributes
        assert first_char.get('name'), "Character missing name"
        assert first_char.get('personality') or first_char.get('background'), "Character missing description"

        print(f"✓ Generated {len(result.characters)} characters")
        for char in result.characters[:3]:
            role = char.get('role', '')
            print(f"  - {char.get('name')} ({role})")

        return True

    except Exception as e:
        import traceback
        print(f"✗ Chinese character design error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all agent tests."""
    print("=" * 60)
    print("Multi-Agent System Test Suite")
    print("=" * 60)

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: State creation
    results.append(("State Creation", test_state_creation()))

    # Test 3: Story outline
    success, state = test_story_writer_outline()
    results.append(("Story Outline", success))

    # Test 4: Characters (if outline succeeded)
    if success and state:
        success, state = test_story_writer_characters(state)
        results.append(("Character Design", success))

    # Test 5: Supervisor
    results.append(("Supervisor", test_supervisor_workflow()))

    # Test 6: WorkflowRunner
    results.append(("WorkflowRunner", test_workflow_runner()))

    # Test 7: Chinese character design
    results.append(("Chinese Characters", test_chinese_character_design()))

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
