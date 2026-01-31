# Agentic Workflow CLI

基于 LangGraph 的多 Agent 工作流命令行工具，支持从故事创意到视频生成的完整自动化流程。

## 功能特点

### 多 Agent 协作
- **StoryWriter Agent**: 生成故事大纲、角色设计、剧集内容
- **Director Agent**: 创建分镜脚本、镜头描述
- **VideoProducer Agent**: 生成视频提示词、提交视频生成任务
- **Supervisor Agent**: 协调工作流路由和状态管理

### 工作流程
```
INIT → STORY_OUTLINE → CHARACTER_DESIGN → EPISODE_WRITING
    → STORYBOARD → VIDEO_PROMPTS → VIDEO_GENERATION → REVIEW → COMPLETED
```

### 交互模式
- **Interactive 模式**: 每个阶段暂停，等待用户审批
- **Autonomous 模式**: 全自动运行，无需人工干预

### 会话管理
- 会话持久化存储
- 支持暂停/恢复
- 失败自动恢复
- 完整的检查点机制

## 快速开始

### 环境配置

```bash
# 从项目根目录
cd movie_generator

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置 API Keys
export GEMINI_API_KEY="your-gemini-api-key"
```

### 配置视频平台

创建 `src/providers/config.local.yaml`:

```yaml
providers:
  kling:
    access_key: "your-access-key"
    secret_key: "your-secret-key"
```

## 命令使用

### 启动新工作流

```bash
# 基本用法
python scripts/run_workflow.py start "一只小猫在阳光下打盹"

# 完整参数
python scripts/run_workflow.py start "故事创意" \
    --genre 科幻 \
    --episodes 1 \
    --duration 60 \
    --characters 3 \
    --platform kling \
    --mode interactive
```

**参数说明:**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--genre` | 故事类型 | drama |
| `--episodes` | 剧集数量 | 1 |
| `--duration` | 每集时长(秒) | 60 |
| `--characters` | 角色数量 | 3 |
| `--platform` | 视频平台 | kling |
| `--mode` | 运行模式 | interactive |

### 列出所有会话

```bash
python scripts/run_workflow.py list

# 按状态筛选
python scripts/run_workflow.py list --status running
python scripts/run_workflow.py list --status paused
python scripts/run_workflow.py list --status completed
```

### 恢复会话

```bash
python scripts/run_workflow.py resume <session_id>
```

### 查看会话详情

```bash
python scripts/run_workflow.py view <session_id>
```

### 查看视频生成状态

```bash
# 查看状态
python scripts/run_workflow.py videos <session_id>

# 等待完成并下载
python scripts/run_workflow.py videos <session_id> --wait --download
```

## 测试脚本

```bash
# Story Generator 测试
python scripts/test_story_generator.py

# Agent 单元测试
python scripts/test_agents.py

# 会话管理测试
python scripts/test_session.py

# 端到端测试
python scripts/test_e2e.py

# MCP 服务器测试
python scripts/test_mcp_servers.py

# API 测试
python scripts/test_api.py

# 技能系统测试
python scripts/test_skills_with_agent.py
python scripts/validate_skills.py
```

## MCP 服务器

工作流使用 MCP (Model Context Protocol) 服务器提供工具接口:

```bash
# 项目管理服务器
python scripts/run_mcp_servers.py project

# 分镜管理服务器
python scripts/run_mcp_servers.py storyboard

# 视频生成服务器
python scripts/run_mcp_servers.py video
```

## 启动脚本

```bash
# 启动视频对比工具 (Streamlit)
./scripts/run_comparison.sh

# 启动剧本生成器 (Streamlit)
./scripts/run_story_generator.sh
```

## 项目结构

```
scripts/
├── run_workflow.py          # 工作流 CLI 入口
├── run_mcp_servers.py       # MCP 服务器启动
├── run_comparison.sh        # 视频对比工具启动脚本
├── run_story_generator.sh   # 剧本生成器启动脚本
├── test_agents.py           # Agent 测试
├── test_session.py          # 会话测试
├── test_e2e.py              # E2E 测试
├── test_mcp_servers.py      # MCP 测试
├── test_api.py              # API 测试
├── test_story_generator.py  # 剧本生成器测试
├── test_skills_with_agent.py # 技能系统测试
├── validate_skills.py       # 技能验证
└── README.md                # 本文档

src/agents/
├── base.py              # Agent 基类
├── story_writer.py      # 故事写作 Agent
├── director.py          # 导演 Agent
├── video_producer.py    # 视频制作 Agent
├── supervisor.py        # 监督 Agent
├── graph.py             # LangGraph 工作流
├── session.py           # 会话管理
└── state.py             # 状态定义
```

## 工作流状态

| 阶段 | 说明 | Agent |
|------|------|-------|
| INIT | 初始化 | - |
| STORY_OUTLINE | 故事大纲 | StoryWriter |
| CHARACTER_DESIGN | 角色设计 | StoryWriter |
| EPISODE_WRITING | 剧集撰写 | StoryWriter |
| STORYBOARD | 分镜脚本 | Director |
| VIDEO_PROMPTS | 视频提示词 | VideoProducer |
| VIDEO_GENERATION | 视频生成 | VideoProducer |
| REVIEW | 审核 | - |
| COMPLETED | 完成 | - |

## 相关文档

- [多 Agent 设计文档](../docs/MULTI_AGENT_PLAN.md)
- [技能系统](../src/skills/)
