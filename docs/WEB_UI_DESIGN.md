# Web UI 设计文档

## 1. 项目概述

将现有的命令行工作流系统升级为完整的 Web 应用，提供精美的用户界面和良好的交互体验。

### 1.1 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Next.js 14 | React 框架，App Router |
| UI组件 | shadcn/ui + Tailwind CSS | 现代化组件库 |
| 状态管理 | Zustand | 轻量级状态管理 |
| 国际化 | next-intl | 完整 i18n 支持（中/英文） |
| 后端 | FastAPI | Python 异步 API 框架 |
| 数据库 | SQLite | 复用现有数据库 |
| 实时通信 | WebSocket | 工作流进度推送 |
| 任务队列 | 内置 asyncio | 异步任务处理 |

### 1.2 设计原则

- **最大化复用**: 直接使用现有的 agents、providers、database 模块
- **渐进式交互**: 工作流每个阶段都可审核、编辑、重试
- **实时反馈**: WebSocket 推送工作流进度，浏览器通知
- **响应式设计**: 当前支持桌面和平板设备
- **完整国际化**: 使用 i18n 实现中英文切换

### 1.3 设计决策

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 用户模式 | 单用户 | 无需登录认证 |
| 数据库 | SQLite | 保持现有方案 |
| 视频存储 | 本地文件 | 下载到 output/ 目录 |
| API 密钥 | 服务端统一配置 | 通过 config.local.yaml |
| 移动端 | 未来支持 | 记录在 Roadmap |

### 1.4 功能对照（参考 story_generator.md）

| 现有功能 | Web UI 实现 |
|----------|-------------|
| 故事创意生成 | 新建工作流页面 |
| 故事大纲生成 | 工作流自动生成 + 审核 |
| 人物知识库 | 角色编辑器 + 重大经历追踪 |
| 分镜脚本生成 | 分镜编辑器 + 密度控制 |
| 视频提示词生成 | 提示词编辑器 + 多平台支持 |
| 剧集大纲编辑 | 直接编辑 + AI 辅助编辑 |
| 一致性检查 | 自动检测 + 修复建议 |
| 编辑历史 | 撤销/重做功能 |
| 一键导出 | 导出 Markdown |
| Admin 功能 | 设置页面（API日志、模板管理） |

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js Frontend                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ 项目列表 │ │ 工作流  │ │ 内容查看 │ │ 视频管理 │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ REST API    │ │ WebSocket   │ │ Background  │           │
│  │ Endpoints   │ │ Handler     │ │ Tasks       │           │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘           │
└─────────┼───────────────┼───────────────┼───────────────────┘
          │               │               │
┌─────────▼───────────────▼───────────────▼───────────────────┐
│                    现有 Python 模块                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ agents/     │ │ providers/  │ │ story_      │           │
│  │ 工作流引擎  │ │ 视频生成    │ │ generator/  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 3. 目录结构

```
movie_generator/
├── api/                          # FastAPI 后端
│   ├── main.py                   # 应用入口
│   ├── config.py                 # 配置管理
│   ├── routers/
│   │   ├── sessions.py           # 会话管理 API
│   │   ├── workflows.py          # 工作流 API
│   │   ├── projects.py           # 项目 API
│   │   └── videos.py             # 视频 API
│   ├── services/
│   │   ├── workflow_service.py   # 工作流服务
│   │   └── video_service.py      # 视频服务
│   ├── schemas/
│   │   ├── session.py            # 会话模型
│   │   ├── workflow.py           # 工作流模型
│   │   └── video.py              # 视频模型
│   └── websocket/
│       └── handler.py            # WebSocket 处理
│
├── web/                          # Next.js 前端
│   ├── app/
│   │   ├── layout.tsx            # 根布局
│   │   ├── page.tsx              # 首页
│   │   ├── projects/
│   │   │   ├── page.tsx          # 项目列表
│   │   │   └── [id]/
│   │   │       └── page.tsx      # 项目详情
│   │   ├── workflow/
│   │   │   ├── new/
│   │   │   │   └── page.tsx      # 新建工作流
│   │   │   └── [sessionId]/
│   │   │       └── page.tsx      # 工作流详情
│   │   └── videos/
│   │       └── [sessionId]/
│   │           └── page.tsx      # 视频管理
│   ├── components/
│   │   ├── ui/                   # shadcn 组件
│   │   ├── workflow/             # 工作流组件
│   │   ├── editor/               # 编辑器组件
│   │   └── video/                # 视频组件
│   ├── lib/
│   │   ├── api.ts                # API 客户端
│   │   ├── websocket.ts          # WebSocket 客户端
│   │   └── utils.ts              # 工具函数
│   └── stores/
│       └── workflow.ts           # 工作流状态
│
└── src/                          # 现有模块 (不变)
    ├── agents/
    ├── providers/
    └── story_generator/
```

## 4. 后端 API 设计

### 4.1 REST API 端点

#### 会话管理

```
POST   /api/sessions              # 创建新会话（启动工作流）
GET    /api/sessions              # 列出所有会话
GET    /api/sessions/{id}         # 获取会话详情
DELETE /api/sessions/{id}         # 删除会话
POST   /api/sessions/{id}/resume  # 恢复会话
POST   /api/sessions/{id}/approve # 审批并继续
POST   /api/sessions/{id}/reject  # 拒绝并停止
```

