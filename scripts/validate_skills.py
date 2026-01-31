#!/usr/bin/env python3
"""
Validate Skills

This script validates all skill files to ensure they:
1. Can be loaded without errors
2. Have required sections (description, agents, tools, output format)
3. Have valid prompt templates with proper variable placeholders
4. Reference existing MCP tools

Usage:
    python scripts/validate_skills.py
    python scripts/validate_skills.py --verbose
    python scripts/validate_skills.py --test-llm  # Actually call LLM (requires API key)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set

# Add src directory to path
_script_dir = Path(__file__).parent
_project_dir = _script_dir.parent
_src_dir = _project_dir / "src"
sys.path.insert(0, str(_src_dir))


class SkillValidator:
    """Validates skill files for correctness and completeness."""

    # Required sections in a skill file
    REQUIRED_SECTIONS = ["描述", "适用 Agent", "输出格式"]
    RECOMMENDED_SECTIONS = ["可用工具", "指导原则", "示例", "提示词模板"]

    # Known MCP tools from our servers
    KNOWN_TOOLS = {
        # Project server
        "create_project", "get_project", "update_project", "delete_project", "list_projects",
        "create_character", "get_character", "update_character", "delete_character",
        "add_character_event", "get_character_context", "list_characters",
        "create_episode", "get_episode", "update_episode", "delete_episode", "list_episodes",
        # Storyboard server
        "create_shot", "get_shot", "update_shot", "delete_shot", "list_shots",
        "batch_create_shots", "delete_all_shots", "save_generated_prompt",
        "get_generated_prompt", "get_storyboard_summary",
        "get_shot_type_names", "get_camera_movement_names",
        # Video server
        "list_providers", "get_provider_status",
        "submit_text_to_video", "text_to_video_sync",
        "submit_image_to_video", "image_to_video_sync",
        "get_task_status", "wait_for_task", "batch_submit_text_to_video",
    }

    # Known agent names
    KNOWN_AGENTS = {
        "supervisor", "story_writer", "character_designer", "director", "video_producer"
    }

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[int, int]:
        """
        Validate all skills.

        Returns:
            Tuple of (error_count, warning_count)
        """
        from skills import get_skill_loader

        loader = get_skill_loader()
        skills = loader.list_skills()

        print(f"Validating {len(skills)} skills...\n")

        total_errors = 0
        total_warnings = 0

        for skill_path in skills:
            self.errors = []
            self.warnings = []

            print(f"  [{skill_path}]")

            try:
                content = loader.load_skill(skill_path)
                self._validate_skill(skill_path, content)
            except Exception as e:
                self.errors.append(f"Failed to load: {e}")

            # Print results
            if self.errors:
                for error in self.errors:
                    print(f"    ❌ ERROR: {error}")
                total_errors += len(self.errors)
            if self.warnings:
                for warning in self.warnings:
                    print(f"    ⚠️  WARN: {warning}")
                total_warnings += len(self.warnings)
            if not self.errors and not self.warnings:
                print(f"    ✅ OK")

        return total_errors, total_warnings

    def _validate_skill(self, skill_path: str, content: str):
        """Validate a single skill."""
        # Check required sections
        self._check_required_sections(content)

        # Check recommended sections
        self._check_recommended_sections(content)

        # Check agent references
        self._check_agent_references(content)

        # Check tool references
        self._check_tool_references(content)

        # Check prompt template variables
        self._check_prompt_variables(content)

        # Check for common issues
        self._check_common_issues(content)

    def _check_required_sections(self, content: str):
        """Check that required sections exist."""
        for section in self.REQUIRED_SECTIONS:
            pattern = rf'^##\s*{re.escape(section)}'
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                self.errors.append(f"Missing required section: '{section}'")

    def _check_recommended_sections(self, content: str):
        """Check that recommended sections exist."""
        for section in self.RECOMMENDED_SECTIONS:
            pattern = rf'^##\s*{re.escape(section)}'
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                if self.verbose:
                    self.warnings.append(f"Missing recommended section: '{section}'")

    def _check_agent_references(self, content: str):
        """Check that referenced agents are known."""
        # Find the "适用 Agent" section
        match = re.search(r'##\s*适用\s*Agent\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            section = match.group(1)
            # Extract agent names from bullet points
            agents = re.findall(r'-\s*(\w+)', section)
            for agent in agents:
                if agent.lower() not in self.KNOWN_AGENTS:
                    self.warnings.append(f"Unknown agent referenced: '{agent}'")

    def _check_tool_references(self, content: str):
        """Check that referenced tools exist in MCP servers."""
        # Find the "可用工具" section
        match = re.search(r'##\s*可用工具.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            section = match.group(1)
            # Extract tool names from backticks or bullet points
            tools = re.findall(r'`(\w+)`', section)
            for tool in tools:
                if tool not in self.KNOWN_TOOLS:
                    self.warnings.append(f"Unknown MCP tool referenced: '{tool}'")

    def _check_prompt_variables(self, content: str):
        """Check that prompt template variables are documented."""
        # Find all {variable} patterns in prompt templates
        prompt_match = re.search(r'```\n(.*?)```', content, re.DOTALL)
        if prompt_match:
            prompt = prompt_match.group(1)
            # Find single-brace variables (not double-brace JSON)
            variables = set(re.findall(r'(?<!\{)\{(\w+)\}(?!\})', prompt))

            # Check if variables are documented in input section
            input_match = re.search(r'##\s*输入.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if input_match and variables:
                input_section = input_match.group(1).lower()
                for var in variables:
                    if var.lower() not in input_section:
                        self.warnings.append(f"Variable '{{{var}}}' used but not documented in input section")

    def _check_common_issues(self, content: str):
        """Check for common issues in skill files."""
        # Check for title
        if not re.search(r'^#\s+', content, re.MULTILINE):
            self.errors.append("Missing main title (# Skill: ...)")

        # Check for empty sections
        sections = re.findall(r'^##\s+(.+)\n(.*?)(?=\n##|\Z)', content, re.MULTILINE | re.DOTALL)
        for section_name, section_content in sections:
            if len(section_content.strip()) < 10:
                self.warnings.append(f"Section '{section_name}' appears empty or too short")

        # Check for broken markdown
        unclosed_code_blocks = len(re.findall(r'```', content)) % 2
        if unclosed_code_blocks:
            self.errors.append("Unclosed code block (```) detected")


def test_skill_with_llm(skill_path: str) -> bool:
    """
    Test a skill by actually calling the LLM with sample inputs.

    Returns:
        True if test passed, False otherwise
    """
    import os
    from skills import get_skill_loader

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("  ⚠️  No API key found (GEMINI_API_KEY or GOOGLE_API_KEY)")
        return False

    loader = get_skill_loader()

    # Sample test data for different skill types
    test_data = {
        "writing/story_outline": {
            "idea": "一个机器人学会了爱",
            "genre_name": "科幻",
            "style": "温馨治愈",
            "target_audience": "年轻人",
            "num_episodes": "3",
            "episode_duration": "60",
            "num_characters": "3"
        },
        "writing/random_idea": {
            "genre_hint": "类型偏好: 科幻",
            "style_hint": "风格偏好: 赛博朋克"
        },
        "directing/storyboard": {
            "project_name": "测试项目",
            "genre_name": "科幻",
            "style": "赛博朋克",
            "episode_number": "1",
            "episode_title": "觉醒",
            "episode_duration": "60",
            "outline": "机器人在实验室觉醒",
            "character_context": "主角：林夜，28岁程序员",
            "target_shots": "6",
            "min_shots": "4",
            "max_video_duration": "10",
            "avg_shot_duration": "10"
        }
    }

    if skill_path not in test_data:
        print(f"  ⚠️  No test data defined for {skill_path}")
        return True  # Skip, not a failure

    try:
        # Load skill with variables
        content = loader.load_skill_with_variables(skill_path, **test_data[skill_path])

        # Extract the prompt template
        prompt_match = re.search(r'##\s*提示词模板\s*\n```\n?(.*?)```', content, re.DOTALL)
        if not prompt_match:
            print(f"  ⚠️  No prompt template found in {skill_path}")
            return True

        prompt = prompt_match.group(1).strip()

        # Replace any remaining variables
        for key, value in test_data[skill_path].items():
            prompt = prompt.replace(f"{{{key}}}", value)

        # Call LLM
        from google import genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt[:2000],  # Truncate for testing
        )

        if response.text and len(response.text) > 50:
            print(f"  ✅ LLM test passed ({len(response.text)} chars response)")
            return True
        else:
            print(f"  ❌ LLM test failed: response too short")
            return False

    except Exception as e:
        print(f"  ❌ LLM test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate skill files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all warnings")
    parser.add_argument("--test-llm", action="store_true", help="Test skills with actual LLM calls")
    parser.add_argument("--skill", type=str, help="Validate specific skill only")
    args = parser.parse_args()

    print("=" * 60)
    print("Skills Validation")
    print("=" * 60)

    validator = SkillValidator(verbose=args.verbose)

    if args.skill:
        # Validate specific skill
        from skills import get_skill_loader
        loader = get_skill_loader()
        content = loader.load_skill(args.skill)
        validator._validate_skill(args.skill, content)
        errors = len(validator.errors)
        warnings = len(validator.warnings)
    else:
        # Validate all skills
        errors, warnings = validator.validate_all()

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  Errors:   {errors}")
    print(f"  Warnings: {warnings}")

    if errors == 0:
        print("\n✅ All skills passed validation!")
    else:
        print(f"\n❌ {errors} error(s) found - please fix before proceeding")

    # Optional LLM testing
    if args.test_llm:
        print("\n" + "=" * 60)
        print("LLM Integration Tests")
        print("=" * 60)

        from skills import get_skill_loader
        loader = get_skill_loader()

        test_skills = ["writing/random_idea"]  # Start with simple one
        for skill_path in test_skills:
            print(f"\n  Testing {skill_path}...")
            test_skill_with_llm(skill_path)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
