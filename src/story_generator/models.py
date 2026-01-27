"""
Story Generator Data Models

数据模型定义，用于故事生成器的所有实体
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json


class Genre(Enum):
    """故事类型"""
    ROMANCE = "romance"  # 爱情
    ACTION = "action"  # 动作
    SCIFI = "sci-fi"  # 科幻
    FANTASY = "fantasy"  # 奇幻
    COMEDY = "comedy"  # 喜剧
    DRAMA = "drama"  # 剧情
    HORROR = "horror"  # 恐怖
    THRILLER = "thriller"  # 悬疑
    DOCUMENTARY = "documentary"  # 纪录片
    ANIMATION = "animation"  # 动画
    OTHER = "other"  # 其他


class ShotType(Enum):
    """镜头类型"""
    EXTREME_WIDE = "extreme_wide"  # 大远景
    WIDE = "wide"  # 远景
    FULL = "full"  # 全景
    MEDIUM = "medium"  # 中景
    MEDIUM_CLOSE = "medium_close"  # 中近景
    CLOSE_UP = "close_up"  # 近景/特写
    EXTREME_CLOSE_UP = "extreme_close_up"  # 大特写
    POV = "pov"  # 主观镜头
    OVER_SHOULDER = "over_shoulder"  # 过肩镜头
    TWO_SHOT = "two_shot"  # 双人镜头


class CameraMovement(Enum):
    """镜头运动"""
    STATIC = "static"  # 固定
    PAN_LEFT = "pan_left"  # 左摇
    PAN_RIGHT = "pan_right"  # 右摇
    TILT_UP = "tilt_up"  # 上摇
    TILT_DOWN = "tilt_down"  # 下摇
    ZOOM_IN = "zoom_in"  # 推进
    ZOOM_OUT = "zoom_out"  # 拉远
    DOLLY_IN = "dolly_in"  # 推轨
    DOLLY_OUT = "dolly_out"  # 拉轨
    TRACKING = "tracking"  # 跟踪
    CRANE_UP = "crane_up"  # 升
    CRANE_DOWN = "crane_down"  # 降
    HANDHELD = "handheld"  # 手持晃动


class ShotDensity(Enum):
    """分镜密度"""
    LOW = "low"  # 少 - 最小分镜数
    MEDIUM = "medium"  # 中 - 1.5倍最小
    HIGH = "high"  # 多 - 2倍最小
    CUSTOM = "custom"  # 自定义


class EditType(Enum):
    """编辑类型"""
    EPISODE_OUTLINE = "episode_outline"  # 剧集大纲
    CHARACTER = "character"  # 人物设定
    PROJECT = "project"  # 项目信息


@dataclass
class MajorEvent:
    """人物重大经历"""
    episode_number: int  # 发生在第几集
    description: str  # 事件描述
    impact: str  # 对人物的影响
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "episode_number": self.episode_number,
            "description": self.description,
            "impact": self.impact,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MajorEvent":
        return cls(
            episode_number=data["episode_number"],
            description=data["description"],
            impact=data["impact"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        )


@dataclass
class EditHistory:
    """编辑历史记录，用于支持撤销/重做"""
    id: Optional[int] = None
    project_id: Optional[int] = None
    edit_type: str = ""  # episode_outline, character, project
    target_id: Optional[int] = None  # 被编辑对象的ID（如episode_id, character_id）
    field_name: str = ""  # 被修改的字段名
    old_value: str = ""  # 修改前的值（JSON格式）
    new_value: str = ""  # 修改后的值（JSON格式）
    edit_instruction: str = ""  # 用户的编辑指令（如果是AI辅助编辑）
    is_ai_edit: bool = False  # 是否为AI辅助编辑
    related_changes: str = ""  # 关联的一致性修改（JSON格式，记录其他被影响的修改）
    is_undone: bool = False  # 是否已被撤销
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "edit_type": self.edit_type,
            "target_id": self.target_id,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "edit_instruction": self.edit_instruction,
            "is_ai_edit": self.is_ai_edit,
            "related_changes": self.related_changes,
            "is_undone": self.is_undone,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EditHistory":
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id"),
            edit_type=data.get("edit_type", ""),
            target_id=data.get("target_id"),
            field_name=data.get("field_name", ""),
            old_value=data.get("old_value", ""),
            new_value=data.get("new_value", ""),
            edit_instruction=data.get("edit_instruction", ""),
            is_ai_edit=data.get("is_ai_edit", False),
            related_changes=data.get("related_changes", ""),
            is_undone=data.get("is_undone", False),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )


@dataclass
class ConsistencyIssue:
    """一致性问题"""
    issue_type: str  # episode_conflict, character_conflict, timeline_conflict
    severity: str  # warning, error
    affected_item_type: str  # episode, character
    affected_item_id: int
    affected_item_name: str
    description: str  # 问题描述
    suggested_fix: str  # 建议的修复内容
    auto_fixable: bool = True  # 是否可以自动修复

    def to_dict(self) -> dict:
        return {
            "issue_type": self.issue_type,
            "severity": self.severity,
            "affected_item_type": self.affected_item_type,
            "affected_item_id": self.affected_item_id,
            "affected_item_name": self.affected_item_name,
            "description": self.description,
            "suggested_fix": self.suggested_fix,
            "auto_fixable": self.auto_fixable
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConsistencyIssue":
        return cls(
            issue_type=data.get("issue_type", ""),
            severity=data.get("severity", "warning"),
            affected_item_type=data.get("affected_item_type", ""),
            affected_item_id=data.get("affected_item_id", 0),
            affected_item_name=data.get("affected_item_name", ""),
            description=data.get("description", ""),
            suggested_fix=data.get("suggested_fix", ""),
            auto_fixable=data.get("auto_fixable", True)
        )


@dataclass
class Character:
    """人物设定"""
    id: Optional[int] = None
    project_id: Optional[int] = None
    name: str = ""
    age: str = ""  # 可以是具体年龄或描述性的（如"中年"）
    appearance: str = ""  # 外貌描述
    personality: str = ""  # 性格特点
    background: str = ""  # 背景故事
    relationships: str = ""  # 与其他人物的关系
    visual_description: str = ""  # 视觉描述（用于生成一致的图像/视频）
    major_events: List[MajorEvent] = field(default_factory=list)  # 重大经历
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_major_event(self, episode_number: int, description: str, impact: str):
        """添加重大经历"""
        event = MajorEvent(
            episode_number=episode_number,
            description=description,
            impact=impact
        )
        self.major_events.append(event)
        self.updated_at = datetime.now()

    def get_knowledge_context(self, up_to_episode: Optional[int] = None) -> str:
        """
        获取人物知识库上下文，用于生成剧本时保持一致性

        Args:
            up_to_episode: 只包含到某一集为止的经历（避免剧透）
        """
        context = f"""【人物设定 - {self.name}】