#### 工作流内容

```
GET    /api/sessions/{id}/outline    # 获取故事大纲
GET    /api/sessions/{id}/characters # 获取角色列表
GET    /api/sessions/{id}/episodes   # 获取剧集列表
GET    /api/sessions/{id}/storyboard # 获取分镜列表
GET    /api/sessions/{id}/prompts    # 获取视频提示词
PUT    /api/sessions/{id}/outline    # 编辑故事大纲
PUT    /api/sessions/{id}/characters/{idx} # 编辑角色
PUT    /api/sessions/{id}/storyboard/{idx} # 编辑分镜
```

#### 视频管理

```
GET    /api/sessions/{id}/videos         # 获取视频任务列表
POST   /api/sessions/{id}/videos/refresh # 刷新视频状态
GET    /api/sessions/{id}/videos/download # 下载所有视频
```

### 4.2 WebSocket 事件

```typescript
// 客户端 -> 服务端
{ type: "subscribe", sessionId: string }
{ type: "unsubscribe", sessionId: string }

// 服务端 -> 客户端
{ type: "phase_changed", phase: string, data: object }
{ type: "approval_required", approvalType: string, data: object }
{ type: "progress", message: string, progress: number }
{ type: "error", message: string }
{ type: "completed", summary: object }
{ type: "video_status", shotId: string, status: string, url?: string }
```

### 4.3 数据模型 (Pydantic Schemas)

```python
# api/schemas/session.py

class CreateSessionRequest(BaseModel):
    idea: str
    genre: str = "drama"
    style: str = ""
    num_episodes: int = 1
    episode_duration: int = 60
    num_characters: int = 3
    target_platform: str = "kling"
    mode: str = "interactive"  # interactive | autonomous

class SessionResponse(BaseModel):
    session_id: str
    status: str  # running | paused | completed | failed
    phase: str
    project_name: str
    created_at: datetime
    updated_at: datetime
    error: Optional[str]

class SessionDetailResponse(SessionResponse):
    story_outline: Optional[dict]
    characters: List[dict]
    episodes: List[dict]
    storyboard: List[dict]
    video_prompts: dict
    video_tasks: dict
    pending_approval: bool
    approval_type: str

class ApproveRequest(BaseModel):
    approved: bool = True
    feedback: str = ""
    edits: Optional[dict] = None  # 可选的编辑内容
```

### 4.4 核心服务实现

```python
# api/services/workflow_service.py

from agents import PersistentWorkflowRunner, SessionManager
from typing import Dict, Any, Optional
import asyncio

class WorkflowService:
    def __init__(self):
        self.runners: Dict[str, PersistentWorkflowRunner] = {}
        self.session_manager = SessionManager()

    async def create_session(self, request: CreateSessionRequest) -> Dict[str, Any]:
        """创建新工作流会话"""
        runner = PersistentWorkflowRunner()

        # 在后台线程运行（因为 LangGraph 是同步的）
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: runner.start(
                idea=request.idea,
                genre=request.genre,
                style=request.style,
                num_episodes=request.num_episodes,
                episode_duration=request.episode_duration,
                num_characters=request.num_characters,
                target_platform=request.target_platform,
                mode=request.mode,
            )
        )

        session_id = result["session_id"]
        self.runners[session_id] = runner
        return result

    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """恢复会话"""
        runner = PersistentWorkflowRunner()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: runner.resume(session_id)
        )

        self.runners[session_id] = runner
        return result

    async def approve_and_continue(
        self,
        session_id: str,
        approved: bool,
        feedback: str = ""
    ) -> Dict[str, Any]:
        """审批并继续工作流"""
        runner = self.runners.get(session_id)
        if not runner:
            runner = PersistentWorkflowRunner()
            await self.resume_session(session_id)
            runner = self.runners[session_id]

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: runner.approve_and_continue(approved, feedback)
        )
        return result

    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        state = self.session_manager.load_state(session_id)
        if state:
            return {
                "story_outline": state.story_outline,
                "characters": state.characters,
                "episodes": state.episodes,
                "storyboard": state.storyboard,
                "video_prompts": state.video_prompts,
                "video_tasks": state.video_tasks,
                "phase": state.phase.value,
                "pending_approval": state.pending_approval,
                "approval_type": state.approval_type,
            }
        return None
```

## 5. 前端页面设计

### 5.1 页面结构

#### 首页 (/)
- 项目统计卡片（总项目数、进行中、已完成）
- 快速开始按钮
- 最近项目列表

