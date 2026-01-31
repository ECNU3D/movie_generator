"""
Story Writer Agent

Handles story creation: outline, characters, and episodes.
"""

from typing import Dict, Any, Optional
from .base import BaseAgent
from .state import AgentState, WorkflowPhase
from story_generator.models import Project, Character, Episode


class StoryWriterAgent(BaseAgent):
    """
    Story Writer Agent - Creates story outlines, characters, and episodes.

    Skills used:
    - writing/random_idea: Generate creative ideas
    - writing/story_outline: Create story structure
    - writing/consistency_check: Validate story consistency
    - character/character_events: Design character arcs
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(name="StoryWriter", api_key=api_key)

    def run(self, state: AgentState) -> AgentState:
        """
        Execute story writing based on current phase.

        Handles:
        - INIT -> STORY_OUTLINE: Generate initial story outline
        - STORY_OUTLINE -> CHARACTER_DESIGN: Create characters
        - CHARACTER_DESIGN -> EPISODE_WRITING: Write episodes
        """
        state.current_agent = self.name

        if state.phase == WorkflowPhase.INIT:
            return self._generate_story_outline(state)
        elif state.phase == WorkflowPhase.STORY_OUTLINE:
            return self._design_characters(state)
        elif state.phase == WorkflowPhase.CHARACTER_DESIGN:
            return self._write_episodes(state)
        else:
            # Phase not handled by this agent - just return state unchanged
            return state

    def _is_chinese_input(self, text: str) -> bool:
        """Detect if input contains Chinese characters."""
        return any('\u4e00' <= c <= '\u9fff' for c in text)

    def _generate_story_outline(self, state: AgentState) -> AgentState:
        """Generate story outline from user request."""
        self.log("Generating story outline...", state)

        if not state.request:
            return self.set_error("No user request provided", state)

        # Detect language
        is_chinese = self._is_chinese_input(state.request.idea)

        try:
            # Build prompt directly with language instruction
            if is_chinese:
                prompt = f"""你是一位专业的编剧和故事策划师。请根据以下信息创作一个完整的故事大纲。

【创作要求】
故事创意: {state.request.idea}
故事类型: {state.request.genre}
风格描述: {state.request.style or '电影感'}
集数: {state.request.num_episodes}集
每集时长: 约{state.request.episode_duration}秒
主要人物数量: {state.request.num_characters}个

【语言要求】
- 所有内容必须使用中文输出，包括标题、简介、角色名等
- 只有 visual_description 字段使用英文

【输出格式】
请以JSON格式输出，不要有其他解释文字：
```json
{{
    "title": "中文故事标题",
    "synopsis": "中文故事简介（200字以内）",
    "theme": "中文核心主题",
    "premise": "中文故事前提",
    "characters": [
        {{
            "name": "中文角色名",
            "age": "年龄",
            "appearance": "中文外貌描述",
            "personality": "中文性格特点",
            "background": "中文背景故事",
            "visual_description": "English visual description for AI video"
        }}
    ],
    "episodes": [
        {{
            "episode_number": 1,
            "title": "中文本集标题",
            "outline": "中文剧情大纲"
        }}
    ]
}}
```"""
            else:
                prompt = f"""You are a professional screenwriter. Create a complete story outline based on the following:

【Requirements】
Story Idea: {state.request.idea}
Genre: {state.request.genre}
Style: {state.request.style or 'cinematic'}
Episodes: {state.request.num_episodes}
Duration per episode: ~{state.request.episode_duration} seconds
Main characters: {state.request.num_characters}

