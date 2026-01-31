# AI Movie Generator

开源 AI 视频生成系统，支持从剧本创作到视频生成的完整工作流。

## 项目模块

| 模块 | 说明 | 文档 |
|------|------|------|
| **Video Comparison** | 多平台视频生成效果对比 (Streamlit) | [README](src/comparison/README.md) |
| **Story Generator** | AI 剧本生成平台 (Streamlit) | [README](src/story_generator/README.md) |
| **Workflow CLI** | 多 Agent 工作流命令行工具 | [README](scripts/README.md) |
| **Web App** | 完整 Web 应用 (Next.js + FastAPI) | [README](web/README.md) |

## 支持的视频平台

| 平台 | 文生视频 | 图生视频 | 首尾帧 | 主体参考 |
|------|:--------:|:--------:|:------:|:--------:|
| 可灵 (Kling) | ✅ | ✅ | ✅ | ✅ |
| 海螺 (Hailuo) | ✅ | ✅ | ✅ | ✅ |
| 即梦 (Jimeng) | ✅ | ✅ | ❌ | ⚠️ |
| 通义万相 (Tongyi) | ✅ | ✅ | ❌ | ⚠️ |

## 快速开始

### 环境配置

```bash
# 克隆项目
git clone https://github.com/your-repo/movie_generator.git
cd movie_generator

# 创建虚拟环境
python3.13 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置 API Keys
export GEMINI_API_KEY="your-gemini-key"
```

### 视频平台配置

创建 `src/providers/config.local.yaml`:

```yaml
providers:
  kling:
    access_key: "your-access-key"
    secret_key: "your-secret-key"
  hailuo:
    api_key: "your-api-key"
```

### 运行各模块

```bash
# 1. 视频平台对比 (Streamlit)
./scripts/run_comparison.sh
# 或: streamlit run src/comparison/app.py --server.port 8501

# 2. 剧本生成器 (Streamlit)
./scripts/run_story_generator.sh
# 或: streamlit run src/story_generator/app.py --server.port 8502

# 3. CLI 工作流
python scripts/run_workflow.py start "一只小猫在阳光下打盹"
python scripts/run_workflow.py list
python scripts/run_workflow.py resume <session_id>

# 4. Web 应用
uvicorn api.main:app --port 8000 &  # 后端
cd web && npm run dev                # 前端
```

## 项目结构

```
movie_generator/
├── src/
│   ├── comparison/      # 视频平台对比模块
│   ├── story_generator/ # 剧本生成模块
│   ├── agents/          # 多 Agent 系统
│   ├── providers/       # 视频平台 Provider
│   ├── skills/          # Agent 技能系统
│   └── mcp_servers/     # MCP 服务器
├── api/                 # FastAPI 后端
├── web/                 # Next.js 前端
├── scripts/             # CLI 脚本和启动脚本
│   ├── run_workflow.py      # 工作流 CLI
│   ├── run_comparison.sh    # 启动对比工具
│   ├── run_story_generator.sh # 启动剧本生成器
│   └── test_*.py            # 测试脚本
├── docs/                # 设计文档
└── api_doc/             # 平台 API 文档
```

## 测试

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
```

## 文档

- [需求文档](docs/REQUIREMENTS.md)
- [多 Agent 设计](docs/MULTI_AGENT_PLAN.md)
- [Web UI 设计](docs/WEB_UI_DESIGN.md)
- [Story Generator 详细文档](docs/STORY_GENERATOR.md)
- [E2E 测试报告](docs/E2E_TEST_REPORT.md)
- [平台 API 文档](docs/providers/)

## License

MIT