#### 新建工作流 (/workflow/new)
```
┌─────────────────────────────────────────────────────────────┐
│  🎬 创建新项目                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  故事创意 *                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 一个机器人在末日世界中寻找人类最后的希望...           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ 类型         │  │ 集数         │  │ 每集时长     │     │
│  │ [科幻    ▼] │  │ [1       ▼] │  │ [60秒    ▼] │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ 角色数量     │  │ 视频平台     │                        │
│  │ [3       ▼] │  │ [可灵    ▼] │                        │
│  └──────────────┘  └──────────────┘                        │
│                                                             │
│  风格描述（可选）                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 赛博朋克风格，霓虹灯光，雨夜氛围                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ☑ 交互模式（每个阶段需要审核）                             │
│  ☐ 自动模式（全自动生成）                                   │
│                                                             │
│                              ┌─────────────────────────┐   │
│                              │     🚀 开始创作         │   │
│                              └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 工作流详情 (/workflow/[sessionId])
```
┌─────────────────────────────────────────────────────────────┐
│  ← 返回    钢铁防线                           状态: 进行中   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ● 故事大纲 ─── ● 角色设计 ─── ○ 剧集 ─── ○ 分镜 ─── ○ 视频 │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    当前阶段: 角色设计                  │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ 角色 1: 林浩                                     │ │   │
│  │  │ 年龄: 28岁                                       │ │   │
│  │  │ 性格: 沉稳、果断、富有责任感                      │ │   │
│  │  │ 外貌: 短发，眼神坚毅，穿着机甲驾驶服              │ │   │
│  │  │                                    [编辑] [删除] │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ 角色 2: 苏晴                                     │ │   │
│  │  │ ...                                              │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ + 添加角色                                       │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   ✗ 拒绝重做    │  │   ✓ 通过继续    │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

#### 分镜查看 (Storyboard View)
```
┌─────────────────────────────────────────────────────────────┐
│  分镜脚本 - 第1集                              共 12 个镜头  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ 镜头 1  │ │ 镜头 2  │ │ 镜头 3  │ │ 镜头 4  │          │
│  │ ┌─────┐ │ │ ┌─────┐ │ │ ┌─────┐ │ │ ┌─────┐ │          │
│  │ │ 🎬  │ │ │ │ 🎬  │ │ │ │ 🎬  │ │ │ │ 🎬  │ │          │
│  │ └─────┘ │ │ └─────┘ │ │ └─────┘ │ │ └─────┘ │          │
│  │ 5秒     │ │ 8秒     │ │ 6秒     │ │ 5秒     │          │
│  │ 远景    │ │ 中景    │ │ 特写    │ │ 跟踪    │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 镜头 1 详情                                    [编辑] │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ 时长: 5秒  |  类型: 远景  |  运动: 缓慢推进          │   │
│  │                                                       │   │
│  │ 画面描述:                                             │   │
│  │ 末日后的城市废墟，天空呈现暗红色，远处有巨大的机甲    │   │
│  │ 残骸，主角林浩站在高处俯瞰整个城市...                 │   │
│  │                                                       │   │
│  │ 视频提示词:                                           │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │ Cinematic wide shot, post-apocalyptic city...   │ │   │
│  │ └─────────────────────────────────────────────────┘ │   │
│  │                                         [复制] [编辑] │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

#### 视频管理 (/videos/[sessionId])
```
┌─────────────────────────────────────────────────────────────┐
│  视频生成 - 钢铁防线                    平台: 可灵           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 总进度: ████████████░░░░░░░░ 8/12 完成              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ 镜头 1  │ │ 镜头 2  │ │ 镜头 3  │ │ 镜头 4  │          │
│  │ ┌─────┐ │ │ ┌─────┐ │ │ ┌─────┐ │ │ ┌─────┐ │          │
│  │ │ ▶️  │ │ │ │ ▶️  │ │ │ │ ⏳  │ │ │ │ ⏳  │ │          │
│  │ └─────┘ │ │ └─────┘ │ │ └─────┘ │ │ └─────┘ │          │
│  │ ✓ 完成  │ │ ✓ 完成  │ │ 生成中  │ │ 等待中  │          │
│  │ [下载]  │ │ [下载]  │ │ 45%     │ │         │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 镜头 1 预览                                          │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │                                                   │ │   │
│  │ │                    [视频播放器]                   │ │   │
│  │ │                                                   │ │   │
│  │ └─────────────────────────────────────────────────┘ │   │
│  │                                                       │   │
│  │ [下载视频]  [重新生成]  [查看提示词]                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │     [刷新状态]     [下载全部]     [导出项目]         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 核心组件

```typescript
// web/components/workflow/WorkflowProgress.tsx
// 工作流进度条组件

interface WorkflowProgressProps {
  currentPhase: string;
  phases: string[];
}

// web/components/workflow/ApprovalPanel.tsx
// 审批面板组件

interface ApprovalPanelProps {
  approvalType: string;
  data: any;
  onApprove: () => void;
  onReject: (feedback: string) => void;
  onEdit: (edits: any) => void;
}

// web/components/editor/CharacterEditor.tsx
// 角色编辑器组件

interface CharacterEditorProps {
  character: Character;
  onChange: (character: Character) => void;
  onDelete: () => void;
}

// web/components/editor/StoryboardEditor.tsx
// 分镜编辑器组件

interface StoryboardEditorProps {
  shots: Shot[];
  selectedIndex: number;
  onSelect: (index: number) => void;
  onEdit: (index: number, shot: Shot) => void;
}

// web/components/video/VideoGrid.tsx
// 视频网格组件

interface VideoGridProps {
  tasks: VideoTask[];
  onRefresh: () => void;
  onDownload: (shotId: string) => void;
  onRegenerate: (shotId: string) => void;
}

// web/components/video/VideoPlayer.tsx
// 视频播放器组件

interface VideoPlayerProps {
  url: string;
  poster?: string;
  onEnded?: () => void;
}
```

### 5.3 状态管理

