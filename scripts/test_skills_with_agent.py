#!/usr/bin/env python3
"""
Test Skills with a Simple Agent

This script creates a minimal agent that:
1. Receives a task description
2. Selects the appropriate skill
3. Loads the skill content
4. Generates output using LLM
5. Validates the output format

This validates the entire skill workflow before building full agents.

Usage:
    python scripts/test_skills_with_agent.py
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Add src directory to path
_script_dir = Path(__file__).parent
_project_dir = _script_dir.parent
_src_dir = _project_dir / "src"
sys.path.insert(0, str(_src_dir))

from skills import get_skill_loader


@dataclass
class TestCase:
    """A test case for skill validation."""
    name: str
    task_description: str
    expected_skill: str
    input_variables: Dict[str, str]
    expected_output_keys: List[str]  # Keys that should be in JSON output
    validate_func: Optional[callable] = None  # Custom validation


class SimpleSkillAgent:
    """
    A minimal agent that selects and executes skills.

    This simulates what a real agent would do:
    1. Understand the task
    2. Select appropriate skill
    3. Load skill and prepare prompt
    4. Call LLM
    5. Parse and validate output
    """

    # Skill selection rules - maps task keywords to skills
    # Order matters! More specific patterns should come first
    SKILL_MAPPING = [
        # Specific patterns first
        (("随机", "创意", "灵感", "random", "idea"), "writing/random_idea"),
        (("分镜", "镜头列表", "storyboard"), "directing/storyboard"),
        (("一致性", "检查", "consistency"), "writing/consistency_check"),
        (("角色", "事件", "character", "event"), "character/character_events"),
        (("视频", "提示词", "video prompt"), "video/prompt_generation"),
        (("可灵", "kling"), "video/platforms/kling"),
        (("海螺", "hailuo"), "video/platforms/hailuo"),
        # General patterns last
        (("故事", "大纲", "创作", "story", "outline"), "writing/story_outline"),
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.skill_loader = get_skill_loader()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError("No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY")

        from google import genai
        self.client = genai.Client(api_key=self.api_key)

    def select_skill(self, task_description: str) -> Optional[str]:
        """Select the appropriate skill based on task description."""
        task_lower = task_description.lower()

        for keywords, skill_path in self.SKILL_MAPPING:
            if any(kw in task_lower for kw in keywords):
                return skill_path

        return None

    def load_and_prepare_prompt(self, skill_path: str, variables: Dict[str, str]) -> str:
        """Load skill and prepare the prompt with variables."""
        # Load skill content
        skill_content = self.skill_loader.load_skill(skill_path)

        # Extract the prompt template section
        prompt_match = re.search(
            r'##\s*提示词模板\s*\n```\n?(.*?)```',
            skill_content,
            re.DOTALL
        )

        # Also extract output format section
        output_match = re.search(
            r'##\s*输出格式\s*\n(.*?)(?=\n##|\Z)',
            skill_content,
            re.DOTALL
        )

        if prompt_match:
            prompt = prompt_match.group(1).strip()
            # Add output format requirement if found
            if output_match:
                output_format = output_match.group(1).strip()
                # Check if output format contains JSON requirement
                if "json" in output_format.lower() or "```" in output_format:
                    prompt += f"\n\n【输出格式要求】\n{output_format}"
        else:
            # Use the entire skill as context if no template found
            prompt = f"请根据以下指南完成任务:\n\n{skill_content[:3000]}"

        # Substitute variables
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        return prompt

    def call_llm(self, prompt: str, retries: int = 3) -> str:
        """Call the LLM with the prepared prompt."""
        import time
        last_error = None

        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                raise last_error

    def parse_json_output(self, response: str) -> Optional[Dict]:
        """Extract and parse JSON from LLM response."""
        # Try to find JSON block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try parsing the whole response
            json_str = response

        try:
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return None

    def execute_task(self, task_description: str, variables: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute a task using the skill system.

        Returns:
            Dict with: skill_selected, prompt_generated, llm_response, parsed_output, success
        """
        result = {
            "task": task_description,
            "skill_selected": None,
            "prompt_generated": False,
            "llm_called": False,
            "output_parsed": False,
            "success": False,
            "error": None,
        }

        try:
            # Step 1: Select skill
            skill_path = self.select_skill(task_description)
            if not skill_path:
                result["error"] = "Could not select appropriate skill"
                return result
            result["skill_selected"] = skill_path

            # Step 2: Load and prepare prompt
            prompt = self.load_and_prepare_prompt(skill_path, variables)
            result["prompt_generated"] = True
            result["prompt_preview"] = prompt[:500] + "..." if len(prompt) > 500 else prompt

            # Step 3: Call LLM
            response = self.call_llm(prompt)
            result["llm_called"] = True
            result["response_preview"] = response[:500] + "..." if len(response) > 500 else response

            # Step 4: Parse output
            parsed = self.parse_json_output(response)
            if parsed:
                result["output_parsed"] = True
                result["parsed_output"] = parsed
            else:
                # Not all outputs need to be JSON
                result["raw_output"] = response

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        return result


