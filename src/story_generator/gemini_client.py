"""
Gemini API Client

Google Gemini API集成，用于故事生成
使用新版 google-genai SDK
"""

import os
import json
import re
import time
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass

from google import genai
from google.genai import types

from .models import (
    Project, Character, Episode, Shot, MajorEvent,
    SHOT_TYPE_NAMES, CAMERA_MOVEMENT_NAMES, GENRE_NAMES,
    APICallLog, PromptTemplate, PROMPT_TEMPLATE_INFO
)

if TYPE_CHECKING:
    from .database import Database


@dataclass
class GeminiConfig:
    """Gemini配置"""
    api_key: str
    model_name: str = "gemini-3-flash-preview"  # 使用最新的Gemini 3 Flash
    temperature: float = 0.8
    max_output_tokens: int = 8192


class GeminiClient:
    """Gemini API客户端"""

    def __init__(self, config: GeminiConfig, database: Optional["Database"] = None):
        self.config = config
        self.client = genai.Client(api_key=config.api_key)
        self.database = database
        self._current_project_id: Optional[int] = None
        self._current_method_name: str = ""

    def set_context(self, project_id: Optional[int] = None, method_name: str = ""):
        """设置当前上下文（用于日志记录）"""
        self._current_project_id = project_id
        self._current_method_name = method_name

    def _generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        """调用Gemini生成内容，并记录日志"""
        start_time = time.time()
        response_text = ""
        status = "success"
        error_message = ""

        try:
            response = self.client.models.generate_content(
                model=self.config.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature if temperature is not None else self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                ),
            )
            response_text = response.text
        except Exception as e:
            status = "error"
            error_message = str(e)
            raise
        finally:
            # 计算延迟
            latency_ms = int((time.time() - start_time) * 1000)

            # 记录API调用日志
            if self.database:
                try:
                    log = APICallLog(
                        project_id=self._current_project_id,
                        method_name=self._current_method_name,
                        prompt=prompt,
                        response=response_text,
                        latency_ms=latency_ms,
                        status=status,
                        error_message=error_message
                    )
                    self.database.create_api_call_log(log)
                except Exception:
                    pass  # 日志记录失败不影响主流程

        return response_text

    def _get_template(self, name: str) -> Optional[str]:
        """从数据库获取提示词模板"""
        if self.database:
            template = self.database.get_active_prompt_template(name)
            if template:
                return template.template
        return None

    def _get_prompt(self, template_name: str, default_prompt: str, **kwargs) -> str:
        """
        获取提示词，优先从数据库模板获取，否则使用默认值

        Args:
            template_name: 模板名称
            default_prompt: 默认提示词（已包含变量替换）
            **kwargs: 用于模板变量替换的参数

        Returns:
            最终的提示词
        """
        # 尝试从数据库获取模板
        template = self._get_template(template_name)
        if template:
            try:
                # 使用安全的格式化，忽略多余的参数
                return template.format(**kwargs)
            except KeyError as e:
                # 模板变量缺失，回退到默认
                print(f"模板变量缺失 {e}，使用默认提示词")
                return default_prompt
        return default_prompt

    def initialize_default_templates(self) -> int:
        """
        初始化所有默认提示词模板到数据库

        Returns:
            创建的模板数量
        """
        if not self.database:
            return 0

        created_count = 0
        default_templates = self._get_all_default_templates()

        for name, template_data in default_templates.items():
            # 检查是否已存在
            existing = self.database.get_active_prompt_template(name)
            if not existing:
                from .models import PromptTemplate, PROMPT_TEMPLATE_INFO
                info = PROMPT_TEMPLATE_INFO.get(name, {})
                template = PromptTemplate(
                    name=name,
                    description=info.get("description", ""),
                    template=template_data["template"],
                    variables=json.dumps(info.get("variables", []), ensure_ascii=False),
                    version=1,
                    is_active=True
                )
                self.database.create_prompt_template(template)
                created_count += 1

        return created_count

    def _get_all_default_templates(self) -> Dict[str, Dict[str, str]]:
        """获取所有默认模板"""
        return {
            "generate_story_outline": {
                "template": self._get_default_story_outline_template()
            },
            "generate_random_story_idea": {
                "template": self._get_default_random_idea_template()
            },
            "generate_storyboard": {
                "template": self._get_default_storyboard_template()
            },
            "expand_shot_description": {
                "template": self._get_default_expand_shot_template()
            },
            "generate_video_prompt": {
                "template": self._get_default_video_prompt_template()
            },
            "analyze_episode_for_character_events": {
                "template": self._get_default_analyze_events_template()
            },
            "edit_episode_with_instruction": {
                "template": self._get_default_edit_episode_template()
            },
            "analyze_edit_impact": {
                "template": self._get_default_analyze_impact_template()
            },
            "generate_consistency_fix": {
                "template": self._get_default_consistency_fix_template()
            },
            "batch_check_consistency": {
                "template": self._get_default_batch_check_template()
            },
            "platform_guide_kling": {
                "template": self._get_platform_guide("kling")
            },
            "platform_guide_tongyi": {
                "template": self._get_platform_guide("tongyi")
            },
            "platform_guide_jimeng": {
                "template": self._get_platform_guide("jimeng")
            },
            "platform_guide_hailuo": {
                "template": self._get_platform_guide("hailuo")
            },
        }

    def _get_platform_guide(self, platform: str) -> str:
        """获取平台提示词指南"""
        guides = {
            "kling": """【可灵 Kling 提示词风格】
- 支持中英文，推荐使用详细的场景描述
- 支持通过<<<image_1>>>等引用图片
- 格式: [主体] + [动作] + [场景] + [风格] + [镜头]
- 示例: 一位年轻女子在樱花树下微笑，春日午后，柔和的阳光，电影级画质，中景镜头""",

            "tongyi": """【通义万相 Tongyi 提示词风格】
- 支持中文，描述要清晰具体
- 支持多镜头叙事（wan2.6模型）
- 格式: 清晰描述场景、人物、动作、氛围
- 示例: 城市街头，一个穿着白色连衣裙的女孩转身微笑，背景是霓虹灯闪烁的夜景，电影感画面""",

            "jimeng": """【即梦 Jimeng 提示词风格】
- 支持中英文混合
- Pro版支持多镜头叙事
- 格式: 详细的视觉描述 + 风格关键词
- 示例: 镜头1：清晨的山间，云雾缭绕；镜头2：一只白鹤展翅飞过湖面""",

            "hailuo": """【海螺 Hailuo 提示词风格】
- 支持中英文
- 支持运镜指令: [左移], [右移], [推进], [拉远], [上升], [下降], [左摇], [右摇], [固定]等
- 格式: 场景描述 + [运镜指令]
- 示例: 女孩站在海边，望向远方的夕阳 [推进]，海风吹动她的长发 [右摇]"""
        }
        return guides.get(platform, "使用清晰详细的中文描述")

    def _get_default_story_outline_template(self) -> str:
        """故事大纲生成的默认模板"""
        return """你是一位专业的编剧和故事策划师。请根据以下信息创作一个完整的故事大纲。

【创作要求】
故事创意: {idea}
故事类型: {genre_name}
风格描述: {style}
目标受众: {target_audience}
集数: {num_episodes}集
每集时长: 约{episode_duration}秒
主要人物数量: {num_characters}个

【输出要求】
请以JSON格式输出，包含以下内容:

```json
{{
    "title": "故事标题",
    "synopsis": "200字以内的故事简介",
    "theme": "核心主题",
    "characters": [
        {{
            "name": "角色名称",
            "age": "年龄（如：25岁、中年等）",
            "appearance": "外貌描述（100字以内，包括身高、体型、发型、穿着风格等视觉特征）",
            "personality": "性格特点（50字以内）",
            "background": "背景故事（100字以内）",
            "relationships": "与其他角色的关系",
            "visual_description": "用于AI生成图像/视频的视觉描述（英文，50词以内，描述这个角色的典型视觉特征）"
        }}
    ],
    "episodes": [
        {{
            "episode_number": 1,
            "title": "本集标题",
            "outline": "本集剧情大纲（100-200字，描述主要情节发展）",
            "key_events": ["关键事件1", "关键事件2"]
        }}
    ]
}}
```

请确保:
1. 创建**正好{num_characters}个**主要角色，角色之间有明确的关系和互动
2. 每集剧情紧凑，适合{episode_duration}秒的时长
3. 整体故事有清晰的开端、发展、高潮、结局
4. 风格与类型一致
5. visual_description用英文编写，便于后续生成视频"""

    def _get_default_random_idea_template(self) -> str:
        """随机创意生成的默认模板"""
        return """你是一位富有创意的故事策划师。请随机生成一个有趣的短视频故事创意。

{genre_hint}
{style_hint}

要求:
1. 创意新颖，有吸引力
2. 适合制作成短视频系列
3. 有明确的主角和冲突
4. 50-100字的简短描述

直接输出故事创意，不要任何额外说明。"""

    def _get_default_storyboard_template(self) -> str:
        """分镜脚本生成的默认模板"""
        return """你是一位专业的分镜师和导演。请将以下剧集大纲展开为详细的分镜脚本。

【项目信息】
故事名称: {project_name}
故事类型: {genre_name}
风格: {style}

【剧集信息】
第{episode_number}集: {episode_title}
目标时长: {episode_duration}秒
剧情大纲:
{outline}

{character_context}

【分镜要求】
请生成 **约{target_shots}个镜头** 的分镜脚本（最少{min_shots}个，每个镜头最长{max_video_duration}秒）。
每个镜头包含:
- scene_number: 场景编号
- shot_number: 镜头编号（场景内）
- shot_type: 镜头类型 (extreme_wide/wide/full/medium/medium_close/close_up/extreme_close_up/pov/over_shoulder/two_shot)
- duration: 镜头时长（秒，平均约{avg_shot_duration}秒，最长不超过{max_video_duration}秒）
- visual_description: 画面描述（详细描述画面内容、人物动作、表情、环境等）
- dialogue: 对白（如果有）
- sound_music: 音效/配乐提示
- camera_movement: 镜头运动 (static/pan_left/pan_right/tilt_up/tilt_down/zoom_in/zoom_out/dolly_in/dolly_out/tracking/crane_up/crane_down/handheld)
- notes: 其他备注

请以JSON格式输出:
```json
{{
    "shots": [
        {{
            "scene_number": 1,
            "shot_number": 1,
            "shot_type": "wide",
            "duration": 5,
            "visual_description": "画面描述...",
            "dialogue": "对白内容...",
            "sound_music": "背景音乐舒缓，环境音...",
            "camera_movement": "static",
            "notes": ""
        }}
    ],
    "total_duration": {episode_duration}
}}
```

注意:
1. 镜头总时长应接近目标时长{episode_duration}秒
2. 每个镜头时长不得超过{max_video_duration}秒
3. 镜头切换要有节奏感
4. 画面描述要足够详细，便于后续生成视频
5. 保持与人物设定的一致性"""

    def _get_default_expand_shot_template(self) -> str:
        """扩展镜头描述的默认模板"""
        return """请帮助扩展和优化以下镜头的画面描述，使其更加详细和生动。

【当前镜头信息】
场景{scene_number} - 镜头{shot_number}
镜头类型: {shot_type}
时长: {duration}秒
镜头运动: {camera_movement}
当前描述: {visual_description}
对白: {dialogue}

【风格要求】
{style}

{character_context}

请输出优化后的画面描述（200字以内），要求:
1. 更加详细和具体
2. 包含光线、色调、氛围等视觉元素
3. 描述人物的表情、动作细节
4. 保持与整体风格一致

直接输出优化后的描述，不要其他说明。"""

    def _get_default_video_prompt_template(self) -> str:
        """视频提示词生成的默认模板"""
        return """你是一位专业的AI视频生成提示词工程师。请为以下镜头{type_instruction}。

【镜头信息】
画面描述: {visual_description}
对白: {dialogue}
镜头类型: {shot_type}
镜头运动: {camera_movement}
时长: {duration}秒
音效/配乐: {sound_music}

【风格要求】
{style}

{character_context}

{platform_guide}
{camera_hint}
{extra_instruction}

请直接输出优化后的提示词（不超过500字），要求:
1. 符合{platform}平台的提示词风格
2. 描述清晰、具体、有画面感
3. 包含必要的风格和质量关键词

直接输出提示词，不要任何额外说明。"""

    def _get_default_analyze_events_template(self) -> str:
        """分析角色事件的默认模板"""
        return """请分析以下剧集内容，提取各角色经历的重大事件。

【剧集内容】
{content}

【角色列表】
{character_names}

请分析每个角色在本集中是否经历了重大事件（如: 重要决定、情感转折、关系变化、重大发现等）。

以JSON格式输出:
```json
{{
    "events": [
        {{
            "character_name": "角色名",
            "event_description": "事件简述（50字以内）",
            "impact": "对角色的影响（30字以内）"
        }}
    ]
}}
```

只输出确实发生了重大事件的角色，如果某角色本集没有重大经历则不要包含。"""

    def _get_default_edit_episode_template(self) -> str:
        """AI编辑剧集的默认模板"""
        return """你是一位专业的编剧。请根据用户的指令修改以下剧集大纲。

【项目信息】
故事名称: {project_name}
故事类型: {genre_name}
风格: {style}
总集数: {num_episodes}

【当前剧集】
第{episode_number}集
标题: {episode_title}
大纲:
{outline}

{character_context}

【用户修改指令】
{instruction}

请根据指令修改剧集大纲，以JSON格式输出:
```json
{{
    "new_title": "修改后的标题（如果标题需要变化）",
    "new_outline": "修改后的完整大纲",
    "changes_summary": "简要说明做了哪些修改（50字以内）"
}}
```

注意:
1. 仅根据指令进行必要的修改
2. 保持与整体故事风格的一致性
3. 考虑与其他剧集的连贯性"""

    def _get_default_analyze_impact_template(self) -> str:
        """分析编辑影响的默认模板"""
        return """你是一位专业的剧本顾问。请分析以下剧集大纲的修改对其他内容的影响。

【被修改的剧集】
第{episode_number}集 - {episode_title}

【原大纲】
{original_outline}

【新大纲】
{new_outline}

【其他剧集】
{other_episodes_context}

【角色设定】
{characters_context}

请分析这次修改是否会导致以下问题:
1. 与前面剧集的剧情矛盾
2. 与后面剧集的剧情不连贯
3. 与角色设定或经历的矛盾
4. 时间线问题

以JSON格式输出所有发现的问题:
```json
{{
    "issues": [
        {{
            "type": "episode",
            "id": 剧集编号,
            "name": "第X集标题",
            "issue": "问题描述",
            "severity": "warning或error（error=严重矛盾必须修复，warning=建议修复但不影响故事理解）",
            "suggested_fix": "建议如何修改受影响的内容",
            "auto_fixable": true或false,
            "auto_fix_reason": "为什么可以/不可以自动修复"
        }},
        {{
            "type": "character",
            "id": 0,
            "name": "角色名",
            "issue": "问题描述",
            "severity": "warning或error",
            "suggested_fix": "建议如何修改角色设定或经历",
            "auto_fixable": true或false,
            "auto_fix_reason": "为什么可以/不可以自动修复"
        }}
    ]
}}
```

【auto_fixable判断标准】
- true: 问题是简单的事实性错误，可以通过添加/修改少量细节来修复，不影响核心剧情
- false: 问题涉及叙事结构、角色核心设定、或需要创意性重写，应由人工审核

如果没有发现问题，返回空的issues数组。只报告真正存在的问题，不要过度解读。"""

    def _get_default_consistency_fix_template(self) -> str:
        """一致性修复的默认模板"""
        return """你是一位专业的剧本顾问。请修复以下一致性问题。

【项目信息】
故事名称: {project_name}
风格: {style}

【问题类型】
{issue_type}: {target_name}

【问题描述】
{issue_description}

【需要修改的内容】
{original_content}

{character_context}

请生成修复后的内容，以JSON格式输出:
```json
{{
    "fixed_content": "修复后的完整内容",
    "explanation": "简要说明修改了什么（30字以内）"
}}
```

注意:
1. 只做必要的修改来解决问题
2. 保持内容的完整性和连贯性
3. 不要改变核心情节，只修复不一致之处"""

    def _get_default_batch_check_template(self) -> str:
        """全局一致性检查的默认模板"""
        return """你是一位专业的剧本审核专家。请全面检查以下故事的一致性问题。

【项目信息】
故事名称: {project_name}
类型: {genre_name}
风格: {style}

【剧情时间线】
{timeline}

【角色经历时间线】
{character_timelines}

请检查以下方面的一致性问题:
1. 剧情逻辑：前后剧集的因果关系是否合理
2. 角色行为：角色的行为是否符合其设定
3. 时间线：事件发生的顺序是否合理
4. 细节一致：场景、物品、关系等细节是否前后一致

以JSON格式输出所有发现的问题:
```json
{{
    "issues": [
        {{
            "type": "episode或character",
            "id": 相关ID,
            "name": "名称",
            "issue": "问题描述",
            "severity": "warning或error",
            "suggested_fix": "建议的修复方案",
            "auto_fixable": true或false
        }}
    ],
    "overall_assessment": "整体一致性评估（好/一般/需要改进）"
}}
```

如果没有发现问题，返回空的issues数组。只报告真正的问题，不要过度解读。"""

    def _parse_json_response(self, response: str) -> dict:
        """解析JSON响应，处理可能的markdown包装"""
        # 尝试提取JSON块
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = response

        # 清理并解析
        json_str = json_str.strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # 尝试修复常见问题
            # 移除可能的注释
            json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
            # 移除尾部逗号
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            return json.loads(json_str)

    # ==================== 故事生成 ====================

    def generate_story_outline(
        self,
        idea: str,
        genre: str,
        style: str,
        num_episodes: int,
        episode_duration: int,
        target_audience: str = "",
        num_characters: int = 3
    ) -> Dict[str, Any]:
        """
        根据创意生成故事大纲

        返回:
        {
            "title": "故事标题",
            "synopsis": "故事简介",
            "characters": [...],
            "episodes": [...]
        }
        """
        self._current_method_name = "generate_story_outline"
        genre_name = GENRE_NAMES.get(genre, genre)
        target_audience_text = target_audience or "通用观众"

        # 构建默认提示词
        default_prompt = f"""你是一位专业的编剧和故事策划师。请根据以下信息创作一个完整的故事大纲。

【创作要求】
故事创意: {idea}
故事类型: {genre_name}
风格描述: {style}
目标受众: {target_audience_text}
集数: {num_episodes}集
每集时长: 约{episode_duration}秒
主要人物数量: {num_characters}个

【输出要求】
请以JSON格式输出，包含以下内容:

```json
{{
    "title": "故事标题",
    "synopsis": "200字以内的故事简介",
    "theme": "核心主题",
    "characters": [
        {{
            "name": "角色名称",
            "age": "年龄（如：25岁、中年等）",
            "appearance": "外貌描述（100字以内，包括身高、体型、发型、穿着风格等视觉特征）",
            "personality": "性格特点（50字以内）",
            "background": "背景故事（100字以内）",
            "relationships": "与其他角色的关系",
            "visual_description": "用于AI生成图像/视频的视觉描述（英文，50词以内，描述这个角色的典型视觉特征）"
        }}
    ],
    "episodes": [
        {{
            "episode_number": 1,
            "title": "本集标题",
            "outline": "本集剧情大纲（100-200字，描述主要情节发展）",
            "key_events": ["关键事件1", "关键事件2"]
        }}
    ]
}}
```

请确保:
1. 创建**正好{num_characters}个**主要角色，角色之间有明确的关系和互动
2. 每集剧情紧凑，适合{episode_duration}秒的时长
3. 整体故事有清晰的开端、发展、高潮、结局
4. 风格与类型一致
5. visual_description用英文编写，便于后续生成视频"""

        # 尝试使用数据库模板
        prompt = self._get_prompt(
            "generate_story_outline",
            default_prompt,
            idea=idea,
            genre_name=genre_name,
            style=style,
            target_audience=target_audience_text,
            num_episodes=num_episodes,
            episode_duration=episode_duration,
            num_characters=num_characters
        )

        response = self._generate(prompt)
        return self._parse_json_response(response)

    def generate_random_story_idea(self, genre: str = "", style: str = "") -> str:
        """随机生成故事创意"""
        self._current_method_name = "generate_random_story_idea"
        genre_hint = f"类型偏好: {GENRE_NAMES.get(genre, genre)}" if genre else "任意类型"
        style_hint = f"风格偏好: {style}" if style else "任意风格"

        default_prompt = f"""你是一位富有创意的故事策划师。请随机生成一个有趣的短视频故事创意。

{genre_hint}
{style_hint}

要求:
1. 创意新颖，有吸引力
2. 适合制作成短视频系列
3. 有明确的主角和冲突
4. 50-100字的简短描述

直接输出故事创意，不要任何额外说明。"""

        prompt = self._get_prompt(
            "generate_random_story_idea",
            default_prompt,
            genre_hint=genre_hint,
            style_hint=style_hint
        )

        return self._generate(prompt, temperature=1.0).strip()

    # ==================== 分镜脚本生成 ====================

    def generate_storyboard(
        self,
        episode: Episode,
        project: Project,
        character_context: str,
        shot_density: str = "medium",  # low, medium, high, custom
        custom_shot_count: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        将剧集大纲展开为详细的分镜脚本

        Args:
            episode: 剧集信息
            project: 项目信息
            character_context: 人物上下文
            shot_density: 分镜密度 (low/medium/high/custom)
            custom_shot_count: 自定义分镜数量（仅当shot_density为custom时使用）

        返回镜头列表
        """
        self._current_method_name = "generate_storyboard"
        import math

        # 计算分镜数量
        min_shots = math.ceil(episode.duration / project.max_video_duration)

        if shot_density == "low":
            target_shots = min_shots
        elif shot_density == "medium":
            target_shots = int(min_shots * 1.5)
        elif shot_density == "high":
            target_shots = min_shots * 2
        elif shot_density == "custom" and custom_shot_count:
            target_shots = max(min_shots, custom_shot_count)
        else:
            target_shots = int(min_shots * 1.5)  # 默认中等

        # 计算每个镜头的平均时长
        avg_shot_duration = episode.duration / target_shots

        prompt = f"""你是一位专业的分镜师和导演。请将以下剧集大纲展开为详细的分镜脚本。

【项目信息】
故事名称: {project.name}
故事类型: {GENRE_NAMES.get(project.genre, project.genre)}
风格: {project.style}

【剧集信息】
第{episode.episode_number}集: {episode.title}
目标时长: {episode.duration}秒
剧情大纲:
{episode.outline}

{character_context}

【分镜要求】
请生成 **约{target_shots}个镜头** 的分镜脚本（最少{min_shots}个，每个镜头最长{project.max_video_duration}秒）。
每个镜头包含:
- scene_number: 场景编号
- shot_number: 镜头编号（场景内）
- shot_type: 镜头类型 (extreme_wide/wide/full/medium/medium_close/close_up/extreme_close_up/pov/over_shoulder/two_shot)
- duration: 镜头时长（秒，平均约{avg_shot_duration:.1f}秒，最长不超过{project.max_video_duration}秒）
- visual_description: 画面描述（详细描述画面内容、人物动作、表情、环境等）
- dialogue: 对白（如果有）
- sound_music: 音效/配乐提示
- camera_movement: 镜头运动 (static/pan_left/pan_right/tilt_up/tilt_down/zoom_in/zoom_out/dolly_in/dolly_out/tracking/crane_up/crane_down/handheld)
- notes: 其他备注

请以JSON格式输出:
```json
{{
    "shots": [
        {{
            "scene_number": 1,
            "shot_number": 1,
            "shot_type": "wide",
            "duration": 5,
            "visual_description": "画面描述...",
            "dialogue": "对白内容...",
            "sound_music": "背景音乐舒缓，环境音...",
            "camera_movement": "static",
            "notes": ""
        }}
    ],
    "total_duration": {episode.duration}
}}
```

注意:
1. 镜头总时长应接近目标时长{episode.duration}秒
2. 每个镜头时长不得超过{project.max_video_duration}秒
3. 镜头切换要有节奏感
4. 画面描述要足够详细，便于后续生成视频
5. 保持与人物设定的一致性"""

        response = self._generate(prompt)
        data = self._parse_json_response(response)
        return data.get("shots", [])

    def expand_shot_description(
        self,
        shot: Shot,
        episode: Episode,
        character_context: str,
        style: str
    ) -> str:
        """扩展单个镜头的画面描述"""
        self._current_method_name = "expand_shot_description"
        prompt = f"""请帮助扩展和优化以下镜头的画面描述，使其更加详细和生动。

【当前镜头信息】
场景{shot.scene_number} - 镜头{shot.shot_number}
镜头类型: {SHOT_TYPE_NAMES.get(shot.shot_type, shot.shot_type)}
时长: {shot.duration}秒
镜头运动: {CAMERA_MOVEMENT_NAMES.get(shot.camera_movement, shot.camera_movement)}
当前描述: {shot.visual_description}
对白: {shot.dialogue}

【风格要求】
{style}

{character_context}

请输出优化后的画面描述（200字以内），要求:
1. 更加详细和具体
2. 包含光线、色调、氛围等视觉元素
3. 描述人物的表情、动作细节
4. 保持与整体风格一致

直接输出优化后的描述，不要其他说明。"""

        return self._generate(prompt).strip()

    # ==================== 视频提示词生成 ====================

    def generate_video_prompt(
        self,
        shot: Shot,
        platform: str,
        character_context: str,
        style: str,
        prompt_type: str = "t2v"  # t2v, i2v_first, i2v_last, i2v, i2v_fl
    ) -> str:
        """
        为指定平台生成视频提示词

        Args:
            shot: 镜头信息
            platform: 平台 (kling, tongyi, jimeng, hailuo)
            character_context: 人物上下文
            style: 风格描述
            prompt_type: 提示词类型
                - t2v: 文生视频
                - i2v_first: 首帧图片提示词
                - i2v_last: 尾帧图片提示词
                - i2v: 图生视频提示词（仅首帧）
                - i2v_fl: 图生视频提示词（首尾帧）
        """
        self._current_method_name = "generate_video_prompt"

        # 尝试从数据库获取平台指南
        platform_guide_template = self._get_template(f"platform_guide_{platform}")
        if platform_guide_template:
            platform_guide = platform_guide_template
        else:
            # 使用默认的平台指南
            platform_guides = {
                "kling": """【可灵 Kling 提示词风格】
- 支持中英文，推荐使用详细的场景描述
- 支持通过<<<image_1>>>等引用图片
- 格式: [主体] + [动作] + [场景] + [风格] + [镜头]
- 示例: 一位年轻女子在樱花树下微笑，春日午后，柔和的阳光，电影级画质，中景镜头""",

                "tongyi": """【通义万相 Tongyi 提示词风格】
- 支持中文，描述要清晰具体
- 支持多镜头叙事（wan2.6模型）
- 格式: 清晰描述场景、人物、动作、氛围
- 示例: 城市街头，一个穿着白色连衣裙的女孩转身微笑，背景是霓虹灯闪烁的夜景，电影感画面""",

                "jimeng": """【即梦 Jimeng 提示词风格】
- 支持中英文混合
- Pro版支持多镜头叙事
- 格式: 详细的视觉描述 + 风格关键词
- 示例: 镜头1：清晨的山间，云雾缭绕；镜头2：一只白鹤展翅飞过湖面""",

                "hailuo": """【海螺 Hailuo 提示词风格】
- 支持中英文
- 支持运镜指令: [左移], [右移], [推进], [拉远], [上升], [下降], [左摇], [右摇], [固定]等
- 格式: 场景描述 + [运镜指令]
- 示例: 女孩站在海边，望向远方的夕阳 [推进]，海风吹动她的长发 [右摇]"""
            }
            platform_guide = platform_guides.get(platform, "使用清晰详细的中文描述")

        # 镜头运动映射到海螺指令
        hailuo_camera_map = {
            "pan_left": "[左摇]",
            "pan_right": "[右摇]",
            "tilt_up": "[上摇]",
            "tilt_down": "[下摇]",
            "zoom_in": "[推进]",
            "zoom_out": "[拉远]",
            "crane_up": "[上升]",
            "crane_down": "[下降]",
            "tracking": "[跟随]",
            "handheld": "[晃动]",
            "static": "[固定]",
        }

        type_instruction = {
            "t2v": "生成文生视频提示词（描述视频中的动作和场景变化）",
            "i2v_first": "生成首帧图片描述提示词（静态画面，作为视频开始的第一帧）",
            "i2v_last": "生成尾帧图片描述提示词（静态画面，作为视频结束的最后一帧）",
            "i2v": "生成图生视频提示词（配合首帧图片使用，描述从首帧开始的动作和变化）",
            "i2v_fl": "生成首尾帧图生视频提示词（配合首帧和尾帧图片使用，描述两帧之间的过渡动作）"
        }.get(prompt_type, "生成文生视频提示词")

        camera_hint = ""
        if platform == "hailuo" and shot.camera_movement in hailuo_camera_map:
            camera_hint = f"\n注意: 请在提示词中加入运镜指令 {hailuo_camera_map[shot.camera_movement]}"

        # 根据提示词类型添加额外的指导
        extra_instruction = ""
        if prompt_type == "i2v_first":
            extra_instruction = """
【特别注意】
这是首帧图片提示词，需要描述一个静态画面，作为视频的起始帧。
- 描述人物/场景的初始状态和姿态
- 不要描述动作过程，只描述静止的瞬间
- 适合生成图片的详细描述"""
        elif prompt_type == "i2v_last":
            extra_instruction = """
【特别注意】
这是尾帧图片提示词，需要描述一个静态画面，作为视频的结束帧。
- 描述人物/场景的最终状态和姿态
- 要与首帧形成合理的动作结束状态
- 不要描述动作过程，只描述静止的瞬间"""
        elif prompt_type == "i2v":
            extra_instruction = """
【特别注意】
这是图生视频提示词，配合首帧图片使用。
- 假设首帧图片已经提供，描述从首帧开始发生的动作和变化
- 重点描述运动、动作、表情变化等动态元素
- 不需要重复描述首帧的静态内容，专注于"发生什么动作"
- 确保动作与首帧画面自然衔接"""
        elif prompt_type == "i2v_fl":
            extra_instruction = """
【特别注意】
这是首尾帧图生视频提示词，配合首帧和尾帧图片使用。
- 假设首帧和尾帧图片已经提供，描述两帧之间的过渡动作
- 重点描述从首帧状态到尾帧状态的自然过渡
- 描述动作、运动轨迹、情感变化等
- 确保过渡流畅合理，不要描述与首尾帧矛盾的内容"""

        prompt = f"""你是一位专业的AI视频生成提示词工程师。请为以下镜头{type_instruction}。

【镜头信息】
画面描述: {shot.visual_description}
对白: {shot.dialogue}
镜头类型: {SHOT_TYPE_NAMES.get(shot.shot_type, shot.shot_type)}
镜头运动: {CAMERA_MOVEMENT_NAMES.get(shot.camera_movement, shot.camera_movement)}
时长: {shot.duration}秒
音效/配乐: {shot.sound_music}

【风格要求】
{style}

{character_context}

{platform_guide}
{camera_hint}
{extra_instruction}

请直接输出优化后的提示词（不超过500字），要求:
1. 符合{platform}平台的提示词风格
2. 描述清晰、具体、有画面感
3. 包含必要的风格和质量关键词

直接输出提示词，不要任何额外说明。"""

        return self._generate(prompt, temperature=0.7).strip()

    def batch_generate_prompts(
        self,
        shot: Shot,
        platforms: List[str],
        character_context: str,
        style: str,
        prompt_types: List[str] = ["t2v"]
    ) -> Dict[str, str]:
        """
        批量生成多平台的提示词

        Returns:
            {
                "kling_t2v": "提示词...",
                "tongyi_t2v": "提示词...",
                "hailuo_i2v_first": "提示词...",
                ...
            }
        """
        results = {}
        for platform in platforms:
            for prompt_type in prompt_types:
                key = f"{platform}_{prompt_type}"
                results[key] = self.generate_video_prompt(
                    shot=shot,
                    platform=platform,
                    character_context=character_context,
                    style=style,
                    prompt_type=prompt_type
                )
        return results

    # ==================== 人物事件更新 ====================

    def analyze_episode_for_character_events(
        self,
        episode: Episode,
        characters: List[Character]
    ) -> List[Dict[str, Any]]:
        """
        分析剧集，提取各角色的重大经历

        Returns:
            [
                {
                    "character_name": "角色名",
                    "event_description": "事件描述",
                    "impact": "对角色的影响"
                }
            ]
        """
        self._current_method_name = "analyze_episode_for_character_events"
        if not episode.shots:
            return []

        # 构建剧集内容摘要
        content = f"第{episode.episode_number}集: {episode.title}\n\n"
        for shot in episode.shots:
            content += f"[场景{shot.scene_number}-{shot.shot_number}] {shot.visual_description}"
            if shot.dialogue:
                content += f" 对白: {shot.dialogue}"
            content += "\n"

        character_names = [c.name for c in characters]

        prompt = f"""请分析以下剧集内容，提取各角色经历的重大事件。

【剧集内容】
{content}

【角色列表】
{', '.join(character_names)}

请分析每个角色在本集中是否经历了重大事件（如: 重要决定、情感转折、关系变化、重大发现等）。

以JSON格式输出:
```json
{{
    "events": [
        {{
            "character_name": "角色名",
            "event_description": "事件简述（50字以内）",
            "impact": "对角色的影响（30字以内）"
        }}
    ]
}}
```

只输出确实发生了重大事件的角色，如果某角色本集没有重大经历则不要包含。"""

        response = self._generate(prompt, temperature=0.5)
        data = self._parse_json_response(response)
        return data.get("events", [])

    # ==================== AI编辑和一致性检查 ====================

    def edit_episode_with_instruction(
        self,
        episode: Episode,
        project: Project,
        instruction: str,
        character_context: str
    ) -> Dict[str, Any]:
        """
        根据用户指令AI编辑剧集大纲

        Returns:
            {
                "new_outline": "修改后的大纲",
                "new_title": "修改后的标题（如果需要）",
                "changes_summary": "修改摘要"
            }
        """
        self._current_method_name = "edit_episode_with_instruction"
        prompt = f"""你是一位专业的编剧。请根据用户的指令修改以下剧集大纲。

【项目信息】
故事名称: {project.name}
故事类型: {GENRE_NAMES.get(project.genre, project.genre)}
风格: {project.style}
总集数: {project.num_episodes}

【当前剧集】
第{episode.episode_number}集
标题: {episode.title}
大纲:
{episode.outline}

{character_context}

【用户修改指令】
{instruction}

请根据指令修改剧集大纲，以JSON格式输出:
```json
{{
    "new_title": "修改后的标题（如果标题需要变化）",
    "new_outline": "修改后的完整大纲",
    "changes_summary": "简要说明做了哪些修改（50字以内）"
}}
```

注意:
1. 仅根据指令进行必要的修改
2. 保持与整体故事风格的一致性
3. 考虑与其他剧集的连贯性"""

        response = self._generate(prompt, temperature=0.7)
        return self._parse_json_response(response)

    def analyze_edit_impact(
        self,
        edited_episode: Episode,
        original_outline: str,
        new_outline: str,
        project: Project,
        all_episodes: List[Episode],
        characters: List[Character]
    ) -> List[Dict[str, Any]]:
        """
        分析编辑对其他剧集和角色的影响

        Returns:
            [
                {
                    "type": "episode" | "character",
                    "id": 目标ID,
                    "name": "名称",
                    "issue": "问题描述",
                    "severity": "warning" | "error",
                    "suggested_fix": "建议的修改",
                    "auto_fixable": true/false
                }
            ]
        """
        self._current_method_name = "analyze_edit_impact"
        # 构建其他剧集的上下文
        other_episodes_context = ""
        for ep in all_episodes:
            if ep.episode_number != edited_episode.episode_number:
                other_episodes_context += f"第{ep.episode_number}集 - {ep.title}: {ep.outline[:200]}...\n\n"

        # 构建角色上下文
        characters_context = ""
        for char in characters:
            characters_context += f"【{char.name}】{char.personality}，{char.background[:100]}...\n"
            if char.major_events:
                for event in char.major_events:
                    characters_context += f"  - 第{event.episode_number}集: {event.description}\n"

        prompt = f"""你是一位专业的剧本顾问。请分析以下剧集大纲的修改对其他内容的影响。

【被修改的剧集】
第{edited_episode.episode_number}集 - {edited_episode.title}

【原大纲】
{original_outline}

【新大纲】
{new_outline}

【其他剧集】
{other_episodes_context or "暂无其他剧集"}

【角色设定】
{characters_context or "暂无角色"}

请分析这次修改是否会导致以下问题:
1. 与前面剧集的剧情矛盾
2. 与后面剧集的剧情不连贯
3. 与角色设定或经历的矛盾
4. 时间线问题

以JSON格式输出所有发现的问题:
```json
{{
    "issues": [
        {{
            "type": "episode",
            "id": 剧集编号,
            "name": "第X集标题",
            "issue": "问题描述",
            "severity": "warning或error（error=严重矛盾必须修复，warning=建议修复但不影响故事理解）",
            "suggested_fix": "建议如何修改受影响的内容",
            "auto_fixable": true或false,
            "auto_fix_reason": "为什么可以/不可以自动修复"
        }},
        {{
            "type": "character",
            "id": 0,
            "name": "角色名",
            "issue": "问题描述",
            "severity": "warning或error",
            "suggested_fix": "建议如何修改角色设定或经历",
            "auto_fixable": true或false,
            "auto_fix_reason": "为什么可以/不可以自动修复"
        }}
    ]
}}
```

【auto_fixable判断标准】
- true: 问题是简单的事实性错误，可以通过添加/修改少量细节来修复，不影响核心剧情
- false: 问题涉及叙事结构、角色核心设定、或需要创意性重写，应由人工审核

如果没有发现问题，返回空的issues数组。只报告真正存在的问题，不要过度解读。"""

        response = self._generate(prompt, temperature=0.5)
        data = self._parse_json_response(response)
        return data.get("issues", [])

    def generate_consistency_fix(
        self,
        issue_type: str,
        target_name: str,
        issue_description: str,
        original_content: str,
        project: Project,
        character_context: str
    ) -> Dict[str, Any]:
        """
        为一致性问题生成修复建议

        Returns:
            {
                "fixed_content": "修复后的内容",
                "explanation": "修改说明"
            }
        """
        self._current_method_name = "generate_consistency_fix"
        prompt = f"""你是一位专业的剧本顾问。请修复以下一致性问题。

【项目信息】
故事名称: {project.name}
风格: {project.style}

【问题类型】
{issue_type}: {target_name}

【问题描述】
{issue_description}

【需要修改的内容】
{original_content}

{character_context}

请生成修复后的内容，以JSON格式输出:
```json
{{
    "fixed_content": "修复后的完整内容",
    "explanation": "简要说明修改了什么（30字以内）"
}}
```

注意:
1. 只做必要的修改来解决问题
2. 保持内容的完整性和连贯性
3. 不要改变核心情节，只修复不一致之处"""

        response = self._generate(prompt, temperature=0.6)
        return self._parse_json_response(response)

    def batch_check_consistency(
        self,
        project: Project,
        episodes: List[Episode],
        characters: List[Character]
    ) -> List[Dict[str, Any]]:
        """
        全局一致性检查

        Returns:
            问题列表
        """
        self._current_method_name = "batch_check_consistency"
        # 构建完整的剧情时间线
        timeline = ""
        for ep in sorted(episodes, key=lambda x: x.episode_number):
            timeline += f"第{ep.episode_number}集 - {ep.title}:\n{ep.outline}\n\n"

        # 构建角色经历时间线
        character_timelines = ""
        for char in characters:
            if char.major_events:
                character_timelines += f"【{char.name}的经历】\n"
                for event in sorted(char.major_events, key=lambda x: x.episode_number):
                    character_timelines += f"  第{event.episode_number}集: {event.description} → {event.impact}\n"
                character_timelines += "\n"

        prompt = f"""你是一位专业的剧本审核专家。请全面检查以下故事的一致性问题。

【项目信息】
故事名称: {project.name}
类型: {GENRE_NAMES.get(project.genre, project.genre)}
风格: {project.style}

【剧情时间线】
{timeline}

【角色经历时间线】
{character_timelines or "暂无角色经历记录"}

请检查以下方面的一致性问题:
1. 剧情逻辑：前后剧集的因果关系是否合理
2. 角色行为：角色的行为是否符合其设定
3. 时间线：事件发生的顺序是否合理
4. 细节一致：场景、物品、关系等细节是否前后一致

以JSON格式输出所有发现的问题:
```json
{{
    "issues": [
        {{
            "type": "episode或character",
            "id": 相关ID,
            "name": "名称",
            "issue": "问题描述",
            "severity": "warning或error",
            "suggested_fix": "建议的修复方案",
            "auto_fixable": true或false
        }}
    ],
    "overall_assessment": "整体一致性评估（好/一般/需要改进）"
}}
```

如果没有发现问题，返回空的issues数组。只报告真正的问题，不要过度解读。"""

        response = self._generate(prompt, temperature=0.5)
        data = self._parse_json_response(response)
        return data.get("issues", [])

    # ==================== 辅助功能 ====================

    def polish_text(self, text: str, style: str = "") -> str:
        """润色文本"""
        self._current_method_name = "polish_text"
        prompt = f"""请润色以下文本，使其更加流畅和生动。

原文:
{text}

风格要求: {style or "保持原有风格，适当优化"}

直接输出润色后的文本，不要任何额外说明。"""

        return self._generate(prompt, temperature=0.6).strip()

    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        self._current_method_name = "test_connection"
        try:
            response = self._generate("请回复'连接成功'", temperature=0)
            return {
                "success": True,
                "message": "Gemini API连接成功",
                "model": self.config.model_name,
                "response": response[:100]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