```typescript
// web/stores/workflow.ts

import { create } from 'zustand';

interface WorkflowState {
  // 会话信息
  sessionId: string | null;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'failed';
  phase: string;

  // 工作流数据
  storyOutline: StoryOutline | null;
  characters: Character[];
  episodes: Episode[];
  storyboard: Shot[];
  videoPrompts: Record<string, string>;
  videoTasks: Record<string, VideoTask>;

  // 审批状态
  pendingApproval: boolean;
  approvalType: string;

  // 操作
  setSession: (sessionId: string) => void;
  updatePhase: (phase: string) => void;
  setStoryOutline: (outline: StoryOutline) => void;
  setCharacters: (characters: Character[]) => void;
  updateCharacter: (index: number, character: Character) => void;
  setStoryboard: (shots: Shot[]) => void;
  updateShot: (index: number, shot: Shot) => void;
  setVideoTasks: (tasks: Record<string, VideoTask>) => void;
  updateVideoTask: (shotId: string, task: VideoTask) => void;
  reset: () => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  sessionId: null,
  status: 'idle',
  phase: 'init',
  storyOutline: null,
  characters: [],
  episodes: [],
  storyboard: [],
  videoPrompts: {},
  videoTasks: {},
  pendingApproval: false,
  approvalType: '',

  setSession: (sessionId) => set({ sessionId }),
  updatePhase: (phase) => set({ phase }),
  // ... 其他操作实现
  reset: () => set({
    sessionId: null,
    status: 'idle',
    phase: 'init',
    storyOutline: null,
    characters: [],
    episodes: [],
    storyboard: [],
    videoPrompts: {},
    videoTasks: {},
    pendingApproval: false,
    approvalType: '',
  }),
}));
```

### 5.4 WebSocket 客户端

```typescript
// web/lib/websocket.ts

class WorkflowWebSocket {
  private ws: WebSocket | null = null;
  private sessionId: string | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  connect(url: string) {
    this.ws = new WebSocket(url);

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.emit(message.type, message);
    };

    this.ws.onclose = () => {
      // 自动重连逻辑
      setTimeout(() => this.connect(url), 3000);
    };
  }

  subscribe(sessionId: string) {
    this.sessionId = sessionId;
    this.send({ type: 'subscribe', sessionId });
  }

  unsubscribe() {
    if (this.sessionId) {
      this.send({ type: 'unsubscribe', sessionId: this.sessionId });
      this.sessionId = null;
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: (data: any) => void) {
    this.listeners.get(event)?.delete(callback);
  }

  private emit(event: string, data: any) {
    this.listeners.get(event)?.forEach(cb => cb(data));
  }

  private send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

export const workflowWS = new WorkflowWebSocket();
```

## 6. API 路由实现

### 6.1 FastAPI 主入口

```python
# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from .routers import sessions, videos
from .websocket.handler import websocket_endpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    print("Starting API server...")
    yield
    # 关闭时清理
    print("Shutting down...")

app = FastAPI(
    title="AI Movie Generator API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])

# WebSocket 端点
app.websocket("/ws")(websocket_endpoint)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
```

### 6.2 会话路由

```python
# api/routers/sessions.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from ..schemas.session import (
    CreateSessionRequest,
    SessionResponse,
    SessionDetailResponse,
    ApproveRequest
)
from ..services.workflow_service import WorkflowService

router = APIRouter()
workflow_service = WorkflowService()

@router.post("", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest, background_tasks: BackgroundTasks):
    """创建新的工作流会话"""
    try:
        result = await workflow_service.create_session(request)
        return SessionResponse(
            session_id=result["session_id"],
            status="running",
            phase=result["summary"]["phase"],
            project_name=result["summary"].get("project_name", ""),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[SessionResponse])
async def list_sessions(status: Optional[str] = None, limit: int = 20):
    """列出所有会话"""
    sessions = workflow_service.session_manager.list_sessions(
        status=status,
        limit=limit
    )
    return [
        SessionResponse(
            session_id=s.session_id,
            status=s.status.value,
            phase=s.current_phase,
            project_name="",  # 从 state 获取
            created_at=s.created_at,
            updated_at=s.updated_at,
            error=s.error_message
        )
        for s in sessions
    ]

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str):
    """获取会话详情"""
    session = workflow_service.session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    state = workflow_service.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session state not found")

    return SessionDetailResponse(
        session_id=session_id,
        status=session.status.value,
        phase=state["phase"],
        project_name=state.get("project_name", ""),
        created_at=session.created_at,
        updated_at=session.updated_at,
        error=session.error_message,
        story_outline=state.get("story_outline"),
        characters=state.get("characters", []),
        episodes=state.get("episodes", []),
        storyboard=state.get("storyboard", []),
        video_prompts=state.get("video_prompts", {}),
        video_tasks=state.get("video_tasks", {}),
        pending_approval=state.get("pending_approval", False),
        approval_type=state.get("approval_type", "")
    )

@router.post("/{session_id}/resume")
async def resume_session(session_id: str):
    """恢复暂停或失败的会话"""
    try:
        result = await workflow_service.resume_session(session_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/approve")
async def approve_session(session_id: str, request: ApproveRequest):
    """审批并继续工作流"""
    try:
        result = await workflow_service.approve_and_continue(
            session_id,
            request.approved,
            request.feedback
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    workflow_service.session_manager.delete_session(session_id)
    return {"status": "deleted"}
```

