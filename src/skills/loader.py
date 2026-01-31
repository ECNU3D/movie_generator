"""
Skill Loader

Loads and manages skill files for agents.
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

SKILLS_DIR = Path(__file__).parent


@dataclass
class SkillMetadata:
    """Metadata parsed from a skill file."""
    name: str = ""
    description: str = ""
    applicable_agents: List[str] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    input_variables: List[str] = field(default_factory=list)
    output_format: str = ""


class SkillLoader:
    """
    Skills Loader

    Loads skill files (Markdown) and provides them to agents.
    Skills contain instructions, guidelines, and examples for specific tasks.
    """

    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = skills_dir or SKILLS_DIR
        self._cache: Dict[str, str] = {}
        self._metadata_cache: Dict[str, SkillMetadata] = {}

    def load_skill(self, skill_path: str) -> str:
        """
        Load a skill file by path.

        Args:
            skill_path: Relative path to skill without .md extension
                       e.g., "writing/story_outline" or "video/platforms/kling"

        Returns:
            Skill content (Markdown)

        Raises:
            FileNotFoundError: If skill file doesn't exist
        """
        if skill_path in self._cache:
            return self._cache[skill_path]

        file_path = self.skills_dir / f"{skill_path}.md"
        if not file_path.exists():
            raise FileNotFoundError(f"Skill not found: {skill_path} (looked for {file_path})")

        content = file_path.read_text(encoding="utf-8")
        self._cache[skill_path] = content
        return content

    def load_skill_with_variables(self, skill_path: str, **variables) -> str:
        """
        Load a skill and substitute variables.

        Args:
            skill_path: Relative path to skill
            **variables: Variables to substitute in the skill template

        Returns:
            Skill content with variables substituted
        """
        content = self.load_skill(skill_path)

        # Simple variable substitution using {variable_name} syntax
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))

        return content

    def get_metadata(self, skill_path: str) -> SkillMetadata:
        """
        Parse and return metadata from a skill file.

        Metadata is extracted from the skill file header sections.
        """
        if skill_path in self._metadata_cache:
            return self._metadata_cache[skill_path]

        content = self.load_skill(skill_path)
        metadata = self._parse_metadata(content)
        self._metadata_cache[skill_path] = metadata
        return metadata

    def _parse_metadata(self, content: str) -> SkillMetadata:
        """Parse metadata from skill content."""
        metadata = SkillMetadata()

        # Extract skill name from first heading
        name_match = re.search(r'^#\s+(?:Skill:\s*)?(.+)$', content, re.MULTILINE)
        if name_match:
            metadata.name = name_match.group(1).strip()

        # Extract description section
        desc_match = re.search(r'##\s*描述\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if desc_match:
            metadata.description = desc_match.group(1).strip()

        # Extract applicable agents
        agents_match = re.search(r'##\s*适用\s*Agent\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if agents_match:
            agents_text = agents_match.group(1)
            metadata.applicable_agents = [
                line.strip().lstrip('- ')
                for line in agents_text.strip().split('\n')
                if line.strip() and line.strip().startswith('-')
            ]

        # Extract available tools
        tools_match = re.search(r'##\s*可用工具.*?\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if tools_match:
            tools_text = tools_match.group(1)
            metadata.available_tools = [
                line.strip().lstrip('- ').split(' ')[0].strip('`')
                for line in tools_text.strip().split('\n')
                if line.strip() and line.strip().startswith('-')
            ]

        # Extract input variables
        input_match = re.search(r'##\s*输入\s*(?:变量)?\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if input_match:
            input_text = input_match.group(1)
            metadata.input_variables = [
                line.strip().lstrip('- ').split(':')[0].split('(')[0].strip()
                for line in input_text.strip().split('\n')
                if line.strip() and line.strip().startswith('-')
            ]

        # Extract output format
        output_match = re.search(r'##\s*输出格式\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if output_match:
            metadata.output_format = output_match.group(1).strip()

        return metadata

    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """
        List available skills.

        Args:
            category: Optional category to filter (e.g., "writing", "video")

        Returns:
            List of skill paths (without .md extension)
        """
        if category:
            search_dir = self.skills_dir / category
        else:
            search_dir = self.skills_dir

        if not search_dir.exists():
            return []

        skills = []
        for md_file in search_dir.rglob("*.md"):
            rel_path = md_file.relative_to(self.skills_dir)
            skill_name = str(rel_path.with_suffix(""))
            skills.append(skill_name)

        return sorted(skills)

    def list_categories(self) -> List[str]:
        """List all skill categories (top-level directories)."""
        categories = []
        for item in self.skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                categories.append(item.name)
        return sorted(categories)

    def skill_exists(self, skill_path: str) -> bool:
        """Check if a skill exists."""
        file_path = self.skills_dir / f"{skill_path}.md"
        return file_path.exists()

    def clear_cache(self):
        """Clear the skill cache."""
        self._cache.clear()
        self._metadata_cache.clear()


# Singleton instance
_skill_loader: Optional[SkillLoader] = None


def get_skill_loader() -> SkillLoader:
    """Get the global skill loader instance."""
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader()
    return _skill_loader
