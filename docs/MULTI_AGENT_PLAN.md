# 多Agent AI视频生成平台 - 架构设计计划

## 1. 项目目标

将现有的故事生成器和视频生成能力转化为可被 LangChain/LangGraph Agent 调用的标准化接口，构建一个多 Agent 协作的自动化 AI 视频生成平台。

## 2. 现有组件分析

### 2.1 已实现的组件

```
src/
├── story_generator/          # ✅ 故事生成模块
│   ├── app.py               # Streamlit UI
│   ├── models.py            # 数据模型 (Project, Character, Episode, Shot, etc.)
│   ├── database.py          # SQLite 数据库操作
│   └── gemini_client.py     # Gemini API 客户端（故事/分镜/提示词生成）
│
├── providers/                # ✅ 视频生成API集成
│   ├── base.py              # VideoProvider 抽象基类, VideoTask, TaskStatus
│   ├── kling.py             # 可灵 API (text-to-video, image-to-video, with-reference)
│   ├── hailuo.py            # 海螺/MiniMax API (t2v, i2v, 主体参考, 运镜控制)
│   ├── jimeng.py            # 即梦 API
│   ├── tongyi.py            # 通义万相 API
│   ├── config.py            # YAML配置管理 (支持环境变量覆盖)
│   └── config.local.yaml    # 本地配置（API Keys）
│
└── comparison/               # ✅ 视频生成对比工具
    ├── app.py               # Streamlit 多平台对比UI
    └── model_capabilities.py # 模型能力定义
```

### 2.2 复用策略

| 现有组件 | 复用方式 |
|----------|----------|
| `gemini_client.py` | **不再直接使用**。LLM调用由Agent完成，提示词迁移到Skills |
| `database.py` | **直接复用**。MCP Server通过它操作数据库 |
| `models.py` | **直接复用**。数据模型保持不变 |
| `providers/*.py` | **直接复用**。MCP Server封装这些Provider |
| `config.py` | **直接复用**。视频平台配置 |

### 2.3 需要迁移的内容

`gemini_client.py` 中的提示词需要迁移到 Skills 文件：

| 方法 | 迁移到 Skill |
|------|--------------|
| `generate_story_outline()` | `skills/writing/story_outline.md` |
| `generate_random_story_idea()` | `skills/writing/random_idea.md` |
| `generate_storyboard()` | `skills/directing/storyboard.md` |
| `expand_shot_description()` | `skills/directing/shot_description.md` |
| `generate_video_prompt()` | `skills/video/prompt_generation.md` |
| `analyze_edit_impact()` | `skills/writing/consistency_check.md` |
| 平台指南 | `skills/video/platforms/*.md` |

## 3. 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent 框架 | LangGraph | 低级编排框架，支持有状态的长时运行 Agent |
| 工具协议 | MCP (Model Context Protocol) | 标准化的 LLM 工具接口协议 |
| MCP 服务器 | FastMCP | Python MCP 服务器框架，STDIO 模式本地运行 |
| Agent 模式 | Supervisor Pattern | 监督者协调专业化工作 Agent |
| LLM | Google Gemini | 继续使用现有的 Gemini |

### 参考资料