### 6.3 WebSocket 处理

```python
# api/websocket/handler.py

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # session_id -> set of websocket connections
        self.subscriptions: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    def subscribe(self, session_id: str, websocket: WebSocket):
        if session_id not in self.subscriptions:
            self.subscriptions[session_id] = set()
        self.subscriptions[session_id].add(websocket)

    def unsubscribe(self, session_id: str, websocket: WebSocket):
        if session_id in self.subscriptions:
            self.subscriptions[session_id].discard(websocket)

    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.subscriptions:
            for ws in self.subscriptions[session_id]:
                try:
                    await ws.send_json(message)
                except:
                    pass

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    subscribed_sessions: Set[str] = set()

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "subscribe":
                session_id = data.get("sessionId")
                if session_id:
                    manager.subscribe(session_id, websocket)
                    subscribed_sessions.add(session_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "sessionId": session_id
                    })

            elif msg_type == "unsubscribe":
                session_id = data.get("sessionId")
                if session_id:
                    manager.unsubscribe(session_id, websocket)
                    subscribed_sessions.discard(session_id)

    except WebSocketDisconnect:
        for session_id in subscribed_sessions:
            manager.unsubscribe(session_id, websocket)

# 用于从其他地方发送消息
async def notify_session(session_id: str, event_type: str, data: dict):
    await manager.broadcast(session_id, {
        "type": event_type,
        **data
    })
```

## 7. 视频生成与重试机制

### 7.1 视频重试场景

支持三种重试方式：

```typescript
// 1. 仅重试失败的视频（保持原提示词）
POST /api/sessions/{id}/videos/{shotId}/retry

// 2. 编辑提示词后重试
PUT /api/sessions/{id}/prompts/{shotId}
POST /api/sessions/{id}/videos/{shotId}/retry

// 3. 切换平台重试
POST /api/sessions/{id}/videos/{shotId}/retry?platform=hailuo
```

### 7.2 多平台对比生成

支持同时向多个平台提交生成，对比效果：

```typescript
// API: 多平台生成
POST /api/sessions/{id}/videos/compare
{
  "shotIds": ["ep1_shot1", "ep1_shot2"],
  "platforms": ["kling", "hailuo", "jimeng"]
}

// 响应
{
  "tasks": {
    "ep1_shot1": {
      "kling": { "taskId": "...", "status": "processing" },
      "hailuo": { "taskId": "...", "status": "processing" },
      "jimeng": { "taskId": "...", "status": "processing" }
    }
  }
}
```

### 7.3 视频管理 UI 更新

```
┌─────────────────────────────────────────────────────────────┐
│  镜头 1 - 多平台对比                                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   可灵      │ │   海螺      │ │   即梦      │           │
│  │  ┌───────┐  │ │  ┌───────┐  │ │  ┌───────┐  │           │
│  │  │  ▶️   │  │ │  │  ▶️   │  │ │  │  ⏳   │  │           │
│  │  └───────┘  │ │  └───────┘  │ │  └───────┘  │           │
│  │  ✓ 完成     │ │  ✓ 完成     │ │  生成中 60% │           │
│  │  [选用]     │ │  [选用]     │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                             │
│  [重新生成全部]  [编辑提示词]  [切换平台重试]               │
└─────────────────────────────────────────────────────────────┘
```

## 8. 浏览器通知

### 8.1 通知场景

| 场景 | 通知内容 |
|------|----------|
| 视频生成完成 | "镜头 X 视频已生成完成" |
| 全部视频完成 | "项目《XXX》所有视频已生成完成" |
| 生成失败 | "镜头 X 生成失败：错误信息" |
| 需要审批 | "项目《XXX》等待审批：角色设计" |

### 8.2 实现方式

```typescript
// web/lib/notifications.ts

export async function requestNotificationPermission() {
  if ('Notification' in window) {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }
  return false;
}

export function showNotification(title: string, options?: NotificationOptions) {
  if ('Notification' in window && Notification.permission === 'granted') {
    const notification = new Notification(title, {
      icon: '/icon.png',
      badge: '/badge.png',
      ...options,
    });

    notification.onclick = () => {
      window.focus();
      notification.close();
    };

    return notification;
  }
}

// 在 WebSocket 消息处理中使用
workflowWS.on('video_status', (data) => {
  if (data.status === 'completed') {
    showNotification('视频生成完成', {
      body: `镜头 ${data.shotId} 已生成完成`,
      tag: data.shotId,
    });
  }
});

workflowWS.on('approval_required', (data) => {
  showNotification('需要审批', {
    body: `${data.projectName} 等待审批：${data.approvalType}`,
    tag: data.sessionId,
  });
});
```

## 9. 国际化 (i18n)

### 9.1 目录结构

```
web/
├── messages/
│   ├── en.json          # 英文翻译
│   └── zh.json          # 中文翻译
├── i18n.ts              # i18n 配置
└── middleware.ts        # 语言检测中间件
```

### 9.2 翻译文件示例