Output JSON format only:
```json
{{
    "title": "Story title",
    "synopsis": "Story synopsis (under 200 words)",
    "theme": "Core theme",
    "premise": "Story premise",
    "characters": [...],
    "episodes": [...]
}}
```"""

            response = self.call_llm(prompt, temperature=0.8)

            # Parse response
            outline = self.parse_json_response(response)
            if not outline:
                # Try to extract key information even without JSON
                outline = self._parse_outline_text(response, state.request)

            state.story_outline = outline
            state.project_name = outline.get("title", f"Project_{state.request.idea[:20]}")

            # Save to database
            project = Project(
                name=state.project_name,
                description=outline.get("premise", state.request.idea),
                genre=state.request.genre,
                style=state.request.style or "",
                num_episodes=state.request.num_episodes,
                episode_duration=state.request.episode_duration,
            )
            project_id = self.db.create_project(project)
            state.project_id = project_id

            # Set up for approval checkpoint
            state.phase = WorkflowPhase.STORY_OUTLINE
            state.pending_approval = True
            state.approval_type = "story_outline"
            state.approval_data = outline

            self.log(f"Story outline generated: {state.project_name}", state)

        except Exception as e:
            return self.set_error(f"Failed to generate story outline: {str(e)}", state)

        return state

    def _design_characters(self, state: AgentState) -> AgentState:
        """Design characters based on story outline."""
        self.log("Designing characters...", state)

        if not state.story_outline:
            return self.set_error("No story outline available", state)

        # Extract character hints from outline
        outline_summary = self._summarize_outline(state.story_outline)
        num_characters = state.request.num_characters if state.request else 3
        genre = state.request.genre if state.request else "drama"

        try:
            # Detect if input is Chinese
            is_chinese = any('\u4e00' <= c <= '\u9fff' for c in outline_summary)

            # Build a direct prompt for character design
            if is_chinese:
                name_instruction = "使用中文姓名"
                lang_note = "所有描述使用中文"
            else:
                name_instruction = "Use appropriate names for the story setting"
                lang_note = "Descriptions in the story's language"

            prompt = f"""请根据以下故事大纲设计{num_characters}个主要角色。

【故事大纲】
{outline_summary}

【故事类型】
{genre}

【设计要求】
1. 每个角色需要有独特的外貌、性格和背景
2. 角色之间应有明确的关系
3. 角色设定应符合{genre}类型的特点
4. {name_instruction}
5. {lang_note}
6. visual_description必须是英文，用于AI视频生成

请以JSON格式输出，不要有其他解释文字：
```json
{{
    "characters": [
        {{
            "name": "角色姓名",
            "age": "年龄",
            "appearance": "外貌描述",
            "personality": "性格特点",
            "background": "背景故事",
            "role": "角色定位",
            "visual_description": "English visual description for AI video generation"
        }}
    ]
}}
```"""

            response = self.call_llm(prompt, temperature=0.7)

            characters = self.parse_json_response(response)
            if not characters:
                characters = self._parse_characters_text(response)

            # Ensure it's a list
            if isinstance(characters, dict):
                characters = characters.get("characters", [characters])

            state.characters = characters

            # Save characters to database
            if state.project_id:
                for char in characters:
                    character = Character(
                        project_id=state.project_id,
                        name=char.get("name", "Unknown"),
                        appearance=char.get("appearance", char.get("visual_description", "")),
                        personality=char.get("personality", ""),
                        background=char.get("background", char.get("description", "")),
                        visual_description=char.get("visual_description", ""),
                    )
                    self.db.create_character(character)

            # Set up for approval
            state.phase = WorkflowPhase.CHARACTER_DESIGN
            state.pending_approval = True
            state.approval_type = "characters"
            state.approval_data = {"characters": characters}

            self.log(f"Designed {len(characters)} characters", state)

        except Exception as e:
            return self.set_error(f"Failed to design characters: {str(e)}", state)

        return state

    def _write_episodes(self, state: AgentState) -> AgentState:
        """Write episode content."""
        self.log("Writing episodes...", state)

        if not state.story_outline:
            return self.set_error("No story outline available", state)

        num_episodes = state.request.num_episodes if state.request else 1
        episodes = []

        try:
            for i in range(num_episodes):
                episode = self._write_single_episode(state, i + 1)
                if episode:
                    episodes.append(episode)

                    # Save to database
                    if state.project_id:
                        ep = Episode(
                            project_id=state.project_id,
                            episode_number=i + 1,
                            title=episode.get("title", f"Episode {i + 1}"),
                            outline=episode.get("synopsis", episode.get("outline", "")),
                            duration=state.request.episode_duration if state.request else 60,
                        )
                        self.db.create_episode(ep)

            state.episodes = episodes

            # Move to storyboard phase (Director's turn)
            state.phase = WorkflowPhase.STORYBOARD
            state.pending_approval = True
            state.approval_type = "episodes"
            state.approval_data = {"episodes": episodes}

            self.log(f"Wrote {len(episodes)} episodes", state)

        except Exception as e:
            return self.set_error(f"Failed to write episodes: {str(e)}", state)

        return state

    def _write_single_episode(self, state: AgentState, episode_num: int) -> Dict[str, Any]:
        """Write a single episode."""
        outline = state.story_outline
        characters = state.characters

        # Build character context
        char_context = "\n".join([
            f"- {c.get('name', 'Unknown')}: {c.get('personality', c.get('background', c.get('description', '')))}"
            for c in characters
        ])

        prompt = f"""请为以下故事创作第{episode_num}集的剧本。