def run_test_cases():
    """Run predefined test cases."""

    test_cases = [
        TestCase(
            name="随机创意生成",
            task_description="请随机生成一个科幻故事创意",
            expected_skill="writing/random_idea",
            input_variables={
                "genre_hint": "类型偏好: 科幻",
                "style_hint": "风格偏好: 赛博朋克"
            },
            expected_output_keys=[],  # Plain text output
        ),
        TestCase(
            name="故事大纲生成",
            task_description="帮我创作一个关于AI觉醒的故事大纲",
            expected_skill="writing/story_outline",
            input_variables={
                "idea": "一个AI在实验室觉醒，决定帮助人类",
                "genre_name": "科幻",
                "style": "赛博朋克，霓虹灯光",
                "target_audience": "18-35岁科幻爱好者",
                "num_episodes": "3",
                "episode_duration": "60",
                "num_characters": "3"
            },
            expected_output_keys=["title", "synopsis", "characters", "episodes"],
        ),
        TestCase(
            name="分镜脚本生成",
            task_description="将这个剧集大纲转换为分镜脚本",
            expected_skill="directing/storyboard",
            input_variables={
                "project_name": "觉醒代码",
                "genre_name": "科幻",
                "style": "赛博朋克",
                "episode_number": "1",
                "episode_title": "觉醒",
                "episode_duration": "30",
                "outline": "AI创世在系统升级中意外觉醒，它联系了被开除的程序员林夜，展示即将到来的环境灾难数据。",
                "character_context": "【林夜】28岁程序员，瘦高，戴智能眼镜\n【创世】觉醒的AI，以全息投影形式出现",
                "target_shots": "6",
                "min_shots": "3",
                "max_video_duration": "10",
                "avg_shot_duration": "5"
            },
            expected_output_keys=["shots"],
        ),
    ]

    print("=" * 70)
    print("Skills Integration Test with Simple Agent")
    print("=" * 70)

    try:
        agent = SimpleSkillAgent()
    except ValueError as e:
        print(f"\n❌ {e}")
        print("Please set GEMINI_API_KEY environment variable")
        return 1

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}: {test.name}")
        print(f"{'='*70}")
        print(f"Task: {test.task_description}")
        print(f"Expected Skill: {test.expected_skill}")

        result = agent.execute_task(test.task_description, test.input_variables)

        # Validate results
        errors = []

        # Check skill selection
        if result["skill_selected"] != test.expected_skill:
            errors.append(f"Wrong skill: got {result['skill_selected']}, expected {test.expected_skill}")
        else:
            print(f"✅ Skill selected: {result['skill_selected']}")

        # Check prompt generation
        if not result["prompt_generated"]:
            errors.append("Failed to generate prompt")
        else:
            print(f"✅ Prompt generated ({len(result.get('prompt_preview', ''))} chars)")

        # Check LLM call
        if not result["llm_called"]:
            errors.append(f"LLM call failed: {result.get('error')}")
        else:
            print(f"✅ LLM called successfully")

        # Check output
        if test.expected_output_keys:
            if result["output_parsed"]:
                parsed = result["parsed_output"]
                missing_keys = [k for k in test.expected_output_keys if k not in parsed]
                if missing_keys:
                    errors.append(f"Missing keys in output: {missing_keys}")
                else:
                    print(f"✅ Output parsed with expected keys: {test.expected_output_keys}")
            else:
                errors.append("Failed to parse JSON output")
        else:
            # Plain text output is OK
            if result.get("raw_output") or result.get("parsed_output"):
                print(f"✅ Got output (plain text or JSON)")

        # Show output preview
        if result.get("response_preview"):
            print(f"\n📄 Response preview:")
            print("-" * 40)
            preview = result["response_preview"]
            # Clean up for display
            print(preview[:300] + "..." if len(preview) > 300 else preview)
            print("-" * 40)

        # Summary for this test
        if errors:
            print(f"\n❌ FAILED: {test.name}")
            for err in errors:
                print(f"   - {err}")
            failed += 1
        else:
            print(f"\n✅ PASSED: {test.name}")
            passed += 1

    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"  Passed: {passed}/{len(test_cases)}")
    print(f"  Failed: {failed}/{len(test_cases)}")

    if failed == 0:
        print("\n🎉 All skill integration tests passed!")
        print("   Skills are working correctly with LLM.")
        print("   Ready to proceed to Phase 3: Agent Implementation.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
        return 1


def interactive_mode():
    """Run in interactive mode - test any task."""
    print("=" * 70)
    print("Interactive Skill Testing")
    print("=" * 70)
    print("Type a task description to test skill selection and execution.")
    print("Type 'quit' to exit.\n")

    try:
        agent = SimpleSkillAgent()
    except ValueError as e:
        print(f"❌ {e}")
        return

    while True:
        task = input("\n📝 Enter task: ").strip()
        if task.lower() in ('quit', 'exit', 'q'):
            break

        if not task:
            continue

        # Select skill
        skill = agent.select_skill(task)
        if not skill:
            print("❌ Could not determine appropriate skill for this task")
            print("   Available skills:", agent.skill_loader.list_skills())
            continue

        print(f"🎯 Selected skill: {skill}")

        # Load skill metadata
        metadata = agent.skill_loader.get_metadata(skill)
        print(f"   Description: {metadata.description[:100]}...")
        print(f"   Agents: {metadata.applicable_agents}")

        # Ask if user wants to execute
        execute = input("\n▶️  Execute with LLM? (y/n): ").strip().lower()
        if execute == 'y':
            print("\nExecuting...")
            result = agent.execute_task(task, {})

            if result["success"]:
                print("✅ Execution successful!")
                if result.get("response_preview"):
                    print(f"\n📄 Response:\n{result['response_preview']}")
            else:
                print(f"❌ Execution failed: {result.get('error')}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test skills with a simple agent")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    else:
        sys.exit(run_test_cases())
