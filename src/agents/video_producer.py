"""
Video Producer Agent

Handles video prompt generation and video production.
"""

from typing import Dict, Any, Optional, List
from .base import BaseAgent
from .state import AgentState, WorkflowPhase


class VideoProducerAgent(BaseAgent):
    """
    Video Producer Agent - Generates video prompts and manages video production.

    Skills used:
    - video/prompt_generation: Generate platform-optimized prompts
    - video/platforms/kling: Kling-specific prompt guidelines
    - video/platforms/hailuo: Hailuo-specific prompt guidelines
    - video/platforms/jimeng: Jimeng-specific prompt guidelines
    - video/platforms/tongyi: Tongyi-specific prompt guidelines
    """

    # Platform skill mapping
    PLATFORM_SKILLS = {
        "kling": "video/platforms/kling",
        "hailuo": "video/platforms/hailuo",
        "jimeng": "video/platforms/jimeng",
        "tongyi": "video/platforms/tongyi",
    }

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="VideoProducer", api_key=api_key)
        self._providers = {}

    def _get_provider(self, platform: str):
        """Get or create video provider instance."""
        if platform not in self._providers:
            if platform == "kling":
                from providers.kling import KlingProvider
                self._providers[platform] = KlingProvider()
            elif platform == "hailuo":
                from providers.hailuo import HailuoProvider
                self._providers[platform] = HailuoProvider()
            elif platform == "jimeng":
                from providers.jimeng import JimengProvider
                self._providers[platform] = JimengProvider()
            elif platform == "tongyi":
                from providers.tongyi import TongyiProvider
                self._providers[platform] = TongyiProvider()
            else:
                raise ValueError(f"Unknown platform: {platform}")
        return self._providers[platform]

    def run(self, state: AgentState) -> AgentState:
        """
        Execute video production tasks based on current phase.

        Handles:
        - VIDEO_PROMPTS: Generate video prompts for each shot
        - VIDEO_GENERATION: Submit and monitor video generation
        """
        state.current_agent = self.name

        if state.phase == WorkflowPhase.VIDEO_PROMPTS:
            return self._generate_video_prompts(state)
        elif state.phase == WorkflowPhase.VIDEO_GENERATION:
            return self._generate_videos(state)
        else:
            self.log(f"Unexpected phase: {state.phase}", state)
            return state

    def _generate_video_prompts(self, state: AgentState) -> AgentState:
        """Generate video prompts for all shots."""
        self.log("Generating video prompts...", state)

        if not state.storyboard:
            return self.set_error("No storyboard available", state)

        platform = state.request.target_platform if state.request else "kling"
        prompts = {}

        try:
            # Load platform-specific skill
            platform_skill = self.PLATFORM_SKILLS.get(platform, "video/platforms/kling")

            for shot in state.storyboard:
                shot_id = f"ep{shot.get('episode_number', 1)}_shot{shot.get('shot_number', 1)}"
                prompt = self._generate_shot_prompt(state, shot, platform_skill)
                prompts[shot_id] = prompt

                # Update shot in database
                if state.project_id:
                    self._save_prompt_to_db(state, shot, prompt)

            state.video_prompts = prompts

            # Set up for approval
            state.phase = WorkflowPhase.VIDEO_GENERATION
            state.pending_approval = True
            state.approval_type = "video_prompts"
            state.approval_data = {"prompts": prompts, "platform": platform}

            self.log(f"Generated {len(prompts)} video prompts for {platform}", state)

        except Exception as e:
            return self.set_error(f"Failed to generate video prompts: {str(e)}", state)

        return state

    def _is_chinese_input(self, text: str) -> bool:
        """Detect if input contains Chinese characters."""
        return any('\u4e00' <= c <= '\u9fff' for c in text)

    def _generate_shot_prompt(
        self,
        state: AgentState,
        shot: Dict[str, Any],
        platform_skill: str
    ) -> str:
        """Generate optimized prompt for a single shot."""
        # Load platform guidelines
        try:
            platform_guidelines = self.load_skill(platform_skill)
        except Exception:
            platform_guidelines = ""

        # Build context
        visual_desc = shot.get('visual_description', shot.get('description', ''))
        camera_movement = shot.get('camera_movement', '')
        duration = shot.get('duration', 3.0)

        # Get character visuals for consistency
        char_context = self._build_character_context(state.characters, shot)

        # Detect language - video prompts should match content language
        # Most Chinese platforms support Chinese prompts
        platform = state.request.target_platform if state.request else "kling"
        is_chinese = self._is_chinese_input(visual_desc) or self._is_chinese_input(str(state.request.idea) if state.request else "")

        if is_chinese:
            prompt = f"""请为以下镜头生成AI视频生成平台的提示词。

镜头描述: {visual_desc}
镜头时长: {duration}秒
摄像机运动: {camera_movement or '静止'}

角色信息:
{char_context}

平台: {platform}
平台指南:
{platform_guidelines[:1500] if platform_guidelines else '生成详细的视频提示词'}

要求:
1. 使用中文输出提示词
2. 详细描述画面内容、构图、光线、色调
3. 包含摄像机运动描述
4. 描述角色的外貌、动作、表情
5. 适合{duration}秒的视频时长

直接输出提示词，不要有其他解释文字。"""
        else:
            prompt = f"""Generate a video generation prompt for the following shot.

Shot description: {visual_desc}
Duration: {duration} seconds
Camera movement: {camera_movement or 'static'}

Character info:
{char_context}

Platform: {platform}
Platform guidelines:
{platform_guidelines[:1500] if platform_guidelines else 'Generate a detailed video prompt'}

Requirements:
1. Output in English
2. Describe visual content, composition, lighting, color tone
3. Include camera movement
4. Describe character appearance, actions, expressions
5. Suitable for {duration} second video

Output the prompt directly, no additional explanation."""

        response = self.call_llm(prompt, temperature=0.6)
        return response.strip()

    def _generate_videos(self, state: AgentState) -> AgentState:
        """Submit video generation tasks."""
        self.log("Submitting video generation tasks...", state)

        if not state.video_prompts:
            return self.set_error("No video prompts available", state)

        platform = state.request.target_platform if state.request else "kling"

        # Preserve existing tasks when resuming
        video_tasks = dict(state.video_tasks) if state.video_tasks else {}

        try:
            provider = self._get_provider(platform)

            for shot_id, prompt in state.video_prompts.items():
                # Skip already submitted tasks
                if shot_id in video_tasks and video_tasks[shot_id].get("status") == "submitted":
                    self.log(f"Skipping {shot_id} (already submitted)", state)
                    continue

                self.log(f"Submitting {shot_id} to {platform}...", state)

                # Retry logic for SSL errors
                max_retries = 3
                last_error = None
                result = None

                for attempt in range(max_retries):
                    try:
                        if attempt > 0:
                            import time
                            self.log(f"Retry {attempt + 1}/{max_retries} for {shot_id}...", state)
                            time.sleep(2)  # Wait before retry

                        # Submit text-to-video task
                        result = provider.submit_text_to_video(prompt)
                        break  # Success, exit retry loop

                    except Exception as e:
                        last_error = e
                        error_str = str(e).lower()
                        # Only retry on SSL/connection errors
                        if 'ssl' in error_str or 'connection' in error_str or 'timeout' in error_str:
                            continue
                        else:
                            raise  # Non-retryable error

                if result is None and last_error:
                    raise last_error

                # VideoTask is a dataclass, access attributes directly
                video_tasks[shot_id] = {
                    "task_id": result.task_id if result else None,
                    "status": "submitted",
                    "platform": platform,
                    "prompt": prompt,
                }

            state.video_tasks = video_tasks

            # Move to review phase
            state.phase = WorkflowPhase.REVIEW
            state.pending_approval = True
            state.approval_type = "video_tasks"
            state.approval_data = {"tasks": video_tasks}

            self.log(f"Submitted {len(video_tasks)} video generation tasks", state)

        except Exception as e:
            # Save partial progress
            state.video_tasks = video_tasks
            return self.set_error(f"Failed to submit video generation: {str(e)}", state)

        return state

    def check_video_status(self, state: AgentState) -> Dict[str, Dict]:
        """Check status of all video generation tasks."""
        results = {}
        platform = state.request.target_platform if state.request else "kling"

        try:
            provider = self._get_provider(platform)

            for shot_id, task_info in state.video_tasks.items():
                task_id = task_info.get("task_id")
                if task_id:
                    # get_task_status returns a VideoTask object
                    task = provider.get_task_status(task_id)
                    results[shot_id] = {
                        "status": task.status.value if hasattr(task.status, 'value') else str(task.status),
                        "video_url": task.video_url,
                        "error": task.error_message,
                    }

                    # Update task info
                    state.video_tasks[shot_id].update(results[shot_id])

        except Exception as e:
            self.log(f"Error checking video status: {str(e)}", state)

        return results

    def _build_character_context(
        self,
        characters: List[Dict[str, Any]],
        shot: Dict[str, Any]
    ) -> str:
        """Build character context for prompt generation."""
        if not characters:
            return "无角色信息"

        # Get characters mentioned in shot
        shot_chars = shot.get('characters', [])
        relevant_chars = []

        for char in characters:
            char_name = char.get('name', '')
            # Include if mentioned in shot or if no specific chars listed
            if not shot_chars or char_name in str(shot_chars):
                visual = char.get('visual_description', char.get('description', ''))
                relevant_chars.append(f"- {char_name}: {visual}")

        if not relevant_chars:
            relevant_chars = [f"- {c.get('name', 'Unknown')}: {c.get('description', '')}"
                           for c in characters[:3]]

        return "\n".join(relevant_chars)

    def _save_prompt_to_db(
        self,
        state: AgentState,
        shot: Dict[str, Any],
        prompt: str
    ):
        """Save generated prompt to database."""
        try:
            # Find the shot in database
            episode_num = shot.get('episode_number', 1)
            shot_num = shot.get('shot_number', 1)
            platform = state.request.target_platform if state.request else "kling"

            episodes = self.db.get_episodes_by_project(state.project_id)
            for ep in episodes:
                if ep.episode_number == episode_num:
                    episode_full = self.db.get_episode(ep.id)
                    if episode_full:
                        for db_shot in episode_full.shots:
                            if db_shot.shot_number == shot_num:
                                # Update the shot's generated_prompts
                                db_shot.generated_prompts[platform] = prompt
                                self.db.update_shot(db_shot)
                                return
        except Exception as e:
            self.log(f"Warning: Could not save prompt to DB: {str(e)}", state)