姓名: {self.name}
年龄: {self.age}
外貌: {self.appearance}
性格: {self.personality}
背景: {self.background}
人物关系: {self.relationships}
视觉特征: {self.visual_description}
"""
        if self.major_events:
            events = self.major_events
            if up_to_episode is not None:
                events = [e for e in events if e.episode_number <= up_to_episode]

            if events:
                context += "\n重大经历:\n"
                for event in sorted(events, key=lambda x: x.episode_number):
                    context += f"  - 第{event.episode_number}集: {event.description} (影响: {event.impact})\n"

        return context

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "age": self.age,
            "appearance": self.appearance,
            "personality": self.personality,
            "background": self.background,
            "relationships": self.relationships,
            "visual_description": self.visual_description,
            "major_events": [e.to_dict() for e in self.major_events],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id"),
            name=data.get("name", ""),
            age=data.get("age", ""),
            appearance=data.get("appearance", ""),
            personality=data.get("personality", ""),
            background=data.get("background", ""),
            relationships=data.get("relationships", ""),
            visual_description=data.get("visual_description", ""),
            major_events=[MajorEvent.from_dict(e) for e in data.get("major_events", [])],
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )


@dataclass
class Shot:
    """分镜/镜头"""
    id: Optional[int] = None
    episode_id: Optional[int] = None
    scene_number: int = 1  # 场景编号
    shot_number: int = 1  # 镜头编号
    shot_type: str = "medium"  # 镜头类型
    duration: int = 5  # 时长（秒）
    visual_description: str = ""  # 画面描述
    dialogue: str = ""  # 对白
    sound_music: str = ""  # 音效/配乐
    camera_movement: str = "static"  # 镜头运动
    notes: str = ""  # 备注

    # 生成的提示词（按平台存储）
    generated_prompts: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "episode_id": self.episode_id,
            "scene_number": self.scene_number,
            "shot_number": self.shot_number,
            "shot_type": self.shot_type,
            "duration": self.duration,
            "visual_description": self.visual_description,
            "dialogue": self.dialogue,
            "sound_music": self.sound_music,
            "camera_movement": self.camera_movement,
            "notes": self.notes,
            "generated_prompts": self.generated_prompts
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Shot":
        return cls(
            id=data.get("id"),
            episode_id=data.get("episode_id"),
            scene_number=data.get("scene_number", 1),
            shot_number=data.get("shot_number", 1),
            shot_type=data.get("shot_type", "medium"),
            duration=data.get("duration", 5),
            visual_description=data.get("visual_description", ""),
            dialogue=data.get("dialogue", ""),
            sound_music=data.get("sound_music", ""),
            camera_movement=data.get("camera_movement", "static"),
            notes=data.get("notes", ""),
            generated_prompts=data.get("generated_prompts", {})
        )


@dataclass
class Episode:
    """剧集"""
    id: Optional[int] = None
    project_id: Optional[int] = None
    episode_number: int = 1
    title: str = ""
    outline: str = ""  # 本集大纲
    duration: int = 60  # 目标时长（秒）
    shots: List[Shot] = field(default_factory=list)
    status: str = "outline"  # outline, in_progress, completed
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_total_duration(self) -> int:
        """计算所有镜头的总时长"""
        return sum(shot.duration for shot in self.shots)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "episode_number": self.episode_number,
            "title": self.title,
            "outline": self.outline,
            "duration": self.duration,
            "shots": [s.to_dict() for s in self.shots],
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Episode":
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id"),
            episode_number=data.get("episode_number", 1),
            title=data.get("title", ""),
            outline=data.get("outline", ""),
            duration=data.get("duration", 60),
            shots=[Shot.from_dict(s) for s in data.get("shots", [])],
            status=data.get("status", "outline"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )


@dataclass
class Project:
    """故事项目"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""  # 故事创意/描述
    genre: str = "drama"  # 类型
    style: str = ""  # 风格描述
    target_audience: str = ""  # 目标受众
    num_episodes: int = 1  # 集数
    episode_duration: int = 60  # 每集时长（秒）
    max_video_duration: int = 10  # 最大视频时长（秒），用于计算最小分镜数
    characters: List[Character] = field(default_factory=list)
    episodes: List[Episode] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def get_min_shots_per_episode(self) -> int:
        """计算每集最小分镜数"""
        import math
        return math.ceil(self.episode_duration / self.max_video_duration)

    def get_all_characters_context(self, up_to_episode: Optional[int] = None) -> str:
        """获取所有人物的知识库上下文"""
        if not self.characters:
            return ""

        context = "=== 人物知识库 ===\n\n"
        for char in self.characters:
            context += char.get_knowledge_context(up_to_episode) + "\n"
        return context

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "genre": self.genre,
            "style": self.style,
            "target_audience": self.target_audience,
            "num_episodes": self.num_episodes,
            "episode_duration": self.episode_duration,
            "max_video_duration": self.max_video_duration,
            "characters": [c.to_dict() for c in self.characters],
            "episodes": [e.to_dict() for e in self.episodes],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            genre=data.get("genre", "drama"),
            style=data.get("style", ""),
            target_audience=data.get("target_audience", ""),
            num_episodes=data.get("num_episodes", 1),
            episode_duration=data.get("episode_duration", 60),
            max_video_duration=data.get("max_video_duration", 10),
            characters=[Character.from_dict(c) for c in data.get("characters", [])],
            episodes=[Episode.from_dict(e) for e in data.get("episodes", [])],
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )


# 镜头类型的中文映射
SHOT_TYPE_NAMES = {
    "extreme_wide": "大远景",
    "wide": "远景",
    "full": "全景",
    "medium": "中景",
    "medium_close": "中近景",
    "close_up": "近景/特写",
    "extreme_close_up": "大特写",
    "pov": "主观镜头",
    "over_shoulder": "过肩镜头",
    "two_shot": "双人镜头",
}

# 镜头运动的中文映射
CAMERA_MOVEMENT_NAMES = {
    "static": "固定",
    "pan_left": "左摇",
    "pan_right": "右摇",
    "tilt_up": "上摇",
    "tilt_down": "下摇",
    "zoom_in": "推进",
    "zoom_out": "拉远",
    "dolly_in": "推轨",
    "dolly_out": "拉轨",
    "tracking": "跟踪",
    "crane_up": "升",
    "crane_down": "降",
    "handheld": "手持晃动",
}

@dataclass
class APICallLog:
    """API调用记录，用于追踪和审计"""
    id: Optional[int] = None
    project_id: Optional[int] = None  # 关联的项目ID（可为空）
    method_name: str = ""  # 调用的方法名，如 "generate_story_outline"
    prompt: str = ""  # 发送给模型的完整prompt
    response: str = ""  # 模型的原始响应
    latency_ms: int = 0  # 响应时间（毫秒）
    status: str = "success"  # success / error
    error_message: str = ""  # 错误信息（如果有）
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "method_name": self.method_name,
            "prompt": self.prompt,
            "response": self.response,
            "latency_ms": self.latency_ms,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "APICallLog":
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id"),
            method_name=data.get("method_name", ""),
            prompt=data.get("prompt", ""),
            response=data.get("response", ""),
            latency_ms=data.get("latency_ms", 0),
            status=data.get("status", "success"),
            error_message=data.get("error_message", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        )