- [LangChain Skills](https://docs.langchain.com/oss/python/langchain/multi-agent/skills)
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [Hierarchical Agent Teams](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/)

## 4. 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户界面层                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ Streamlit   │  │ CLI         │  │ 全托管模式   │                 │
│  │ (交互模式)   │  │ 命令行工具   │  │ (自动化)    │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                     Agent 编排层 (LangGraph)                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   Supervisor Agent                           │   │
│  │              (总监督者 - 任务分解与协调)                        │   │
│  │                    使用 Gemini LLM                           │   │
│  └──────────┬──────────┬──────────┬──────────┬─────────────────┘   │
│             │          │          │          │                      │
│  ┌──────────▼───┐ ┌────▼─────┐ ┌──▼──────┐ ┌─▼──────────┐          │
│  │ Story Writer │ │Character │ │Director │ │ Video      │          │
│  │ Agent        │ │Designer  │ │ Agent   │ │ Producer   │          │
│  │ (编剧)       │ │ Agent    │ │ (分镜师) │ │ Agent      │          │
│  │              │ │ (角色师)  │ │         │ │ (视频师)   │          │
│  └──────┬───────┘ └────┬─────┘ └────┬────┘ └──────┬─────┘          │
│         │              │            │             │                 │
│         └──────────────┴─────┬──────┴─────────────┘                 │
│                              │ 加载 Skills                          │
│  ┌───────────────────────────▼─────────────────────────────────┐   │
│  │                      Skills 资料库                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │   │
│  │  │ 写作技巧  │ │ 角色设计  │ │ 分镜知识  │ │ 平台指南  │        │   │
│  │  │ Skills   │ │ Skills   │ │ Skills   │ │ Skills   │        │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │ MCP Protocol (STDIO)
┌────────────────────────────▼────────────────────────────────────────┐
│                     MCP 服务器层 (FastMCP)                           │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Project Server   │  │ Storyboard       │  │ Video Server     │  │
│  │                  │  │ Server           │  │                  │  │
│  │ 复用:            │  │ 复用:            │  │ 复用:            │  │
│  │ - database.py    │  │ - database.py    │  │ - providers/*    │  │
│  │ - models.py      │  │ - models.py      │  │ - config.py      │  │
│  │                  │  │                  │  │                  │  │
│  │ Tools:           │  │ Tools:           │  │ Tools:           │  │
│  │ - create_project │  │ - create_shots   │  │ - submit_t2v     │  │
│  │ - create_episode │  │ - update_shot    │  │ - submit_i2v     │  │
│  │ - create_char    │  │ - list_shots     │  │ - get_task_status│  │
│  │ - update_*       │  │                  │  │ - download_video │  │
│  │ - get_*          │  │ Resources:       │  │                  │  │
│  │                  │  │ - storyboard://  │  │ Resources:       │  │
│  │ Resources:       │  │                  │  │ - video_task://  │  │
│  │ - project://     │  │                  │  │                  │  │
│  │ - character://   │  │                  │  │                  │  │
│  │ - episode://     │  │                  │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                        数据层                                        │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │ SQLite               │  │ 文件存储              │                │
│  │ (story_generator.db) │  │ (视频/图片素材)       │                │
│  │                      │  │                      │                │
│  │ 复用现有表结构:       │  │                      │                │
│  │ - projects           │  │                      │                │
│  │ - characters         │  │                      │                │
│  │ - episodes           │  │                      │                │
│  │ - shots              │  │                      │                │
│  │ - api_call_logs      │  │                      │                │
│  │ - prompt_templates   │  │                      │                │
│  └──────────────────────┘  └──────────────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

## 5. Skills 系统设计

### 5.1 核心概念

**Skills 是什么：**
- Skills 是给 Agent 的"知识/指导"文件
- 告诉 Agent 怎么做一件事、有哪些工具可用、有哪些注意事项
- Agent (LLM) 加载 Skill 后，理解其内容，然后执行相应操作

**Skills 不是什么：**
- Skills 不是独立调用 LLM 的代码
- Skills 不是 MCP Tool（Tool 是实际执行操作的）

**Agent 使用 Skills 的流程：**
```
1. Supervisor 分配任务给 Story Writer Agent
2. Story Writer Agent 加载 "story_outline" Skill
3. Skill 告诉 Agent：
   - 如何构思故事大纲
   - 需要考虑哪些元素
   - 输出应该是什么格式
   - 可以调用哪些 MCP Tools
4. Agent (Gemini LLM) 根据 Skill 指导生成内容
5. Agent 调用 MCP Tools 保存数据
```

### 5.2 Skills 目录结构

```
src/skills/
├── __init__.py
├── loader.py                    # Skill 加载器
├── registry.py                  # Skill 注册表
│
├── writing/                     # 编剧 Skills
│   ├── story_outline.md         # 故事大纲生成指南
│   ├── random_idea.md           # 随机创意生成
│   ├── episode_editing.md       # 剧集编辑
│   ├── consistency_check.md     # 一致性检查
│   └── genres/                  # 类型特化
│       ├── scifi.md
│       ├── romance.md
│       ├── thriller.md
│       └── comedy.md
│
├── character/                   # 角色设计 Skills
│   ├── character_creation.md    # 角色创建指南
│   ├── character_development.md # 角色发展
│   └── relationship_design.md   # 人物关系设计
│
├── directing/                   # 分镜 Skills
│   ├── storyboard.md           # 分镜脚本生成
│   ├── shot_description.md     # 镜头描述扩展
│   ├── camera_movement.md      # 镜头运动设计
│   └── visual_styles/          # 视觉风格
│       ├── cinematic.md
│       ├── anime.md
│       └── documentary.md
│
└── video/                       # 视频生成 Skills
    ├── prompt_generation.md     # 提示词生成通用指南
    ├── platforms/               # 平台特化指南
    │   ├── kling.md            # 可灵平台
    │   ├── hailuo.md           # 海螺平台
    │   ├── jimeng.md           # 即梦平台
    │   └── tongyi.md           # 通义万相平台
    └── prompt_types/           # 提示词类型
        ├── t2v.md              # 文生视频
        ├── i2v.md              # 图生视频
        └── i2v_fl.md           # 首尾帧图生视频
```

### 5.3 Skill 文件格式

每个 Skill 是一个 Markdown 文件，包含：

```markdown
# Skill: 故事大纲生成

## 描述
指导如何根据用户创意生成完整的故事大纲。

## 适用 Agent
- story_writer

## 可用工具 (MCP Tools)
- `project://create` - 创建新项目
- `project://update` - 更新项目
- `character://create` - 创建角色
- `episode://create` - 创建剧集

## 输入
- 用户创意描述
- 故事类型 (可选)
- 风格偏好 (可选)
- 集数和时长要求

## 输出格式
生成的故事大纲应包含：
1. 故事标题
2. 故事简介 (200字以内)
3. 核心主题
4. 主要角色列表 (每个角色包含姓名、年龄、外貌、性格、背景、关系)
5. 剧集列表 (每集包含标题、大纲、关键事件)

## 指导原则
1. 角色之间需要有明确的关系和互动
2. 每集剧情要紧凑，适合指定时长
3. 整体故事有清晰的开端、发展、高潮、结局
4. 风格与类型保持一致
5. 为每个角色生成英文视觉描述 (visual_description)

## 示例
[示例输入和输出]
```

### 5.4 Skill Loader 实现

```python
# src/skills/loader.py

from pathlib import Path
from typing import Optional, List, Dict

SKILLS_DIR = Path(__file__).parent

class SkillLoader:
    """Skills 加载器"""

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def load_skill(self, skill_path: str) -> str:
        """
        加载指定的 Skill 文件

        Args:
            skill_path: Skill 路径，如 "writing/story_outline"

        Returns:
            Skill 内容 (Markdown)
        """
        if skill_path in self._cache:
            return self._cache[skill_path]

        file_path = SKILLS_DIR / f"{skill_path}.md"
        if not file_path.exists():
            raise FileNotFoundError(f"Skill not found: {skill_path}")

        content = file_path.read_text(encoding="utf-8")
        self._cache[skill_path] = content
        return content

    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """列出可用的 Skills"""
        if category:
            search_dir = SKILLS_DIR / category
        else:
            search_dir = SKILLS_DIR

        skills = []
        for md_file in search_dir.rglob("*.md"):
            rel_path = md_file.relative_to(SKILLS_DIR)
            skill_name = str(rel_path.with_suffix(""))
            skills.append(skill_name)

        return sorted(skills)

    def get_skill_metadata(self, skill_path: str) -> Dict:
        """获取 Skill 元数据 (从文件头部解析)"""
        content = self.load_skill(skill_path)
        # 解析 Markdown 头部提取元数据
        # ...
        return {}
```

## 6. MCP 服务器设计

### 6.1 Project Server (项目服务器)

复用 `database.py` 和 `models.py`，提供项目、角色、剧集的 CRUD 操作。

```python
# src/mcp_servers/project_server.py

from fastmcp import FastMCP
from story_generator.database import Database
from story_generator.models import Project, Character, Episode

mcp = FastMCP("Project Server")
db = Database()

# ==================== Project Tools ====================

@mcp.tool()
def create_project(
    name: str,
    description: str,
    genre: str,
    style: str,
    num_episodes: int,
    episode_duration: int,
    max_video_duration: int = 10,
    target_audience: str = ""
) -> dict:
    """创建新项目"""
    project = Project(
        name=name,
        description=description,
        genre=genre,
        style=style,
        target_audience=target_audience,
        num_episodes=num_episodes,
        episode_duration=episode_duration,
        max_video_duration=max_video_duration
    )
    project_id = db.create_project(project)
    return {"project_id": project_id, "name": name}

@mcp.tool()
def get_project(project_id: int) -> dict:
    """获取项目详情"""
    project = db.get_project(project_id)
    if not project:
        return {"error": "Project not found"}
    return project.to_dict()

@mcp.tool()
def update_project(project_id: int, updates: dict) -> dict:
    """更新项目信息"""
    project = db.get_project(project_id)
    if not project:
        return {"error": "Project not found"}
    for key, value in updates.items():
        if hasattr(project, key):
            setattr(project, key, value)
    db.update_project(project)
    return {"success": True}

# ==================== Character Tools ====================

@mcp.tool()
def create_character(
    project_id: int,
    name: str,
    age: str,
    appearance: str,
    personality: str,
    background: str,
    relationships: str,
    visual_description: str
) -> dict:
    """创建角色"""
    character = Character(
        project_id=project_id,
        name=name,
        age=age,
        appearance=appearance,
        personality=personality,
        background=background,
        relationships=relationships,
        visual_description=visual_description
    )
    char_id = db.create_character(character)
    return {"character_id": char_id, "name": name}

@mcp.tool()
def add_character_event(
    character_id: int,
    episode_number: int,
    description: str,
    impact: str
) -> dict:
    """添加角色重大经历"""
    character = db.get_character(character_id)
    if not character:
        return {"error": "Character not found"}
    character.add_major_event(episode_number, description, impact)
    db.update_character(character)
    return {"success": True}

@mcp.tool()
def get_character_context(project_id: int, up_to_episode: int = None) -> str:
    """获取角色知识库上下文（用于保持一致性）"""
    project = db.get_project(project_id)
    if not project:
        return ""
    return project.get_all_characters_context(up_to_episode)

# ==================== Episode Tools ====================

@mcp.tool()
def create_episode(
    project_id: int,
    episode_number: int,
    title: str,
    outline: str,
    duration: int
) -> dict:
    """创建剧集"""
    episode = Episode(
        project_id=project_id,
        episode_number=episode_number,
        title=title,
        outline=outline,
        duration=duration
    )
    ep_id = db.create_episode(episode)
    return {"episode_id": ep_id, "title": title}

@mcp.tool()
def update_episode(episode_id: int, updates: dict) -> dict:
    """更新剧集信息"""
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found"}
    for key, value in updates.items():
        if hasattr(episode, key):
            setattr(episode, key, value)
    db.update_episode(episode)
    return {"success": True}

# ==================== Resources ====================

@mcp.resource("project://{project_id}")
def get_project_resource(project_id: int) -> dict:
    """获取项目完整数据"""
    return get_project(project_id)

@mcp.resource("project://{project_id}/characters")
def get_project_characters(project_id: int) -> list:
    """获取项目所有角色"""
    project = db.get_project(project_id)
    return [c.to_dict() for c in project.characters] if project else []

@mcp.resource("project://{project_id}/episodes")
def get_project_episodes(project_id: int) -> list:
    """获取项目所有剧集"""
    project = db.get_project(project_id)
    return [e.to_dict() for e in project.episodes] if project else []

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 6.2 Storyboard Server (分镜服务器)

```python
# src/mcp_servers/storyboard_server.py

from fastmcp import FastMCP
from story_generator.database import Database
from story_generator.models import Shot

mcp = FastMCP("Storyboard Server")
db = Database()

@mcp.tool()
def create_shot(
    episode_id: int,
    scene_number: int,
    shot_number: int,
    shot_type: str,
    duration: int,
    visual_description: str,
    dialogue: str = "",
    sound_music: str = "",
    camera_movement: str = "static",
    notes: str = ""
) -> dict:
    """创建分镜"""
    shot = Shot(
        episode_id=episode_id,
        scene_number=scene_number,
        shot_number=shot_number,
        shot_type=shot_type,
        duration=duration,
        visual_description=visual_description,
        dialogue=dialogue,
        sound_music=sound_music,
        camera_movement=camera_movement,
        notes=notes
    )
    shot_id = db.create_shot(shot)
    return {"shot_id": shot_id}

@mcp.tool()
def update_shot(shot_id: int, updates: dict) -> dict:
    """更新分镜信息"""
    shot = db.get_shot(shot_id)
    if not shot:
        return {"error": "Shot not found"}
    for key, value in updates.items():
        if hasattr(shot, key):
            setattr(shot, key, value)
    db.update_shot(shot)
    return {"success": True}

@mcp.tool()
def save_generated_prompt(shot_id: int, platform: str, prompt_type: str, prompt: str) -> dict:
    """保存生成的提示词"""
    shot = db.get_shot(shot_id)
    if not shot:
        return {"error": "Shot not found"}
    key = f"{platform}_{prompt_type}"
    shot.generated_prompts[key] = prompt
    db.update_shot(shot)
    return {"success": True}

@mcp.tool()
def get_episode_shots(episode_id: int) -> list:
    """获取剧集所有分镜"""
    episode = db.get_episode(episode_id)
    if not episode:
        return []
    return [s.to_dict() for s in episode.shots]

@mcp.resource("storyboard://{episode_id}")
def get_storyboard(episode_id: int) -> dict:
    """获取剧集完整分镜数据"""
    episode = db.get_episode(episode_id)
    if not episode:
        return {"error": "Episode not found"}
    return {
        "episode": episode.to_dict(),
        "shots": [s.to_dict() for s in episode.shots],
        "total_duration": episode.get_total_duration()
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 6.3 Video Server (视频服务器)

复用 `providers/*`，提供视频生成 API 调用。

```python
# src/mcp_servers/video_server.py

from fastmcp import FastMCP
from typing import Optional
from providers.kling import KlingProvider
from providers.hailuo import HailuoProvider
from providers.jimeng import JimengProvider
from providers.tongyi import TongyiProvider
from providers.base import TaskStatus

mcp = FastMCP("Video Server")

# 初始化 Providers
providers = {
    "kling": KlingProvider(),
    "hailuo": HailuoProvider(),
    "jimeng": JimengProvider(),
    "tongyi": TongyiProvider(),
}

@mcp.tool()
def submit_text_to_video(
    provider: str,
    prompt: str,
    duration: int = 5,
    resolution: Optional[str] = None,
    **kwargs
) -> dict:
    """
    提交文生视频任务

    Args:
        provider: 平台名称 (kling, hailuo, jimeng, tongyi)
        prompt: 视频描述提示词
        duration: 时长（秒）
        resolution: 分辨率
    """
    if provider not in providers:
        return {"error": f"Unknown provider: {provider}"}

    p = providers[provider]
    if not p.is_configured():
        return {"error": f"Provider {provider} not configured"}

    task = p.submit_text_to_video(prompt, duration, resolution, **kwargs)
    return task.to_dict()

@mcp.tool()
def submit_image_to_video(
    provider: str,
    image_url: str,
    prompt: str,
    duration: int = 5,
    resolution: Optional[str] = None,
    end_frame_url: Optional[str] = None,
    **kwargs
) -> dict:
    """
    提交图生视频任务

    Args:
        provider: 平台名称
        image_url: 首帧图片URL
        prompt: 视频描述提示词
        duration: 时长（秒）
        end_frame_url: 尾帧图片URL（可选）
    """
    if provider not in providers:
        return {"error": f"Unknown provider: {provider}"}

    p = providers[provider]
    if not p.is_configured():
        return {"error": f"Provider {provider} not configured"}

    if end_frame_url:
        kwargs["end_frame_url"] = end_frame_url

    task = p.submit_image_to_video(image_url, prompt, duration, resolution, **kwargs)
    return task.to_dict()

@mcp.tool()
def get_task_status(provider: str, task_id: str) -> dict:
    """查询视频生成任务状态"""
    if provider not in providers:
        return {"error": f"Unknown provider: {provider}"}

    task = providers[provider].get_task_status(task_id)
    return task.to_dict()

@mcp.tool()
def wait_for_video(provider: str, task_id: str, timeout: int = 300) -> dict:
    """等待视频生成完成"""
    if provider not in providers:
        return {"error": f"Unknown provider: {provider}"}

    task = providers[provider].wait_for_completion(task_id, timeout)
    return task.to_dict()

@mcp.tool()
def list_available_providers() -> list:
    """列出可用的视频生成平台"""
    return [
        {
            "name": name,
            "configured": p.is_configured(),
            "models": p.list_models() if hasattr(p, "list_models") else []
        }
        for name, p in providers.items()
    ]

@mcp.resource("video_task://{provider}/{task_id}")
def get_video_task(provider: str, task_id: str) -> dict:
    """获取视频任务详情"""
    return get_task_status(provider, task_id)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## 7. Agent 设计

### 7.1 Agent 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户请求                                  │
│              "帮我创作一个科幻爱情故事，3集"                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                               │
│  1. 理解用户需求                                                   │
│  2. 制定工作计划                                                   │
│  3. 分配任务给专业Agent                                            │
│  4. 协调Agent之间的依赖                                            │
│  5. 汇总结果，请求用户确认（如需）                                   │
└───────────────────────────┬───────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │   Story   │   │ Character │   │ Director  │
    │   Writer  │──▶│ Designer  │──▶│   Agent   │──▶ ...
    │   Agent   │   │   Agent   │   │           │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
          │ 加载 Skills   │ 加载 Skills   │ 加载 Skills
          ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ writing/  │   │character/ │   │directing/ │
    │ story_*   │   │ creation  │   │storyboard │
    │ scifi.md  │   │           │   │ cinematic │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
          │ 调用 MCP     │ 调用 MCP     │ 调用 MCP
          ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ Project   │   │ Project   │   │Storyboard │
    │ Server    │   │ Server    │   │ Server    │
    └───────────┘   └───────────┘   └───────────┘
```

### 7.2 Supervisor Agent

```python
# src/agents/supervisor.py

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

class SupervisorAgent:
    """
    总监督者 Agent

    职责：
    - 接收用户高级指令
    - 分解任务并分配给专业 Agent
    - 协调 Agent 之间的工作流
    - 管理 Human-in-the-loop 交互
    - 处理错误和断点恢复
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.mcp_client = MultiServerMCPClient({
            "project": {"transport": "stdio", "command": "python", "args": ["mcp_servers/project_server.py"]},
            "storyboard": {"transport": "stdio", "command": "python", "args": ["mcp_servers/storyboard_server.py"]},
            "video": {"transport": "stdio", "command": "python", "args": ["mcp_servers/video_server.py"]},
        })

        # 子 Agent
        self.story_writer = StoryWriterAgent(self.llm, self.mcp_client)
        self.character_designer = CharacterDesignerAgent(self.llm, self.mcp_client)
        self.director = DirectorAgent(self.llm, self.mcp_client)
        self.video_producer = VideoProducerAgent(self.llm, self.mcp_client)

    async def run(self, user_request: str, mode: str = "interactive"):
        """
        执行用户请求

        Args:
            user_request: 用户的高级指令
            mode: "interactive" (交互模式) 或 "auto" (全托管模式)
        """
        # 1. 分析用户请求，制定计划
        plan = await self._create_plan(user_request)

        # 2. 按计划执行，在关键节点请求确认
        for step in plan.steps:
            result = await self._execute_step(step)

            if mode == "interactive" and step.requires_confirmation:
                # 请求用户确认
                confirmed = await self._request_user_confirmation(step, result)
                if not confirmed:
                    # 用户要求修改
                    continue

        return plan.final_result
```

### 7.3 Story Writer Agent

```python
# src/agents/story_writer.py

from skills.loader import SkillLoader

class StoryWriterAgent:
    """
    编剧 Agent

    职责：
    - 故事创意构思
    - 大纲生成与编辑
    - 剧情一致性维护
    """

    def __init__(self, llm, mcp_client):
        self.llm = llm
        self.mcp = mcp_client
        self.skill_loader = SkillLoader()

    async def create_story_outline(
        self,
        idea: str,
        genre: str,
        style: str,
        num_episodes: int,
        episode_duration: int,
        num_characters: int
    ) -> dict:
        """创建故事大纲"""

        # 1. 加载相关 Skills
        outline_skill = self.skill_loader.load_skill("writing/story_outline")
        genre_skill = self.skill_loader.load_skill(f"writing/genres/{genre}")

        # 2. 构建 Agent 提示
        prompt = f"""
你是一位专业的编剧。请根据以下指导创作故事大纲。

## 故事大纲创作指南
{outline_skill}

## {genre} 类型写作指南
{genre_skill}

## 用户需求
- 创意: {idea}
- 风格: {style}
- 集数: {num_episodes}
- 每集时长: {episode_duration}秒
- 人物数量: {num_characters}

请创作故事大纲，并以 JSON 格式输出。
"""

        # 3. 调用 LLM 生成
        response = await self.llm.ainvoke(prompt)
        story_data = self._parse_json_response(response.content)

        # 4. 调用 MCP Tools 保存数据
        tools = await self.mcp.get_tools()

        # 创建项目
        project_result = await tools["create_project"](
            name=story_data["title"],
            description=story_data["synopsis"],
            genre=genre,
            style=style,
            num_episodes=num_episodes,
            episode_duration=episode_duration
        )
        project_id = project_result["project_id"]

        # 创建角色
        for char in story_data["characters"]:
            await tools["create_character"](
                project_id=project_id,
                **char
            )

        # 创建剧集
        for ep in story_data["episodes"]:
            await tools["create_episode"](
                project_id=project_id,
                episode_number=ep["episode_number"],
                title=ep["title"],
                outline=ep["outline"],
                duration=episode_duration
            )

        return {"project_id": project_id, "story": story_data}
```

## 8. Human-in-the-loop 设计

### 8.1 交互模式 vs 全托管模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **交互模式** | 在关键节点暂停，请求用户确认/修改 | 需要精细控制的创作 |
| **全托管模式** | Agent 全自动执行，完成后通知用户 | 批量生成、原型测试 |

### 8.2 交互节点

```
用户输入创意
     │
     ▼
┌─────────────┐
│ 生成故事大纲 │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 📋 确认点1:      │  ← 用户可查看/修改：标题、简介、类型
│    故事大纲      │     快速输入：接受 / 修改 / 重新生成
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ 生成角色设定 │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 📋 确认点2:      │  ← 用户可查看/修改：角色列表、关系
│    角色设定      │     快速输入：接受 / 添加角色 / 修改角色
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ 生成分镜脚本 │  (按剧集循环)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 📋 确认点3:      │  ← 用户可查看：镜头列表、总时长
│    分镜脚本      │     快速输入：接受 / 调整密度 / 重新生成
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ 生成视频提示词│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 📋 确认点4:      │  ← 用户可选择：目标平台、开始生成
│    开始生成视频   │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ 视频生成中...│  ← 显示进度，支持取消
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 📋 确认点5:      │  ← 用户可查看：生成的视频列表
│    视频生成完成   │     操作：下载 / 重新生成某个镜头
└─────────────────┘
```

### 8.3 快速输入设计

用户可以在确认点输入简短指令：

```
确认点1 - 故事大纲:
> ok                    # 接受，继续
> 改成5集               # 修改参数
> 主角要更勇敢一点       # 修改细节
> 重新生成              # 完全重来
> 不要爱情线            # 删除元素

确认点3 - 分镜脚本:
> ok
> 镜头太多了，减少一点
> 第3个镜头改成特写
> 增加一个过渡镜头
```

## 9. 断点恢复设计

### 9.1 状态持久化

每个 Agent 操作后，状态保存到数据库：

```python
# 新增表: agent_sessions
CREATE TABLE agent_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    user_request TEXT,
    mode TEXT,  -- interactive / auto
    current_step TEXT,
    state_json TEXT,  -- 完整状态快照
    status TEXT,  -- running / paused / completed / failed
    error_message TEXT,
    created_at TEXT,
    updated_at TEXT
);

# 新增表: agent_checkpoints
CREATE TABLE agent_checkpoints (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    step_name TEXT,
    input_json TEXT,
    output_json TEXT,
    created_at TEXT,
    FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id)
);
```

### 9.2 恢复流程

```python
class SupervisorAgent:
    async def resume(self, session_id: str):
        """从断点恢复执行"""
        # 1. 加载会话状态
        session = db.get_agent_session(session_id)
        checkpoints = db.get_agent_checkpoints(session_id)

        # 2. 恢复到最后一个成功的检查点
        last_checkpoint = checkpoints[-1]

        # 3. 继续执行
        return await self._continue_from_checkpoint(session, last_checkpoint)
```

## 10. 目录结构

```
movie_generator/
├── src/
│   ├── story_generator/          # ✅ 现有 - 保留
│   │
│   ├── providers/                # ✅ 现有 - 保留
│   │
│   ├── comparison/               # ✅ 现有 - 保留
│   │
│   ├── mcp_servers/              # 🆕 新增
│   │   ├── __init__.py
│   │   ├── project_server.py     # 项目/角色/剧集 CRUD
│   │   ├── storyboard_server.py  # 分镜 CRUD
│   │   └── video_server.py       # 视频生成 API 封装
│   │
│   ├── agents/                   # 🆕 新增
│   │   ├── __init__.py
│   │   ├── supervisor.py         # 总监督者
│   │   ├── story_writer.py       # 编剧 Agent
│   │   ├── character_designer.py # 角色设计 Agent
│   │   ├── director.py           # 分镜师 Agent
│   │   ├── video_producer.py     # 视频师 Agent
│   │   ├── state.py              # Agent 状态定义
│   │   └── graph.py              # LangGraph 图定义
│   │
│   └── skills/                   # 🆕 新增
│       ├── __init__.py
│       ├── loader.py
│       ├── writing/
│       │   ├── story_outline.md
│       │   ├── random_idea.md
│       │   └── genres/*.md
│       ├── character/
│       │   └── *.md
│       ├── directing/
│       │   └── *.md
│       └── video/
│           ├── platforms/*.md
│           └── prompt_types/*.md
│
├── scripts/
│   ├── run_mcp_servers.py        # 启动所有 MCP 服务器
│   ├── run_agent.py              # 启动 Agent 系统
│   └── run_interactive.py        # 交互式运行
│
└── tests/
    ├── test_mcp_servers/
    ├── test_agents/
    └── test_skills/
```

## 11. 实施计划

### Phase 1: MCP 服务器 (1-2周) ✅ 已完成

**Week 1:**
- [x] 搭建 FastMCP 项目结构
- [x] 实现 Project Server（复用 database.py）- 17 tools
- [x] 实现 Storyboard Server - 12 tools
- [x] 实现 Video Server（复用 providers/*）- 10 tools
- [x] 测试脚本 (scripts/test_mcp_servers.py)

**已实现的文件:**
```
src/mcp_servers/
├── __init__.py
├── project_server.py    # Project/Character/Episode CRUD
├── storyboard_server.py # Shot/Storyboard operations
└── video_server.py      # Video generation via providers

scripts/
├── run_mcp_servers.py   # 运行单个MCP服务器
└── test_mcp_servers.py  # 测试脚本
```

**运行方式:**
```bash
# 激活虚拟环境
source venv/bin/activate

# 列出所有可用服务器和工具
python scripts/run_mcp_servers.py --list

# 运行测试
python scripts/test_mcp_servers.py

# 运行单个服务器 (STDIO模式)
python scripts/run_mcp_servers.py project
python scripts/run_mcp_servers.py storyboard
python scripts/run_mcp_servers.py video
```

**使用 MCP Inspector 测试:**
```bash
# 安装 MCP Inspector (如果还没有)
npm install -g @anthropic/mcp-inspector

# 测试 Project Server
mcp-inspector python scripts/run_mcp_servers.py project

# 测试 Storyboard Server
mcp-inspector python scripts/run_mcp_servers.py storyboard

# 测试 Video Server
mcp-inspector python scripts/run_mcp_servers.py video
```

### Phase 2: Skills 系统 (1周) ✅ 已完成

**Week 3:**
- [x] 设计 Skill 文件格式（Markdown with metadata sections）
- [x] 从 gemini_client.py 迁移提示词到 Skills
- [x] 实现 Skill Loader（支持缓存、元数据解析、变量替换）
- [x] 创建各类型 Skills（写作、分镜、平台指南）

**已实现的文件:**
```
src/skills/
├── __init__.py
├── loader.py                    # Skill 加载器
│
├── writing/                     # 编剧 Skills
│   ├── story_outline.md         # 故事大纲生成
│   ├── random_idea.md           # 随机创意生成
│   └── consistency_check.md     # 一致性检查与修复
│
├── character/                   # 角色设计 Skills
│   └── character_events.md      # 角色事件分析
│
├── directing/                   # 分镜 Skills
│   ├── storyboard.md           # 分镜脚本生成
│   └── shot_description.md     # 镜头描述优化
│
└── video/                       # 视频生成 Skills
    ├── prompt_generation.md     # 提示词生成通用指南
    └── platforms/               # 平台特化指南
        ├── kling.md            # 可灵平台
        ├── hailuo.md           # 海螺平台（运镜指令）
        ├── jimeng.md           # 即梦平台
        └── tongyi.md           # 通义万相平台
```

**使用方式:**
```python
from skills import get_skill_loader

loader = get_skill_loader()

# 列出所有 Skills
skills = loader.list_skills()  # ['writing/story_outline', ...]

# 加载 Skill
content = loader.load_skill('writing/story_outline')

# 加载并替换变量
content = loader.load_skill_with_variables('video/prompt_generation',
    platform='kling',
    visual_description='...'
)

# 获取元数据
metadata = loader.get_metadata('writing/story_outline')
print(metadata.applicable_agents)  # ['story_writer', 'supervisor']
print(metadata.available_tools)    # ['create_project', ...]
```

### Phase 3: Agent 实现 (2周) ✅ 已完成

**Week 4-5:**
- [x] 搭建 LangGraph 项目结构
- [x] 实现 Agent 状态定义 (state.py)
- [x] 实现 BaseAgent 基类 (base.py)
- [x] 实现 Supervisor Agent
- [x] 实现 Story Writer Agent
- [x] 实现 Director Agent
- [x] 实现 Video Producer Agent
- [x] 实现 LangGraph Workflow (graph.py)
- [x] Agent 协作流程测试

**已实现的文件:**
```
src/agents/
├── __init__.py          # 包导出
├── state.py             # AgentState, WorkflowPhase, InteractionMode
├── base.py              # BaseAgent 基类 (LLM调用, Skill加载)
├── story_writer.py      # StoryWriterAgent (大纲/角色/剧集)
├── director.py          # DirectorAgent (分镜)
├── video_producer.py    # VideoProducerAgent (视频提示词/生成)
├── supervisor.py        # SupervisorAgent (工作流协调)
└── graph.py             # LangGraph Workflow, WorkflowRunner
```

**使用方式:**
```python
from agents import WorkflowRunner, InteractionMode

# 创建运行器
runner = WorkflowRunner()

# 启动工作流 (交互模式)
state = runner.start(
    idea="一个机器人学会了爱",
    genre="科幻",
    num_episodes=1,
    episode_duration=60,
    mode=InteractionMode.INTERACTIVE,
)

# 工作流会在每个检查点暂停，等待用户确认
print(runner.get_summary())

# 批准并继续
if state.get("pending_approval"):
    state = runner.approve_and_continue(approved=True)
```

**测试:**
```bash
source venv/bin/activate
python scripts/test_agents.py
```

### Phase 4: 交互与恢复 (1周) ✅ 已完成

**Week 6:**
- [x] Human-in-the-loop 实现
- [x] 断点恢复机制 (Session Management)
- [x] 状态持久化 (SQLite)
- [x] CLI 工具开发

**已实现的文件:**
```
src/agents/
├── session.py           # SessionManager, Session, Checkpoint, SessionStatus

scripts/
├── run_workflow.py      # 交互式CLI工具
└── test_session.py      # Session测试脚本
```

**数据库新增表:**
```sql
-- Agent会话表
CREATE TABLE agent_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    user_request TEXT,
    mode TEXT,
    current_phase TEXT,
    current_agent TEXT,
    project_id INTEGER,
    state_json TEXT,
    status TEXT,
    error_message TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Agent检查点表
CREATE TABLE agent_checkpoints (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    step_name TEXT,
    phase TEXT,
    input_json TEXT,
    output_json TEXT,
    created_at TEXT
);
```

**使用方式:**
```bash
# 激活环境
source venv/bin/activate

# 启动新工作流
python scripts/run_workflow.py start "一个机器人学会了爱" --genre 科幻 --episodes 1

# 列出会话
python scripts/run_workflow.py list

# 恢复暂停的会话（也支持从失败状态恢复重试）
python scripts/run_workflow.py resume <session_id>

# 交互模式
python scripts/run_workflow.py interactive

# 查看会话详情
python scripts/run_workflow.py info <session_id>
```

**Python API:**
```python
from agents import PersistentWorkflowRunner, InteractionMode

# 创建运行器（带持久化）
runner = PersistentWorkflowRunner()

# 启动工作流
result = runner.start(
    idea="一个机器人学会了爱",
    genre="科幻",
    mode=InteractionMode.INTERACTIVE,
)
session_id = result['session_id']

# 批准并继续
result = runner.approve_and_continue(approved=True)

# 稍后恢复
result = runner.resume(session_id)

# 列出会话
sessions = runner.list_sessions(status="paused")
```

### Phase 5: 集成测试 (1周) ✅ 已完成

**Week 7:**
- [x] 端到端测试
- [x] 多场景测试 (交互模式、会话恢复、错误处理)
- [x] 文档完善
- [x] 模块README

**已实现的文件:**
```
scripts/
├── test_e2e.py          # 端到端测试脚本

src/agents/
└── README.md            # Agent模块文档
```

**测试覆盖:**
```bash
# 运行所有测试
source venv/bin/activate

# Agent单元测试
python scripts/test_agents.py      # 7/7 passed

# Session管理测试
python scripts/test_session.py     # 5/5 passed

# 端到端测试
python scripts/test_e2e.py         # 4/4 passed
```

**测试场景:**
1. Full Workflow (Interactive) - 完整工作流自动审批
2. Session Recovery - 会话暂停与恢复
3. Autonomous Mode - 自动模式配置
4. Error Handling - 用户拒绝与错误处理
5. Chinese Characters - 中文角色设计
6. Resume From Error - 从错误状态恢复重试

**新增功能:**
- 角色设计技能 (`skills/character/character_design.md`)
- 语言检测：中文输入自动使用中文角色名
- 改进的角色信息解析
- 从错误状态恢复：支持 `resume` 命令恢复失败的会话
- SSL/连接错误自动重试逻辑
- 部分进度保存：视频生成失败时保存已提交的任务

## 12. 依赖包

```
# requirements.txt (新增)

# MCP
fastmcp>=2.0.0

# LangChain / LangGraph
langgraph>=0.2.0
langchain>=0.3.0
langchain-google-genai>=2.0.0
langchain-mcp-adapters>=0.1.0

# 现有依赖保留
google-genai>=1.0.0
streamlit>=1.28.0
pyyaml>=6.0
requests>=2.31.0
pyjwt>=2.8.0
```

---

*文档版本: 3.0 (完成版)*
*创建日期: 2026-01-27*
*更新日期: 2026-01-31*
*Phase 1 完成日期: 2026-01-29*
*Phase 2 完成日期: 2026-01-29*
*Phase 3 完成日期: 2026-01-31*
*Phase 4 完成日期: 2026-01-31*
*Phase 5 完成日期: 2026-01-31*

## 项目完成状态: ✅ 全部完成
