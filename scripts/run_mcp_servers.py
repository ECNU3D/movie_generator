#!/usr/bin/env python3
"""
Run MCP Servers

Usage:
    python scripts/run_mcp_servers.py project    # Run project server
    python scripts/run_mcp_servers.py storyboard # Run storyboard server
    python scripts/run_mcp_servers.py video      # Run video server
    python scripts/run_mcp_servers.py --list     # List available servers
"""

import argparse
import sys
from pathlib import Path

# Add src directory to path
_script_dir = Path(__file__).parent
_project_dir = _script_dir.parent
_src_dir = _project_dir / "src"
sys.path.insert(0, str(_src_dir))


def run_project_server():
    """Run the project MCP server."""
    from mcp_servers.project_server import mcp
    print("Starting Project Server (STDIO mode)...")
    mcp.run(transport="stdio")


def run_storyboard_server():
    """Run the storyboard MCP server."""
    from mcp_servers.storyboard_server import mcp
    print("Starting Storyboard Server (STDIO mode)...")
    mcp.run(transport="stdio")


def run_video_server():
    """Run the video MCP server."""
    from mcp_servers.video_server import mcp
    print("Starting Video Server (STDIO mode)...")
    mcp.run(transport="stdio")


def list_servers():
    """List available servers and their tools."""
    from mcp_servers.project_server import mcp as p_mcp
    from mcp_servers.storyboard_server import mcp as s_mcp
    from mcp_servers.video_server import mcp as v_mcp

    print("Available MCP Servers:")
    print()

    servers = [
        ("project", p_mcp, "Project, Character, Episode CRUD"),
        ("storyboard", s_mcp, "Shot/Storyboard operations"),
        ("video", v_mcp, "Video generation via providers"),
    ]

    for name, server, description in servers:
        tools = list(server._tool_manager._tools.keys())
        print(f"  {name}: {description}")
        print(f"    Tools ({len(tools)}):")
        for tool in sorted(tools):
            print(f"      - {tool}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Run MCP Servers")
    parser.add_argument(
        "server",
        nargs="?",
        choices=["project", "storyboard", "video"],
        help="Server to run"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available servers and tools"
    )

    args = parser.parse_args()

    if args.list:
        list_servers()
        return

    if not args.server:
        parser.print_help()
        return

    server_funcs = {
        "project": run_project_server,
        "storyboard": run_storyboard_server,
        "video": run_video_server,
    }

    server_funcs[args.server]()


if __name__ == "__main__":
    main()