```json
// messages/zh.json
{
  "common": {
    "save": "保存",
    "cancel": "取消",
    "delete": "删除",
    "edit": "编辑",
    "confirm": "确认",
    "loading": "加载中...",
    "error": "错误",
    "success": "成功"
  },
  "workflow": {
    "title": "创建新项目",
    "idea": "故事创意",
    "ideaPlaceholder": "输入你的故事创意...",
    "genre": "类型",
    "episodes": "集数",
    "duration": "每集时长",
    "characters": "角色数量",
    "platform": "视频平台",
    "style": "风格描述",
    "stylePlaceholder": "描述视觉风格（可选）",
    "interactiveMode": "交互模式（每个阶段需要审核）",
    "autonomousMode": "自动模式（全自动生成）",
    "start": "开始创作"
  },
  "phases": {
    "init": "初始化",
    "story_outline": "故事大纲",
    "character_design": "角色设计",
    "episode_writing": "剧集编写",
    "storyboard": "分镜脚本",
    "video_prompts": "视频提示词",
    "video_generation": "视频生成",
    "review": "审核",
    "completed": "已完成",
    "error": "错误"
  },
  "approval": {
    "approve": "通过",
    "reject": "拒绝",
    "feedback": "反馈意见",
    "feedbackPlaceholder": "请输入修改建议..."
  },
  "video": {
    "status": "状态",
    "platform": "平台",
    "download": "下载",
    "regenerate": "重新生成",
    "compare": "多平台对比",
    "selectPlatform": "选择平台",
    "processing": "生成中",
    "completed": "已完成",
    "failed": "失败",
    "pending": "等待中"
  },
  "genres": {
    "drama": "剧情",
    "comedy": "喜剧",
    "action": "动作",
    "sci-fi": "科幻",
    "fantasy": "奇幻",
    "romance": "爱情",
    "horror": "恐怖",
    "thriller": "悬疑"
  },
  "platforms": {
    "kling": "可灵",
    "hailuo": "海螺",
    "jimeng": "即梦",
    "tongyi": "通义万相"
  }
}
```

```json
// messages/en.json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "confirm": "Confirm",
    "loading": "Loading...",
    "error": "Error",
    "success": "Success"
  },
  "workflow": {
    "title": "Create New Project",
    "idea": "Story Idea",
    "ideaPlaceholder": "Enter your story idea...",
    "genre": "Genre",
    "episodes": "Episodes",
    "duration": "Episode Duration",
    "characters": "Number of Characters",
    "platform": "Video Platform",
    "style": "Style Description",
    "stylePlaceholder": "Describe visual style (optional)",
    "interactiveMode": "Interactive Mode (review each phase)",
    "autonomousMode": "Autonomous Mode (fully automatic)",
    "start": "Start Creating"
  },
  "phases": {
    "init": "Initializing",
    "story_outline": "Story Outline",
    "character_design": "Character Design",
    "episode_writing": "Episode Writing",
    "storyboard": "Storyboard",
    "video_prompts": "Video Prompts",
    "video_generation": "Video Generation",
    "review": "Review",
    "completed": "Completed",
    "error": "Error"
  }
}
```

### 9.3 使用方式

```typescript
// web/i18n.ts
import { getRequestConfig } from 'next-intl/server';

export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`./messages/${locale}.json`)).default
}));

// 组件中使用
import { useTranslations } from 'next-intl';

export function WorkflowForm() {
  const t = useTranslations('workflow');

  return (
    <form>
      <label>{t('idea')}</label>
      <input placeholder={t('ideaPlaceholder')} />
      <button>{t('start')}</button>
    </form>
  );
}
```

### 9.4 语言切换

```typescript
// web/components/LanguageSwitcher.tsx
'use client';

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLocale = (newLocale: string) => {
    router.push(pathname.replace(`/${locale}`, `/${newLocale}`));
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => switchLocale('zh')}
        className={locale === 'zh' ? 'font-bold' : ''}
      >
        中文
      </button>
      <button
        onClick={() => switchLocale('en')}
        className={locale === 'en' ? 'font-bold' : ''}
      >
        English
      </button>
    </div>
  );
}
```

## 10. 编辑与一致性管理

### 10.1 编辑功能（参考 story_generator.md）

| 编辑类型 | 功能 |
|----------|------|
| 直接编辑 | 手动修改内容，立即保存 |
| AI 辅助编辑 | 输入修改指令，AI 生成建议 |
| 撤销/重做 | 完整的编辑历史支持 |

### 10.2 一致性检查

编辑后自动检测：
- 与前后剧集的剧情矛盾
- 与角色设定或经历的矛盾
- 时间线问题

```typescript
// API: 一致性检查
POST /api/sessions/{id}/consistency-check
{
  "editType": "episode",
  "targetId": 1,
  "newContent": "..."
}

// 响应
{
  "issues": [
    {
      "type": "character_conflict",
      "severity": "warning",
      "description": "角色林浩在第1集已经受伤，但第2集描述他在奔跑",
      "suggestion": "修改为：林浩忍着伤痛缓慢移动",
      "autoFixable": true
    }
  ]
}

// API: 自动修复
POST /api/sessions/{id}/consistency-fix
{
  "issueIds": [1, 2]
}
```

### 10.3 编辑历史 UI

