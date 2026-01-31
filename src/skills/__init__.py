"""
Skills Package

Skills are knowledge/guidance files for Agents. They provide:
- Instructions on how to perform a task
- Available MCP tools to use
- Output format specifications
- Best practices and examples

Skills are NOT:
- Independent LLM calls
- MCP tools (those are in mcp_servers/)
"""

from .loader import SkillLoader, get_skill_loader

__all__ = ["SkillLoader", "get_skill_loader"]
