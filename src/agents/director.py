"""
Director Agent

Handles storyboarding and shot planning.
"""

from typing import Dict, Any, Optional, List
from .base import BaseAgent
from .state import AgentState, WorkflowPhase
from story_generator.models import Shot


class DirectorAgent(BaseAgent):
    """
    Director Agent - Creates storyboards and shot descriptions.

    Skills used:
    - directing/storyboard: Create shot lists and storyboards
    - directing/shot_description: Detailed shot descriptions
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="Director", api_key=api_key)

    def run(self, state: AgentState) -> AgentState:
        """
        Execute directing tasks based on current phase.

        Handles:
        - STORYBOARD: Create storyboard from episodes
        """
        state.current_agent = self.name

        if state.phase == WorkflowPhase.STORYBOARD:
            return self._create_storyboard(state)
        else:
            self.log(f"Unexpected phase: {state.phase}", state)
            return state

    def _create_storyboard(self, state: AgentState) -> AgentState:
        """Create storyboard from episode scripts."""
        self.log("Creating storyboard...", state)

        if not state.episodes:
            return self.set_error("No episodes available for storyboard", state)

        all_shots = []

        try:
            for episode_idx, episode in enumerate(state.episodes):
                episode_shots = self._create_episode_storyboard(
                    state, episode, episode_idx + 1
                )
                all_shots.extend(episode_shots)

            state.storyboard = all_shots

            # Save shots to database
            if state.project_id and state.episodes:
                # Get episode ID from database
                episodes = self.db.get_episodes_by_project(state.project_id)
                episode_id_map = {ep.episode_number: ep.id for ep in episodes}

                for shot in all_shots:
                    episode_num = shot.get('episode_number', 1)
                    episode_id = episode_id_map.get(episode_num)
                    if episode_id:
                        shot_model = Shot(
                            episode_id=episode_id,
                            shot_number=shot.get('shot_number', 1),
                            visual_description=shot.get('visual_description', shot.get('description', '')),
                            duration=int(shot.get('duration', 3)),
                            camera_movement=shot.get('camera_movement', 'static'),
                        )
                        self.db.create_shot(shot_model)

            # Move to video prompts phase
            state.phase = WorkflowPhase.VIDEO_PROMPTS
            state.pending_approval = True
            state.approval_type = "storyboard"
            state.approval_data = {"shots": all_shots}

            self.log(f"Created storyboard with {len(all_shots)} shots", state)

        except Exception as e:
            return self.set_error(f"Failed to create storyboard: {str(e)}", state)

        return state

    def _create_episode_storyboard(
        self,
        state: AgentState,
        episode: Dict[str, Any],
        episode_num: int
    ) -> List[Dict[str, Any]]:
        """Create storyboard for a single episode."""
        self.log(f"Creating storyboard for episode {episode_num}...", state)

        # Prepare episode content
        episode_content = self._format_episode_content(episode)

        # Build character visual reference
        char_visuals = self._build_character_visuals(state.characters)

        variables = {
            "episode_content": episode_content,
            "episode_number": episode_num,
            "duration": state.request.episode_duration if state.request else 60,
            "style": state.request.style if state.request else "cinematic",
        }

        # Use storyboard skill
        response = self.call_llm_with_skill(
            "directing/storyboard",
            variables,
            additional_context=f"角色视觉参考:\n{char_visuals}",
            temperature=0.7
        )

        shots = self.parse_json_response(response)

        if not shots:
            # Try to parse as list of shots
            shots = self._parse_storyboard_text(response, episode_num)
        elif isinstance(shots, dict):
            shots = shots.get("shots", [shots])

        # Add episode reference and enhance each shot
        for i, shot in enumerate(shots):
            shot['episode_number'] = episode_num
            shot['shot_number'] = i + 1

            # Enhance shot description if needed
            if not shot.get('visual_description'):
                shot['visual_description'] = self._enhance_shot_description(
                    state, shot, episode
                )

        return shots

    def _enhance_shot_description(
        self,
        state: AgentState,
        shot: Dict[str, Any],
        episode: Dict[str, Any]
    ) -> str:
        """Enhance shot with detailed visual description."""
        # Build context
        char_visuals = self._build_character_visuals(state.characters)

        prompt = f"""请为以下镜头创建详细的视觉描述,用于生成AI视频。

镜头描述: {shot.get('description', '')}
场景: {shot.get('scene', '')}
角色: {shot.get('characters', [])}

角色视觉参考:
{char_visuals}

请生成一段详细的视觉描述(100-150字),包括:
1. 画面构图
2. 光线和色调
3. 角色姿态和表情
4. 环境细节
5. 镜头运动(如有)

直接输出描述文字,不需要JSON格式。"""

        response = self.call_llm(prompt, temperature=0.6)
        return response.strip()

    def _format_episode_content(self, episode: Dict[str, Any]) -> str:
        """Format episode content for storyboard generation."""
        parts = []

        if episode.get('title'):
            parts.append(f"标题: {episode['title']}")

        if episode.get('synopsis'):
            parts.append(f"摘要: {episode['synopsis']}")

        if episode.get('scenes'):
            parts.append("\n场景:")
            for scene in episode['scenes']:
                scene_text = f"- 场景{scene.get('scene_number', '')}: "
                scene_text += f"{scene.get('location', '')} - {scene.get('description', '')}"
                parts.append(scene_text)

        if episode.get('script'):
            parts.append(f"\n剧本:\n{episode['script'][:2000]}")

        return "\n".join(parts)

    def _build_character_visuals(self, characters: List[Dict[str, Any]]) -> str:
        """Build character visual reference string."""
        if not characters:
            return "无角色信息"

        lines = []
        for char in characters:
            name = char.get('name', 'Unknown')
            visual = char.get('visual_description', char.get('description', ''))
            lines.append(f"- {name}: {visual}")

        return "\n".join(lines)

    def _parse_storyboard_text(
        self,
        text: str,
        episode_num: int
    ) -> List[Dict[str, Any]]:
        """Parse storyboard from plain text when JSON parsing fails."""
        # Simple parsing - split by common markers
        shots = []
        lines = text.split('\n')

        current_shot = None
        shot_num = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect shot markers
            if any(marker in line.lower() for marker in ['shot', '镜头', '场景']):
                if current_shot:
                    shots.append(current_shot)
                shot_num += 1
                current_shot = {
                    'shot_number': shot_num,
                    'episode_number': episode_num,
                    'description': line,
                    'duration': 3.0
                }
            elif current_shot:
                current_shot['description'] += f" {line}"

        if current_shot:
            shots.append(current_shot)

        # If no shots found, create one from the text
        if not shots:
            shots = [{
                'shot_number': 1,
                'episode_number': episode_num,
                'description': text[:500],
                'duration': 5.0
            }]

        return shots