```
┌─────────────────────────────────────────────────────────────┐
│  编辑历史                                    [撤销] [重做]   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🤖 AI编辑 - 2分钟前                                  │   │
│  │ 修改了第2集大纲                                      │   │
│  │ "增加林浩与苏晴的对话场景"                           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ✏️ 手动编辑 - 5分钟前                                │   │
│  │ 修改了角色"林浩"的性格描述                           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🔧 自动修复 - 10分钟前                               │   │
│  │ 修复了第3集的时间线问题                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 11. 实现计划

### Phase 1: 基础框架 ✅ 已完成

**后端 (FastAPI):**
- [x] 创建 FastAPI 项目结构
- [x] 实现基础 REST API 端点
- [x] 实现 Pydantic schemas
- [x] 实现 WorkflowService 和 VideoService
- [x] 实现 WebSocket handler
- [x] 添加 API 测试 (8/8 passed)

**前端 (Next.js):**
- [x] 创建 Next.js 项目结构
- [x] 配置 Tailwind CSS v4 和 Design System
- [x] 配置国际化 (i18n) 系统
- [x] 实现基础页面布局和语言切换

**已实现的文件:**
```
api/                           # FastAPI 后端
├── main.py                    # 应用入口
├── config.py                  # 配置管理
├── routers/sessions.py        # 会话 API
├── routers/videos.py          # 视频 API
├── services/workflow_service.py
├── services/video_service.py
├── schemas/session.py
├── schemas/video.py
└── websocket/handler.py

web/                           # Next.js 前端
├── src/
│   ├── app/
│   │   ├── layout.tsx         # 根布局 + LocaleProvider
│   │   ├── page.tsx           # 首页
│   │   ├── projects/page.tsx  # 项目列表
│   │   └── workflow/
│   │       ├── new/page.tsx   # 新建工作流
│   │       └── [sessionId]/page.tsx
│   ├── components/
│   │   ├── ui/                # UI 组件库
│   │   ├── layout/            # 布局组件
│   │   ├── workflow/          # 工作流组件
│   │   └── video/             # 视频组件
│   ├── i18n/
│   │   ├── index.ts           # i18n 工具
│   │   ├── context.tsx        # LocaleProvider
│   │   └── messages/          # 翻译文件 (zh/en)
│   ├── lib/
│   │   ├── api.ts             # API 客户端
│   │   ├── websocket.ts       # WebSocket 客户端
│   │   └── notifications.ts   # 浏览器通知
│   └── stores/workflow.ts     # Zustand 状态管理
```

**测试结果:**
- API 测试: 8/8 passed
- 前端构建: 成功

**Phase 1 完成日期: 2026-01-31**

### Phase 2: 工作流核心 ✅ 已完成

- [x] 实现 WorkflowService 封装
- [x] 实现 WebSocket 实时通信
- [x] 创建工作流页面组件
- [x] 实现进度展示和审批面板
- [x] 实现浏览器通知
- [x] 连接前后端工作流
- [x] 添加 i18n 支持到所有组件

**已实现的组件:**
```
web/src/components/
├── workflow/
│   ├── WorkflowProgress.tsx    # 工作流进度条 (i18n)
│   ├── ApprovalPanel.tsx       # 审批面板 (i18n)
│   ├── StoryOutlineView.tsx    # 故事大纲视图 (i18n)
│   ├── CharacterList.tsx       # 角色列表/编辑器 (i18n)
│   └── StoryboardGrid.tsx      # 分镜网格/编辑器 (i18n)
├── video/
│   └── VideoGrid.tsx           # 视频网格 (i18n)
└── layout/
    ├── MainLayout.tsx
    └── Sidebar.tsx             # 导航栏 (i18n)

web/src/lib/
├── websocket.ts                # WebSocket 客户端
├── notifications.ts            # 浏览器通知
└── api.ts                      # API 客户端
```

**测试结果:**
- API 测试: 8/8 passed
- 前端构建: 成功

**Phase 2 完成日期: 2026-01-31**

### Phase 3: 内容编辑 ✅ 已完成

- [x] 实现故事大纲编辑器
- [x] 实现角色编辑器（含重大经历）
- [x] 实现分镜编辑器（含密度控制）
- [x] 实现提示词编辑器
- [x] 实现 AI 辅助编辑接口
- [x] 实现内容编辑 API 端点
- [x] 实现编辑历史（撤销/重做）

**已实现的后端:**
```
api/
├── routers/content.py           # 内容编辑 API 端点
├── schemas/content.py           # 内容编辑 Pydantic schemas
└── services/workflow_service.py # 添加内容更新方法
```

**已实现的前端组件:**
```
web/src/components/workflow/
├── StoryOutlineEditor.tsx       # 故事大纲编辑器
├── PromptEditor.tsx             # 视频提示词编辑器
└── EditHistoryPanel.tsx         # 编辑历史面板

