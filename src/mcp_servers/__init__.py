"""
MCP Servers Package

Provides MCP (Model Context Protocol) servers for the multi-agent video generation platform.

Servers:
- project_server: Project, Character, Episode CRUD operations
- storyboard_server: Shot/Storyboard operations
- video_server: Video generation via providers (Kling, Hailuo, Jimeng, Tongyi)
"""

__all__ = [
    "project_server",
    "storyboard_server",
    "video_server",
]
