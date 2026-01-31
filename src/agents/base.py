"""
Base Agent Class

Provides common functionality for all agents.
"""

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

from google import genai
from google.genai import types

from skills import get_skill_loader
from .state import AgentState, WorkflowPhase


class BaseAgent(ABC):
    """
    Base class for all agents.

    Provides:
    - LLM client access
    - Skill loading
    - MCP tool execution (via direct database calls for now)
    - Common utilities
    """

    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        model: str = "gemini-2.0-flash"
    ):
        self.name = name
        self.model = model
        self.skill_loader = get_skill_loader()

        # Initialize LLM client
        api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY")
        self.llm_client = genai.Client(api_key=api_key)

        # Database connection (lazy loaded)
        self._db = None

    @property
    def db(self):
        """Lazy load database connection."""
        if self._db is None:
            from story_generator.database import Database
            self._db = Database()
        return self._db

    @abstractmethod
    def run(self, state: AgentState) -> AgentState:
        """
        Execute the agent's task.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        pass

    def load_skill(self, skill_path: str, **variables) -> str:
        """Load a skill with optional variable substitution."""
        if variables:
            return self.skill_loader.load_skill_with_variables(skill_path, **variables)
        return self.skill_loader.load_skill(skill_path)

    def call_llm(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> str:
        """Call the LLM with a prompt."""
        response = self.llm_client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text

    def call_llm_with_skill(
        self,
        skill_path: str,
        variables: Dict[str, Any],
        additional_context: str = "",
        temperature: float = 0.7
    ) -> str:
        """
        Load a skill, prepare prompt, and call LLM.

        Args:
            skill_path: Path to the skill
            variables: Variables to substitute in the skill
            additional_context: Extra context to append
            temperature: LLM temperature

        Returns:
            LLM response text
        """
        # Load skill content
        skill_content = self.skill_loader.load_skill(skill_path)

        # Extract prompt template
        prompt = self._extract_prompt_template(skill_content)

        # Substitute variables
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))

        # Add output format if available
        output_format = self._extract_output_format(skill_content)
        if output_format:
            prompt += f"\n\n【输出格式要求】\n{output_format}"

        # Add additional context
        if additional_context:
            prompt += f"\n\n{additional_context}"

        return self.call_llm(prompt, temperature=temperature)

    def _extract_prompt_template(self, skill_content: str) -> str:
        """Extract prompt template from skill content."""
        match = re.search(
            r'##\s*提示词模板\s*\n```\n?(.*?)```',
            skill_content,
            re.DOTALL
        )
        if match:
            return match.group(1).strip()
        # Fall back to using the whole skill as guidance
        return f"请根据以下指南完成任务:\n\n{skill_content[:3000]}"

    def _extract_output_format(self, skill_content: str) -> Optional[str]:
        """Extract output format section from skill content."""
        match = re.search(
            r'##\s*输出格式\s*\n(.*?)(?=\n##|\Z)',
            skill_content,
            re.DOTALL
        )
        if match:
            return match.group(1).strip()
        return None

    def parse_json_response(self, response: str) -> Optional[Dict]:
        """Parse JSON from LLM response."""
        # Try to find JSON block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response

        try:
            # Clean up common issues
            json_str = json_str.strip()
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # Remove trailing commas
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    def log(self, message: str, state: AgentState):
        """Log a message to the state."""
        state.add_message(self.name, message)
        print(f"[{self.name}] {message}")

    def set_error(self, error: str, state: AgentState) -> AgentState:
        """Set error state."""
        state.error = error
        state.phase = WorkflowPhase.ERROR
        self.log(f"Error: {error}", state)
        return state