故事标题: {outline.get('title', '')}
故事主题: {outline.get('theme', '')}
故事前提: {outline.get('premise', '')}

角色列表:
{char_context}

要求:
1. 每集时长约 {state.request.episode_duration if state.request else 60} 秒
2. 包含完整的开头、发展和结尾
3. 对话和场景描述清晰

请以JSON格式输出:
```json
{{
    "title": "第{episode_num}集标题",
    "synopsis": "简短摘要",
    "scenes": [
        {{
            "scene_number": 1,
            "location": "场景地点",
            "description": "场景描述",
            "dialogue": ["角色A: 对话内容", "角色B: 对话内容"]
        }}
    ],
    "script": "完整剧本文字"
}}
```"""

        response = self.call_llm(prompt, temperature=0.7)
        episode = self.parse_json_response(response)

        if not episode:
            episode = {
                "title": f"Episode {episode_num}",
                "synopsis": response[:500],
                "script": response
            }

        return episode

    def _summarize_outline(self, outline: Dict[str, Any]) -> str:
        """Create a brief summary of the story outline."""
        parts = []
        if outline.get("title"):
            parts.append(f"标题: {outline['title']}")
        if outline.get("premise"):
            parts.append(f"前提: {outline['premise']}")
        if outline.get("theme"):
            parts.append(f"主题: {outline['theme']}")
        if outline.get("setting"):
            parts.append(f"背景: {outline['setting']}")
        return "\n".join(parts)

    def _parse_outline_text(self, text: str, request) -> Dict[str, Any]:
        """Parse outline from plain text when JSON parsing fails."""
        return {
            "title": request.idea[:50] if request else "Untitled",
            "premise": text[:500],
            "theme": request.genre if request else "drama",
            "raw_content": text
        }

    def _parse_characters_text(self, text: str) -> list:
        """Parse characters from plain text when JSON parsing fails."""
        import re

        characters = []

        # Try to find character blocks with names
        # Look for patterns like "1. 林战" or "【林战】" or "林战："
        name_patterns = [
            r'(?:\d+\.\s*)?([^\n:：【】]+?)(?:：|:|\n)',  # "1. 名字：" or "名字："
            r'【([^】]+)】',  # 【名字】
            r'"name"\s*:\s*"([^"]+)"',  # JSON fragments
        ]

        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                name = match.strip()
                if len(name) >= 2 and len(name) <= 20 and not any(c in name for c in ['请', '输出', 'JSON', '角色', '{', '}']):
                    # Check if we already have this character
                    if not any(c.get('name') == name for c in characters):
                        characters.append({
                            "name": name,
                            "appearance": "",
                            "personality": "",
                            "background": "",
                            "visual_description": "",
                        })

        # If we found characters, try to extract more details
        if characters:
            return characters[:5]  # Limit to 5 characters

        # Fallback: create a generic character
        return [{
            "name": "主角",
            "appearance": "待补充",
            "personality": "待补充",
            "background": text[:200] if text else "待补充",
            "visual_description": "Main character",
        }]