@dataclass
class PromptTemplate:
    """提示词模板，支持版本管理"""
    id: Optional[int] = None
    name: str = ""  # 模板名称/方法名，如 "generate_story_outline"
    description: str = ""  # 中文说明
    template: str = ""  # 提示词模板内容
    variables: str = ""  # 可用变量列表（JSON格式）
    version: int = 1  # 版本号
    is_active: bool = True  # 是否为当前激活版本
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "variables": self.variables,
            "version": self.version,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PromptTemplate":
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            template=data.get("template", ""),
            variables=data.get("variables", ""),
            version=data.get("version", 1),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )

    def get_variables_list(self) -> List[str]:
        """获取变量列表"""
        if not self.variables:
            return []
        try:
            return json.loads(self.variables)
        except:
            return []


# 故事类型的中文映射
GENRE_NAMES = {
    "romance": "爱情",
    "action": "动作",
    "sci-fi": "科幻",
    "fantasy": "奇幻",
    "comedy": "喜剧",
    "drama": "剧情",
    "horror": "恐怖",
    "thriller": "悬疑",
    "documentary": "纪录片",
    "animation": "动画",
    "other": "其他",
}


# 提示词模板的中文名称和说明
PROMPT_TEMPLATE_INFO = {
    "generate_story_outline": {
        "name": "故事大纲生成",
        "description": "根据用户创意生成完整的故事大纲、角色和剧集",
        "variables": ["idea", "genre_name", "style", "target_audience", "num_episodes", "episode_duration", "num_characters"]
    },
    "generate_random_story_idea": {
        "name": "随机创意生成",
        "description": "随机生成一个故事创意",
        "variables": ["genre_hint", "style_hint"]
    },
    "generate_storyboard": {
        "name": "分镜脚本生成",
        "description": "将剧集大纲展开为详细的分镜脚本",
        "variables": ["project_name", "genre_name", "style", "episode_number", "episode_title", "episode_duration", "episode_outline", "character_context", "target_shots", "min_shots", "max_video_duration", "avg_shot_duration"]
    },
    "expand_shot_description": {
        "name": "镜头描述优化",
        "description": "扩展和优化单个镜头的画面描述",
        "variables": ["scene_number", "shot_number", "shot_type", "duration", "camera_movement", "visual_description", "dialogue", "style", "character_context"]
    },
    "generate_video_prompt": {
        "name": "视频提示词生成",
        "description": "为指定平台生成视频生成提示词",
        "variables": ["visual_description", "dialogue", "shot_type", "camera_movement", "duration", "sound_music", "style", "character_context", "platform", "platform_guide", "camera_hint", "type_instruction", "extra_instruction"]
    },
    "platform_guide_kling": {
        "name": "可灵平台提示词指南",
        "description": "可灵(Kling)平台的提示词风格指南",
        "variables": []
    },
    "platform_guide_tongyi": {
        "name": "通义万相平台提示词指南",
        "description": "通义万相平台的提示词风格指南",
        "variables": []
    },
    "platform_guide_jimeng": {
        "name": "即梦平台提示词指南",
        "description": "即梦(Jimeng)平台的提示词风格指南",
        "variables": []
    },
    "platform_guide_hailuo": {
        "name": "海螺平台提示词指南",
        "description": "海螺(Hailuo)平台的提示词风格指南",
        "variables": []
    },
    "edit_episode_with_instruction": {
        "name": "AI编辑剧集",
        "description": "根据用户指令AI编辑剧集大纲",
        "variables": ["project_name", "genre_name", "style", "num_episodes", "episode_number", "episode_title", "episode_outline", "character_context", "instruction"]
    },
    "analyze_edit_impact": {
        "name": "编辑影响分析",
        "description": "分析编辑对其他剧集和角色的影响",
        "variables": ["episode_number", "episode_title", "original_outline", "new_outline", "other_episodes_context", "characters_context"]
    },
    "generate_consistency_fix": {
        "name": "一致性修复",
        "description": "为一致性问题生成修复建议",
        "variables": ["project_name", "style", "issue_type", "target_name", "issue_description", "original_content", "character_context"]
    },
    "batch_check_consistency": {
        "name": "批量一致性检查",
        "description": "全局检查故事的一致性问题",
        "variables": ["project_name", "genre_name", "style", "timeline", "character_timelines"]
    },
    "analyze_episode_for_character_events": {
        "name": "角色事件分析",
        "description": "分析剧集中各角色的重大经历",
        "variables": ["content", "character_names"]
    }
}
