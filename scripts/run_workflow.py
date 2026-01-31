#!/usr/bin/env python3
"""
Interactive CLI for Multi-Agent Workflow

Provides a command-line interface for:
- Starting new workflows
- Resuming paused sessions
- Managing sessions
- Viewing workflow progress
"""

import os
import sys
import argparse
import json
from typing import Optional

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
)


class WorkflowCLI:
    """Interactive CLI for workflow management."""

    def __init__(self):
        self.runner = PersistentWorkflowRunner()
        self._is_chinese = False  # Will be set based on user input

    def _detect_chinese(self, text: str) -> bool:
        """Detect if text contains Chinese characters."""
        return any('\u4e00' <= c <= '\u9fff' for c in text)

    def _t(self, en: str, zh: str) -> str:
        """Return Chinese or English text based on current mode."""
        return zh if self._is_chinese else en

    def run(self):
        """Run the CLI."""
        parser = argparse.ArgumentParser(
            description="Multi-Agent Video Generation Workflow CLI"
        )
        subparsers = parser.add_subparsers(dest="command", help="Commands")

        # Start command
        start_parser = subparsers.add_parser("start", help="Start a new workflow")
        start_parser.add_argument("idea", help="Story idea")
        start_parser.add_argument("--genre", default="drama", help="Story genre")
        start_parser.add_argument("--style", default="", help="Visual style")
        start_parser.add_argument("--episodes", type=int, default=1, help="Number of episodes")
        start_parser.add_argument("--duration", type=int, default=60, help="Episode duration (seconds)")
        start_parser.add_argument("--characters", type=int, default=3, help="Number of characters")
        start_parser.add_argument("--platform", default="kling", help="Video platform")
        start_parser.add_argument("--auto", action="store_true", help="Run in autonomous mode")

        # Resume command
        resume_parser = subparsers.add_parser("resume", help="Resume a paused session")
        resume_parser.add_argument("session_id", help="Session ID to resume")

        # List command
        list_parser = subparsers.add_parser("list", help="List sessions")
        list_parser.add_argument("--status", help="Filter by status (running, paused, completed, failed)")
        list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of sessions")

        # Info command
        info_parser = subparsers.add_parser("info", help="Get session info")
        info_parser.add_argument("session_id", help="Session ID")

        # View command - view all session content
        view_parser = subparsers.add_parser("view", help="View session content (story, characters, storyboard, etc.)")
        view_parser.add_argument("session_id", help="Session ID")

        # Delete command
        delete_parser = subparsers.add_parser("delete", help="Delete a session")
        delete_parser.add_argument("session_id", help="Session ID to delete")

        # Videos command - check video generation status
        videos_parser = subparsers.add_parser("videos", help="Check video generation status")
        videos_parser.add_argument("session_id", help="Session ID")
        videos_parser.add_argument("--wait", action="store_true", help="Wait for videos to complete")
        videos_parser.add_argument("--download", action="store_true", help="Download completed videos")
        videos_parser.add_argument("--output", "-o", default="./output", help="Output directory for downloads")

        # Interactive command
        interactive_parser = subparsers.add_parser("interactive", help="Start interactive session")
        interactive_parser.add_argument("--session", help="Resume existing session")

        args = parser.parse_args()

        if args.command == "start":
            self.cmd_start(args)
        elif args.command == "resume":
            self.cmd_resume(args)
        elif args.command == "list":
            self.cmd_list(args)
        elif args.command == "info":
            self.cmd_info(args)
        elif args.command == "view":
            self.cmd_view(args)
        elif args.command == "delete":
            self.cmd_delete(args)
        elif args.command == "videos":
            self.cmd_videos(args)
        elif args.command == "interactive":
            self.cmd_interactive(args)
        else:
            parser.print_help()

    def cmd_start(self, args):
        """Start a new workflow."""
        # Detect language from idea
        self._is_chinese = self._detect_chinese(args.idea)

        print(f"\n{'='*60}")
        print(self._t("Starting New Workflow", "开始新工作流"))
        print(f"{'='*60}")
        print(f"{self._t('Idea', '创意')}: {args.idea}")
        print(f"{self._t('Genre', '类型')}: {args.genre}")
        print(f"{self._t('Episodes', '集数')}: {args.episodes}")
        print(f"{self._t('Platform', '平台')}: {args.platform}")
        print()

        mode = InteractionMode.AUTONOMOUS if args.auto else InteractionMode.INTERACTIVE

        try:
            result = self.runner.start(
                idea=args.idea,
                genre=args.genre,
                style=args.style,
                num_episodes=args.episodes,
                episode_duration=args.duration,
                num_characters=args.characters,
                target_platform=args.platform,
                mode=mode,
            )

            self._print_result(result)

            if mode == InteractionMode.INTERACTIVE:
                self._interactive_loop()

        except Exception as e:
            print(f"\n{self._t('Error', '错误')}: {e}")
            return 1

    def cmd_resume(self, args):
        """Resume a paused or failed session."""
        try:
            # Get session info first to detect language
            info = self.runner.get_session_info(args.session_id)
            user_request = info['session'].get('user_request', '')
            self._is_chinese = self._detect_chinese(user_request)

            print(f"\n{'='*60}")
            print(self._t(f"Resuming Session: {args.session_id}", f"恢复会话: {args.session_id}"))
            print(f"{'='*60}\n")

            result = self.runner.resume(args.session_id)

            # Check if resumed from error
            if result.get('resumed_from_error'):
                print(self._t(
                    "Resumed from error state. Retrying...",
                    "从错误状态恢复。正在重试..."
                ))
                print(f"{self._t('Retry count', '重试次数')}: {result['summary'].get('retry_count', 1)}")
                print()

            self._print_result(result)
            self._interactive_loop()

        except Exception as e:
            print(f"\n{self._t('Error', '错误')}: {e}")
            return 1

    def cmd_list(self, args):
        """List sessions."""
        sessions = self.runner.list_sessions(status=args.status, limit=args.limit)

        if not sessions:
            print("\nNo sessions found.")
            return

        print(f"\n{'='*80}")
        print(f"{'ID':<40} {'Status':<12} {'Phase':<20} {'Updated':<20}")
        print(f"{'='*80}")

        for s in sessions:
            session_id = s['session_id'][:36]
            status = s['status']
            phase = s['current_phase']
            updated = s['updated_at'][:19] if s['updated_at'] else ''
            print(f"{session_id:<40} {status:<12} {phase:<20} {updated:<20}")

        print()

    def cmd_info(self, args):
        """Get session info."""
        try:
            info = self.runner.get_session_info(args.session_id)

            print(f"\n{'='*60}")
            print("Session Info")
            print(f"{'='*60}")

            session = info['session']
            print(f"ID: {session['session_id']}")
            print(f"Status: {session['status']}")
            print(f"Phase: {session['current_phase']}")
            print(f"Request: {session['user_request']}")
            print(f"Project ID: {session.get('project_id')}")
            print(f"Created: {session['created_at']}")
            print(f"Updated: {session['updated_at']}")

            if session.get('error_message'):
                print(f"Error: {session['error_message']}")

            checkpoints = info['checkpoints']
            if checkpoints:
                print(f"\nCheckpoints ({len(checkpoints)}):")
                for cp in checkpoints:
                    print(f"  - {cp['step_name']} @ {cp['phase']} ({cp['created_at'][:19]})")

            print()

        except Exception as e:
            print(f"\nError: {e}")
            return 1

    def cmd_view(self, args):
        """View all session content interactively."""
        try:
            # Load session info
            info = self.runner.get_session_info(args.session_id)
            session = info['session']
            user_request = session.get('user_request', '')
            self._is_chinese = self._detect_chinese(user_request)

            # Load full state
            from agents import SessionManager
            manager = SessionManager()
            state = manager.load_state(args.session_id)

            if not state:
                print(self._t("Session not found or no state available", "会话未找到或无状态"))
                return 1

            project_name = state.project_name or self._t("Unnamed Project", "未命名项目")

            print(f"\n{'='*60}")
            print(f"{self._t('Project', '项目')}: {project_name}")
            print(f"{self._t('Status', '状态')}: {session['status']}")
            print(f"{self._t('Phase', '阶段')}: {session['current_phase']}")
            print(f"{'='*60}")

            # Interactive menu
            while True:
                print(f"\n{self._t('View Options', '查看选项')}:")
                print(f"  [1] {self._t('Story Outline', '故事大纲')}")
                print(f"  [2] {self._t('Characters', '角色')} ({len(state.characters)})")
                print(f"  [3] {self._t('Episodes', '剧集')} ({len(state.episodes)})")
                print(f"  [4] {self._t('Storyboard', '分镜')} ({len(state.storyboard)})")
                print(f"  [5] {self._t('Video Prompts', '视频提示词')} ({len(state.video_prompts)})")
                print(f"  [6] {self._t('Video Tasks', '视频任务')} ({len(state.video_tasks)})")
                print(f"  [0] {self._t('Exit', '退出')}")

                choice = input(f"\n{self._t('Select option', '选择选项')}: ").strip()

                if choice == '0' or choice.lower() in ('q', 'quit', 'exit', '退出'):
                    break
                elif choice == '1':
                    self._view_story_outline(state)
                elif choice == '2':
                    self._view_characters(state)
                elif choice == '3':
                    self._view_episodes(state)
                elif choice == '4':
                    self._view_storyboard(state)
                elif choice == '5':
                    self._view_video_prompts(state)
                elif choice == '6':
                    self._view_video_tasks(state)
                else:
                    print(self._t("Invalid option", "无效选项"))

        except Exception as e:
            print(f"\n{self._t('Error', '错误')}: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def _view_story_outline(self, state):
        """View story outline."""
        print(f"\n{'='*60}")
        print(self._t("Story Outline", "故事大纲"))
        print(f"{'='*60}")

        outline = state.story_outline
        if not outline:
            print(self._t("No story outline available", "无故事大纲"))
            return

        if isinstance(outline, dict):
            if outline.get('title'):
                print(f"\n{self._t('Title', '标题')}: {outline['title']}")
            if outline.get('synopsis') or outline.get('premise'):
                print(f"\n{self._t('Synopsis', '简介')}:")
                print(f"  {outline.get('synopsis', outline.get('premise', ''))}")
            if outline.get('theme'):
                print(f"\n{self._t('Theme', '主题')}: {outline['theme']}")
            if outline.get('setting'):
                print(f"\n{self._t('Setting', '背景')}: {outline['setting']}")
        else:
            print(outline)

        input(f"\n{self._t('Press Enter to continue...', '按回车继续...')}")

    def _view_characters(self, state):
        """View characters."""
        print(f"\n{'='*60}")
        print(self._t("Characters", "角色"))
        print(f"{'='*60}")

        if not state.characters:
            print(self._t("No characters available", "无角色信息"))
            input(f"\n{self._t('Press Enter to continue...', '按回车继续...')}")
            return

        for i, char in enumerate(state.characters):
            print(f"\n[{i+1}] {char.get('name', 'Unknown')}")
            if char.get('age'):
                print(f"    {self._t('Age', '年龄')}: {char['age']}")
            if char.get('role'):
                print(f"    {self._t('Role', '角色定位')}: {char['role']}")
            if char.get('personality'):
                print(f"    {self._t('Personality', '性格')}: {char['personality']}")
            if char.get('appearance'):
                print(f"    {self._t('Appearance', '外貌')}: {char['appearance']}")
            if char.get('background'):
                print(f"    {self._t('Background', '背景')}: {char['background']}")
            if char.get('visual_description'):
                print(f"    Visual: {char['visual_description']}")

        # Allow viewing specific character
        while True:
            choice = input(f"\n{self._t('Enter number for details (or Enter to go back)', '输入编号查看详情（或按回车返回）')}: ").strip()
            if not choice:
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(state.characters):
                    char = state.characters[idx]
                    print(f"\n{'='*40}")
                    print(f"{char.get('name', 'Unknown')}")
                    print(f"{'='*40}")
                    for key, value in char.items():
                        if value:
                            print(f"{key}: {value}")
                    print(f"{'='*40}")
            except ValueError:
                break

    def _view_episodes(self, state):
        """View episodes."""
        print(f"\n{'='*60}")
        print(self._t("Episodes", "剧集"))
        print(f"{'='*60}")

        if not state.episodes:
            print(self._t("No episodes available", "无剧集信息"))
            input(f"\n{self._t('Press Enter to continue...', '按回车继续...')}")
            return

        for i, ep in enumerate(state.episodes):
            ep_num = ep.get('episode_number', i + 1)
            title = ep.get('title', f"Episode {ep_num}")
            synopsis = ep.get('synopsis', ep.get('outline', ''))[:100]
            print(f"\n[{ep_num}] {title}")
            print(f"    {synopsis}{'...' if len(ep.get('synopsis', ep.get('outline', ''))) > 100 else ''}")

        # Allow viewing specific episode
        while True:
            choice = input(f"\n{self._t('Enter episode number for full script (or Enter to go back)', '输入集数查看完整剧本（或按回车返回）')}: ").strip()
            if not choice:
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(state.episodes):
                    ep = state.episodes[idx]
                    print(f"\n{'='*60}")
                    print(f"{self._t('Episode', '第')} {ep.get('episode_number', idx + 1)} {self._t('', '集')}: {ep.get('title', '')}")
                    print(f"{'='*60}")

                    if ep.get('synopsis') or ep.get('outline'):
                        print(f"\n{self._t('Synopsis', '简介')}:")
                        print(ep.get('synopsis', ep.get('outline', '')))

                    if ep.get('scenes'):
                        print(f"\n{self._t('Scenes', '场景')}:")
                        for scene in ep['scenes']:
                            print(f"\n  --- {self._t('Scene', '场景')} {scene.get('scene_number', '?')} ---")
                            if scene.get('location'):
                                print(f"  {self._t('Location', '地点')}: {scene['location']}")
                            if scene.get('description'):
                                print(f"  {scene['description']}")
                            if scene.get('dialogue'):
                                print(f"\n  {self._t('Dialogue', '对话')}:")
                                for line in scene['dialogue']:
                                    print(f"    {line}")

                    if ep.get('script'):
                        print(f"\n{self._t('Full Script', '完整剧本')}:")
                        print(ep['script'])

                    print(f"\n{'='*60}")
            except ValueError:
                break

    def _view_storyboard(self, state):
        """View storyboard."""
        print(f"\n{'='*60}")
        print(self._t("Storyboard", "分镜"))
        print(f"{'='*60}")

        if not state.storyboard:
            print(self._t("No storyboard available", "无分镜信息"))
            input(f"\n{self._t('Press Enter to continue...', '按回车继续...')}")
            return

        for shot in state.storyboard:
            ep_num = shot.get('episode_number', 1)
            shot_num = shot.get('shot_number', '?')
            duration = shot.get('duration', '?')
            desc = shot.get('visual_description', shot.get('description', ''))[:60]
            camera = shot.get('camera_movement', '')

            print(f"\n  [{ep_num}-{shot_num}] ({duration}s) {desc}{'...' if len(shot.get('visual_description', shot.get('description', ''))) > 60 else ''}")
            if camera:
                print(f"         {self._t('Camera', '镜头')}: {camera}")

        # Allow viewing specific shot
        while True:
            choice = input(f"\n{self._t('Enter shot number for details (or Enter to go back)', '输入镜头编号查看详情（或按回车返回）')}: ").strip()
            if not choice:
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(state.storyboard):
                    shot = state.storyboard[idx]
                    print(f"\n{'='*40}")
                    print(f"{self._t('Shot', '镜头')} {shot.get('shot_number', idx + 1)}")
                    print(f"{'='*40}")
                    print(f"{self._t('Duration', '时长')}: {shot.get('duration', '?')}s")
                    print(f"{self._t('Camera', '镜头运动')}: {shot.get('camera_movement', 'N/A')}")
                    print(f"\n{self._t('Visual Description', '视觉描述')}:")
                    print(shot.get('visual_description', shot.get('description', 'N/A')))
                    if shot.get('characters'):
                        print(f"\n{self._t('Characters', '角色')}: {shot['characters']}")
                    if shot.get('dialogue'):
                        print(f"\n{self._t('Dialogue', '对话')}: {shot['dialogue']}")
                    print(f"{'='*40}")
            except ValueError:
                break

    def _view_video_prompts(self, state):
        """View video prompts."""
        print(f"\n{'='*60}")
        print(self._t("Video Prompts", "视频提示词"))
        print(f"{'='*60}")

        if not state.video_prompts:
            print(self._t("No video prompts available", "无视频提示词"))
            input(f"\n{self._t('Press Enter to continue...', '按回车继续...')}")
            return

        items = list(state.video_prompts.items())
        for i, (shot_id, prompt) in enumerate(items):
            preview = prompt[:80].replace('\n', ' ')
            print(f"\n  [{i+1}] {shot_id}")
            print(f"      {preview}{'...' if len(prompt) > 80 else ''}")

        # Allow viewing specific prompt
        while True:
            choice = input(f"\n{self._t('Enter number for full prompt (or Enter to go back)', '输入编号查看完整提示词（或按回车返回）')}: ").strip()
            if not choice:
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    shot_id, prompt = items[idx]
                    print(f"\n{'='*40}")
                    print(f"{shot_id}")
                    print(f"{'='*40}")
                    print(prompt)
                    print(f"{'='*40}")
            except ValueError:
                break

    def _view_video_tasks(self, state):
        """View video tasks status."""
        print(f"\n{'='*60}")
        print(self._t("Video Tasks", "视频任务"))
        print(f"{'='*60}")

        if not state.video_tasks:
            print(self._t("No video tasks available", "无视频任务"))
            input(f"\n{self._t('Press Enter to continue...', '按回车继续...')}")
            return

        for shot_id, task_info in state.video_tasks.items():
            status = task_info.get('status', 'unknown')
            task_id = task_info.get('task_id', 'N/A')
            platform = task_info.get('platform', 'unknown')
            video_url = task_info.get('video_url', '')

            if status in ['completed', 'success']:
                icon = '✓'
            elif status == 'failed':
                icon = '✗'
            elif status in ['processing', 'pending', 'submitted']:
                icon = '⏳'
            else:
                icon = '?'

            print(f"\n  {icon} {shot_id}")
            print(f"      {self._t('Status', '状态')}: {status}")
            print(f"      {self._t('Platform', '平台')}: {platform}")
            print(f"      Task ID: {task_id[:20]}..." if task_id and len(task_id) > 20 else f"      Task ID: {task_id}")
            if video_url:
                print(f"      URL: {video_url}")
            if task_info.get('error'):
                print(f"      {self._t('Error', '错误')}: {task_info['error']}")

        input(f"\n{self._t('Press Enter to continue...', '按回车继续...')}")

    def cmd_videos(self, args):
        """Check video generation status and get URLs."""
        import time
        import requests
        from pathlib import Path

        try:
            # Load session to detect language
            info = self.runner.get_session_info(args.session_id)
            user_request = info['session'].get('user_request', '')
            self._is_chinese = self._detect_chinese(user_request)

            # Load session state
            from agents import SessionManager, VideoProducerAgent

            manager = SessionManager()
            state = manager.load_state(args.session_id)

            if not state:
                print(self._t("Session not found or no state available", "会话未找到或无状态"))
                return 1

            if not state.video_tasks:
                print(self._t("No video tasks found in this session", "此会话中没有视频任务"))
                return 1

            platform = state.request.target_platform if state.request else "kling"
            project_name = state.project_name or "video_project"

            print(f"\n{'='*60}")
            print(self._t(f"Video Status - {platform}", f"视频状态 - {platform}"))
            print(f"{'='*60}\n")

            # Create video producer to check status
            producer = VideoProducerAgent()

            while True:
                all_complete = True
                has_pending = False

                for shot_id, task_info in state.video_tasks.items():
                    task_id = task_info.get("task_id")
                    current_status = task_info.get("status", "unknown")

                    if task_id and current_status not in ["completed", "success", "failed"]:
                        # Check status from provider
                        try:
                            provider = producer._get_provider(platform)
                            task = provider.get_task_status(task_id)
                            status = task.status.value if hasattr(task.status, 'value') else str(task.status)
                            video_url = task.video_url
                            error = task.error_message

                            state.video_tasks[shot_id].update({
                                "status": status,
                                "video_url": video_url,
                                "error": error,
                            })
                        except Exception as e:
                            status = f"error: {e}"
                            video_url = None
                    else:
                        status = current_status
                        video_url = task_info.get("video_url")

                    # Display status
                    if status in ["completed", "success"]:
                        icon = "✓"
                    elif status == "failed":
                        icon = "✗"
                    elif status in ["processing", "pending", "submitted"]:
                        icon = "⏳"
                        has_pending = True
                        all_complete = False
                    else:
                        icon = "?"
                        all_complete = False

                    print(f"  {icon} {shot_id}: {status}")
                    if video_url:
                        print(f"     URL: {video_url}")
                    if task_info.get("error"):
                        print(f"     {self._t('Error', '错误')}: {task_info['error']}")

                print()

                if all_complete:
                    print(self._t("All videos completed!", "所有视频已完成！"))
                    break

                if not args.wait:
                    if has_pending:
                        print(self._t(
                            "Some videos still processing. Use --wait to wait for completion.",
                            "部分视频仍在处理中。使用 --wait 等待完成。"
                        ))
                    break

                # Wait and check again
                print(self._t("Waiting for videos to complete...", "等待视频完成..."))
                time.sleep(10)
                print()

            # Download videos if requested
            if args.download:
                self._download_videos(state, project_name, args.output)

        except Exception as e:
            print(f"\n{self._t('Error', '错误')}: {e}")
            import traceback
            traceback.print_exc()
            return 1

    def _download_videos(self, state, project_name: str, output_dir: str):
        """Download completed videos."""
        import requests
        from pathlib import Path
        from urllib.parse import urlparse

        # Create output directory
        output_path = Path(output_dir) / self._sanitize_filename(project_name)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(self._t(f"Downloading to: {output_path}", f"下载到: {output_path}"))
        print(f"{'='*60}\n")

        downloaded = 0
        failed = 0

        for shot_id, task_info in state.video_tasks.items():
            video_url = task_info.get("video_url")
            status = task_info.get("status", "")

            if not video_url:
                if status in ["completed", "success"]:
                    print(f"  ⚠ {shot_id}: {self._t('No URL available', '无可用链接')}")
                continue

            # Determine file extension from URL
            parsed_url = urlparse(video_url)
            url_path = parsed_url.path
            ext = Path(url_path).suffix or ".mp4"

            # Create filename
            filename = f"{shot_id}{ext}"
            filepath = output_path / filename

            # Skip if already downloaded
            if filepath.exists():
                print(f"  ✓ {shot_id}: {self._t('Already exists', '已存在')} - {filepath}")
                downloaded += 1
                continue

            # Download
            print(f"  ⏳ {shot_id}: {self._t('Downloading...', '下载中...')}", end="", flush=True)

            try:
                response = requests.get(video_url, stream=True, timeout=120)
                response.raise_for_status()

                # Get file size if available
                total_size = int(response.headers.get('content-length', 0))

                # Write to file
                with open(filepath, 'wb') as f:
                    if total_size:
                        downloaded_size = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                # Show progress
                                percent = int(downloaded_size * 100 / total_size)
                                print(f"\r  ⏳ {shot_id}: {self._t('Downloading...', '下载中...')} {percent}%", end="", flush=True)
                    else:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)

                print(f"\r  ✓ {shot_id}: {self._t('Downloaded', '已下载')} - {filepath}      ")
                downloaded += 1

            except requests.exceptions.RequestException as e:
                print(f"\r  ✗ {shot_id}: {self._t('Failed', '失败')} - {e}      ")
                failed += 1
            except Exception as e:
                print(f"\r  ✗ {shot_id}: {self._t('Error', '错误')} - {e}      ")
                failed += 1

        print(f"\n{'='*60}")
        print(self._t(
            f"Download complete: {downloaded} succeeded, {failed} failed",
            f"下载完成: {downloaded} 成功, {failed} 失败"
        ))
        print(f"{self._t('Output directory', '输出目录')}: {output_path}")
        print(f"{'='*60}")

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename by removing invalid characters."""
        import re
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        # Limit length
        return sanitized[:50]

    def cmd_delete(self, args):
        """Delete a session."""
        confirm = input(f"Delete session {args.session_id}? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

        try:
            self.runner.delete_session(args.session_id)
            print("Session deleted.")
        except Exception as e:
            print(f"\nError: {e}")
            return 1

    def cmd_interactive(self, args):
        """Start interactive mode."""
        print(f"\n{'='*60}")
        print("Multi-Agent Video Generation - Interactive Mode")
        print(f"{'='*60}")
        print("\nCommands:")
        print("  new      - Start a new workflow")
        print("  resume   - Resume a paused session")
        print("  list     - List sessions")
        print("  info     - Get session info")
        print("  quit     - Exit")
        print()

        if args.session:
            try:
                result = self.runner.resume(args.session)
                self._print_result(result)
                self._interactive_loop()
            except Exception as e:
                print(f"Error resuming session: {e}")

        while True:
            try:
                cmd = input("\n> ").strip().lower()

                if cmd == "quit" or cmd == "exit":
                    print("Goodbye!")
                    break

                elif cmd == "new":
                    idea = input("Story idea: ").strip()
                    if not idea:
                        print("Idea cannot be empty.")
                        continue

                    genre = input("Genre [drama]: ").strip() or "drama"
                    episodes = input("Episodes [1]: ").strip() or "1"
                    platform = input("Platform [kling]: ").strip() or "kling"

                    result = self.runner.start(
                        idea=idea,
                        genre=genre,
                        num_episodes=int(episodes),
                        target_platform=platform,
                    )
                    self._print_result(result)
                    self._interactive_loop()

                elif cmd == "resume":
                    session_id = input("Session ID: ").strip()
                    if session_id:
                        result = self.runner.resume(session_id)
                        self._print_result(result)
                        self._interactive_loop()

                elif cmd == "list":
                    sessions = self.runner.list_sessions(limit=10)
                    if not sessions:
                        print("No sessions found.")
                    else:
                        for s in sessions:
                            print(f"  {s['session_id'][:8]}... | {s['status']:<10} | {s['current_phase']}")

                elif cmd == "info":
                    session_id = input("Session ID: ").strip()
                    if session_id:
                        info = self.runner.get_session_info(session_id)
                        print(json.dumps(info['session'], indent=2))

                elif cmd == "help":
                    print("Commands: new, resume, list, info, quit")

                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'quit' to exit.")
            except Exception as e:
                print(f"Error: {e}")

    def _interactive_loop(self):
        """Run the interactive approval loop."""
        # Phase name translations
        phase_names = {
            "story_outline": self._t("Story Outline", "故事大纲"),
            "character_design": self._t("Character Design", "角色设计"),
            "characters": self._t("Characters", "角色"),
            "episodes": self._t("Episodes", "剧集"),
            "storyboard": self._t("Storyboard", "分镜"),
            "video_prompts": self._t("Video Prompts", "视频提示词"),
            "video_generation": self._t("Video Generation", "视频生成"),
            "completed": self._t("Completed", "已完成"),
        }

        while True:
            summary = self.runner.get_summary()

            if summary.get("error"):
                print(f"\n{self._t('Workflow failed', '工作流失败')}: {summary['error']}")
                print(f"\n{self._t('To resume this session later, use', '稍后恢复此会话，使用')}:")
                print(f"  python scripts/run_workflow.py resume {summary.get('session_id', 'N/A')}")
                break

            phase = summary.get("phase")
            if phase == "completed":
                print("\n" + "="*60)
                print(self._t("Workflow Completed!", "工作流已完成！"))
                print("="*60)
                self._print_summary(summary)
                break

            if not summary.get("pending_approval"):
                # Continue running
                continue

            # Show approval checkpoint
            approval_type = summary.get('approval_type', 'unknown')
            checkpoint_name = phase_names.get(approval_type, approval_type)
            print("\n" + "-"*60)
            print(f"{self._t('Checkpoint', '检查点')}: {checkpoint_name}")
            print("-"*60)
            self._print_summary(summary)
            self._print_approval_data()

            # Get user input
            while True:
                if self._is_chinese:
                    prompt = "\n[A]通过 / [R]拒绝 / [V]查看详情 / [Q]暂停: "
                else:
                    prompt = "\n[A]pprove / [R]eject / [V]iew details / [Q]uit: "
                action = input(prompt).strip().lower()

                if action in ('a', 'approve', 'ok', 'y', 'yes', '', '通过'):
                    print(f"\n{self._t('Continuing workflow...', '继续工作流...')}")
                    result = self.runner.approve_and_continue(approved=True)
                    self._print_result(result)
                    break

                elif action in ('r', 'reject', 'n', 'no', '拒绝'):
                    feedback = input(self._t("Feedback (optional): ", "反馈（可选）：")).strip()
                    result = self.runner.approve_and_continue(approved=False, feedback=feedback)
                    print(f"\n{self._t('Workflow stopped', '工作流已停止')}: {result['summary'].get('error')}")
                    return

                elif action in ('v', 'view', 'd', 'details', '查看'):
                    self._print_approval_data(detailed=True)

                elif action in ('q', 'quit', '暂停'):
                    print(f"\n{self._t('Workflow paused. Use resume to continue later.', '工作流已暂停。稍后使用 resume 继续。')}")
                    print(f"{self._t('Session ID', '会话ID')}: {summary.get('session_id')}")
                    return

                else:
                    print("Invalid input. Use A/R/V/Q.")

    def _print_result(self, result: dict):
        """Print workflow result."""
        summary = result.get("summary", {})
        self._print_summary(summary)

    def _print_summary(self, summary: dict):
        """Print workflow summary."""
        phase_names = {
            "init": self._t("Init", "初始化"),
            "story_outline": self._t("Story Outline", "故事大纲"),
            "character_design": self._t("Character Design", "角色设计"),
            "storyboard": self._t("Storyboard", "分镜"),
            "video_prompts": self._t("Video Prompts", "视频提示词"),
            "video_generation": self._t("Video Generation", "视频生成"),
            "review": self._t("Review", "审核"),
            "completed": self._t("Completed", "已完成"),
            "error": self._t("Error", "错误"),
        }
        phase = summary.get('phase', 'unknown')
        phase_display = phase_names.get(phase, phase)

        print(f"\n{self._t('Phase', '阶段')}: {phase_display}")
        print(f"{self._t('Project', '项目')}: {summary.get('project_name', 'N/A')}")

        if summary.get('num_characters'):
            print(f"{self._t('Characters', '角色数')}: {summary['num_characters']}")
        if summary.get('num_episodes'):
            print(f"{self._t('Episodes', '剧集数')}: {summary['num_episodes']}")
        if summary.get('num_shots'):
            print(f"{self._t('Shots', '镜头数')}: {summary['num_shots']}")
        if summary.get('num_prompts'):
            print(f"{self._t('Video Prompts', '视频提示词')}: {summary['num_prompts']}")

    def _print_approval_data(self, detailed: bool = False):
        """Print approval data."""
        state = self.runner.get_state()
        if not state:
            return

        approval_type = state.get("approval_type", "")
        approval_data = state.get("approval_data", {})

        if approval_type == "story_outline":
            outline = state.get("story_outline", {})
            print(f"\n{self._t('Title', '标题')}: {outline.get('title', 'N/A')}")
            if detailed:
                print(f"{self._t('Synopsis', '简介')}: {outline.get('synopsis', outline.get('premise', 'N/A'))[:500]}")
                if outline.get('theme'):
                    print(f"{self._t('Theme', '主题')}: {outline['theme']}")

        elif approval_type == "characters":
            characters = state.get("characters", [])
            print(f"\n{self._t('Characters', '角色')} ({len(characters)}):")
            for i, char in enumerate(characters):
                name = char.get('name', 'Unknown')
                age = char.get('age', '')
                role = char.get('role', '')

                header = f"  [{i+1}] {name}"
                if age:
                    header += f" ({age})"
                if role:
                    header += f" - {role}"
                print(header)

                if detailed:
                    personality = char.get('personality', '')
                    if personality:
                        print(f"      {self._t('Personality', '性格')}: {personality}")
                    appearance = char.get('appearance', '')
                    if appearance:
                        print(f"      {self._t('Appearance', '外貌')}: {appearance}")
                    background = char.get('background', '')
                    if background:
                        print(f"      {self._t('Background', '背景')}: {background}")
                    visual = char.get('visual_description', '')
                    if visual:
                        print(f"      Visual: {visual}")
                else:
                    personality = char.get('personality', char.get('background', ''))[:60]
                    if personality:
                        print(f"      {personality}{'...' if len(char.get('personality', char.get('background', ''))) > 60 else ''}")

        elif approval_type == "episodes":
            episodes = state.get("episodes", [])
            print(f"\n{self._t('Episodes', '剧集')} ({len(episodes)}):")
            for ep in episodes:
                ep_num = ep.get('episode_number', '?')
                title = ep.get('title', self._t(f"Episode {ep_num}", f"第{ep_num}集"))
                synopsis = ep.get('synopsis', ep.get('outline', ''))
                print(f"\n  [{ep_num}] {title}")
                if detailed:
                    # Show full synopsis
                    print(f"      {synopsis}")
                    # Show scenes if available
                    scenes = ep.get('scenes', [])
                    if scenes:
                        print(f"      {self._t('Scenes', '场景')} ({len(scenes)}):")
                        for scene in scenes[:5]:
                            scene_num = scene.get('scene_number', '?')
                            location = scene.get('location', '')
                            desc = scene.get('description', '')[:60]
                            print(f"        {self._t('Scene', '场景')} {scene_num}: {location} - {desc}")
                else:
                    print(f"      {synopsis[:100]}{'...' if len(synopsis) > 100 else ''}")

        elif approval_type == "storyboard":
            shots = state.get("storyboard", [])
            print(f"\n{self._t('Storyboard', '分镜')} ({len(shots)} {self._t('shots', '镜头')}):")
            if detailed:
                # Show all shots
                for shot in shots:
                    shot_num = shot.get('shot_number', '?')
                    ep_num = shot.get('episode_number', 1)
                    desc = shot.get('visual_description', shot.get('description', ''))[:80]
                    duration = shot.get('duration', '?')
                    camera = shot.get('camera_movement', '')
                    print(f"  [{ep_num}-{shot_num}] ({duration}s) {desc}")
                    if camera:
                        print(f"         {self._t('Camera', '镜头运动')}: {camera}")

                # Allow viewing full description
                while True:
                    choice = input(f"\n{self._t('Enter shot number to view full description (or Enter to continue)', '输入镜头编号查看完整描述（或按回车继续）')}: ").strip()
                    if not choice:
                        break
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(shots):
                            shot = shots[idx]
                            print(f"\n--- {self._t('Shot', '镜头')} {shot.get('shot_number', '?')} ---")
                            print(f"{self._t('Duration', '时长')}: {shot.get('duration', '?')}s")
                            print(f"{self._t('Camera', '镜头运动')}: {shot.get('camera_movement', 'N/A')}")
                            print(f"{self._t('Description', '描述')}:")
                            print(shot.get('visual_description', shot.get('description', 'N/A')))
                            print("-" * 40)
                    except ValueError:
                        break
            else:
                # Brief view - show first few
                for shot in shots[:3]:
                    shot_num = shot.get('shot_number', '?')
                    desc = shot.get('visual_description', shot.get('description', ''))[:60]
                    print(f"  {self._t('Shot', '镜头')} {shot_num}: {desc}...")
                if len(shots) > 3:
                    print(f"  ... {self._t('and', '及')} {len(shots) - 3} {self._t('more shots', '个更多镜头')}")

        elif approval_type == "video_prompts":
            prompts = state.get("video_prompts", {})
            print(f"\n{self._t('Video Prompts', '视频提示词')} ({len(prompts)}):")
            if detailed:
                # Show all prompts with pagination
                items = list(prompts.items())
                for i, (shot_id, prompt) in enumerate(items):
                    # Truncate long prompts
                    prompt_preview = prompt[:100].replace('\n', ' ')
                    print(f"  [{i+1}] {shot_id}: {prompt_preview}...")

                # Allow viewing full prompt
                while True:
                    choice = input(f"\n{self._t('Enter number to view full prompt (or Enter to continue)', '输入编号查看完整提示词（或按回车继续）')}: ").strip()
                    if not choice:
                        break
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(items):
                            shot_id, prompt = items[idx]
                            print(f"\n--- {shot_id} ---")
                            print(prompt)
                            print("-" * 40)
                    except ValueError:
                        break
            else:
                # Brief view - show count only
                pass


def main():
    cli = WorkflowCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main() or 0)
