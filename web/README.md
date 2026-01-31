# AI Movie Generator Web App

基于 Next.js + FastAPI 的 AI 视频生成 Web 应用。

## 功能

- **工作流管理**: 创建项目、阶段审批、实时状态、会话恢复
- **内容编辑**: 故事大纲、角色、分镜、提示词编辑
- **视频生成**: 单独生成、状态刷新、预览、下载
- **多语言**: 中文/English

## 技术栈

- **前端**: Next.js 16, shadcn/ui, Tailwind, Zustand, TypeScript
- **后端**: FastAPI, SQLite, Python 3.13+

## 快速开始

### 后端

```bash
cd movie_generator
source venv/bin/activate
export GEMINI_API_KEY="your-key"
uvicorn api.main:app --port 8000 --reload
```

### 前端

```bash
cd web
npm install
npm run dev
```

访问 http://localhost:3000

## API 端点

| 端点 | 说明 |
|------|------|
| `POST /api/sessions` | 创建会话 |
| `GET /api/sessions/{id}` | 获取会话 |
| `POST /api/sessions/{id}/approve` | 审批 |
| `POST /api/videos/{id}/{shot}/retry` | 生成视频 |
| `GET /api/videos/{id}/{shot}/download` | 下载视频 |

## 相关文档

- [Web UI 设计](../docs/WEB_UI_DESIGN.md)
- [E2E 测试报告](../docs/E2E_TEST_REPORT.md)