web/src/stores/
└── editHistory.ts               # 编辑历史状态管理
```

**API 端点:**
- GET/PUT `/api/sessions/{id}/outline` - 故事大纲 CRUD
- GET/PUT/POST/DELETE `/api/sessions/{id}/characters` - 角色 CRUD
- GET/PUT `/api/sessions/{id}/storyboard` - 分镜 CRUD
- GET/PUT `/api/sessions/{id}/prompts` - 视频提示词 CRUD
- GET/POST `/api/sessions/{id}/videos` - 视频任务管理

**测试结果:**
- API 测试: 8/8 passed
- 前端构建: 成功

**Phase 3 完成日期: 2026-01-31**

### Phase 4: 视频管理 ✅ 已完成

- [x] 实现视频状态展示
- [x] 实现视频预览播放
- [x] 实现视频下载功能
- [x] 实现单个视频重试
- [x] 实现编辑提示词后重试
- [x] 实现切换平台重试
- [x] 实现多平台对比生成

**已实现的组件:**
```
web/src/components/video/
├── VideoGrid.tsx              # 视频网格展示 (i18n)
├── VideoPlayer.tsx            # 视频播放器 + 全屏
└── VideoManager.tsx           # 完整视频管理 (对比/重试/编辑)
```

**已实现的 API 方法:**
- `downloadVideo()` - 下载单个视频
- `compareVideos()` - 多平台对比生成
- `updateVideoPrompt()` - 编辑视频提示词
- `getVideoPrompts()` - 获取所有提示词
- `retryVideo()` - 重试视频生成

**测试结果:**
- API 测试: 8/8 passed
- 前端构建: 成功

**Phase 4 完成日期: 2026-01-31**

### Phase 5: 优化完善 ✅ 已完成

- [x] 添加错误处理和提示
- [x] 优化加载状态
- [x] 完善国际化翻译
- [x] 性能优化
- [x] 测试和修复
- [x] 导出功能（Markdown）

**已实现的组件:**
```
web/src/components/ui/
├── error-boundary.tsx         # 错误边界 + 错误显示组件
└── skeleton.tsx               # 加载骨架屏 (新增 Video/Character)

web/src/components/workflow/
└── ExportButton.tsx           # 导出按钮 (Markdown/JSON)

web/src/lib/
└── export.ts                  # 导出工具 (Markdown/JSON)
```

**功能特性:**
- ErrorBoundary: React 错误边界，捕获组件错误
- ErrorDisplay: 错误提示组件，支持重试
- VideoCardSkeleton/CharacterCardSkeleton: 专用加载骨架
- exportToMarkdown(): 导出为 Markdown 格式
- exportToJSON(): 导出为 JSON 格式
- downloadAsFile(): 通用文件下载

**测试结果:**
- API 测试: 8/8 passed
- 前端构建: 成功

**Phase 5 完成日期: 2026-01-31**

---

## Web UI 开发完成总结

所有 5 个阶段已全部完成：

| 阶段 | 内容 | 状态 | 完成日期 |
|------|------|------|----------|
| Phase 1 | 基础框架 | ✅ 完成 | 2026-01-31 |
| Phase 2 | 工作流核心 | ✅ 完成 | 2026-01-31 |
| Phase 3 | 内容编辑 | ✅ 完成 | 2026-01-31 |
| Phase 4 | 视频管理 | ✅ 完成 | 2026-01-31 |
| Phase 5 | 优化完善 | ✅ 完成 | 2026-01-31 |

**已实现的完整功能:**
- FastAPI 后端 + WebSocket 实时通信
- Next.js 前端 + Tailwind CSS 设计系统
- 完整的 i18n 国际化支持 (中/英文)
- 工作流创建、审批、恢复
- 故事大纲/角色/分镜/提示词编辑
- 视频管理 (预览/下载/重试/多平台对比)
- 编辑历史 (撤销/重做)
- 浏览器通知
- 项目导出 (Markdown/JSON)
- 错误处理和加载状态优化

## 12. 未来 Roadmap

### v1.1 - 移动端支持
- [ ] 响应式布局优化
- [ ] 移动端手势支持
- [ ] 简化的移动端编辑界面
- [ ] PWA 支持

### v1.2 - 高级功能
- [ ] 多用户支持（登录认证）
- [ ] 项目协作功能
- [ ] 云存储集成（视频上传到 OSS/S3）
- [ ] 定时清理过期数据

### v1.3 - AI 增强
- [ ] 更多 LLM 提供商支持
- [ ] 自定义提示词模板
- [ ] AI 智能推荐（风格、镜头）
- [ ] 批量生成优化

## 13. 启动命令

### 开发环境

```bash
# 终端 1: 启动后端
cd movie_generator
source venv/bin/activate
uvicorn api.main:app --reload --port 8000

# 终端 2: 启动前端
cd movie_generator/web
npm install
npm run dev
```

### 生产环境

```bash
# 构建前端
cd web && npm run build

# 启动后端 (使用 gunicorn)
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Docker 部署

```dockerfile
# Dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY api/ api/

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}

  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - api
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
```

## 9. 依赖更新

```txt
# requirements.txt 新增

# FastAPI
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
websockets>=12.0
python-multipart>=0.0.6

# 现有依赖保持不变
```

```json
// web/package.json
{
  "name": "movie-generator-web",
  "version": "1.0.0",
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next-intl": "^3.4.0",
    "zustand": "^4.5.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.323.0",
    "tailwind-merge": "^2.2.1",
    "tailwindcss-animate": "^1.0.7"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.0",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.0"
  }
}
```

---

*文档版本: 1.3*
*创建日期: 2025-01-31*
*更新日期: 2026-01-31*
*Phase 1 完成日期: 2026-01-31*
*Phase 2 完成日期: 2026-01-31*
