# AI 电影生成器

一个开源的 AI 驱动电影/短视频生成工具，支持从剧本创作到视频生成的完整工作流程。

## 项目愿景

构建一个类似 [Elser AI](https://www.elser.ai/zh/home) 的完整视频生成工作流，但：
- **开源免费**：核心功能完全开源
- **多平台支持**：接入可灵、通义万相、即梦AI、海螺视频等多个视频生成平台
- **灵活配置**：每个功能可选择不同的 AI 服务提供商
- **成本可控**：支持主体参考（高成本高质量）和提示词控制（低成本）两种一致性方案

## 当前进度

### ✅ Phase 1: 故事生成器 (已完成)

基于 Streamlit + Google Gemini 的故事剧本生成工具，功能包括：

- 故事创意生成（随机/自定义）
- 完整故事大纲生成（标题、简介、角色、剧集）
- 人物数量自定义（1-10个）
- 人物知识库（角色设定、重大经历追踪）
- 分镜脚本生成（支持密度选择）
- 剧集大纲编辑（直接编辑/AI辅助）
- 一致性检查与自动修复
- 编辑历史（撤销/重做）
- 四大平台视频提示词生成
- 图生视频提示词（首帧/首尾帧）
- 一键导出大纲

详细文档：[story_generator.md](./story_generator.md)

### 📋 后续计划

- **Phase 2**: 接入视频生成平台 API
- **Phase 3**: 分镜图片生成、视频生成与管理
- **Phase 4**: FastAPI + Next.js 架构升级

## 快速开始

### 运行故事生成器

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 Gemini API Key
echo "your-api-key" > gemini_api_key

# 启动应用
./run_story_generator.sh
# 或
streamlit run src/story_generator/app.py --server.port 8502
```

访问 http://localhost:8502

## 支持的视频平台

| 平台 | 文生视频 | 图生视频 | 首尾帧 | 主体参考 | 状态 |
|------|----------|----------|--------|----------|------|
| 可灵 (Kling) | ✅ | ✅ | ✅ | ✅ | 📄 文档就绪 |
| 通义万相 | ✅ | ✅ | ❌ | ⚠️ | 📄 文档就绪 |
| 即梦AI | ✅ | ✅ | ❌ | ⚠️ | 📄 文档就绪 |
| 海螺视频 | ✅ | ✅ | ✅ | ✅ | 📄 文档就绪 |

平台 API 文档：[docs/providers/](./docs/providers/)

## 项目结构

```
movie_generator/
├── src/
│   └── story_generator/     # 故事生成器模块
│       ├── app.py           # Streamlit UI
│       ├── models.py        # 数据模型
│       ├── database.py      # 数据库操作
│       └── gemini_client.py # Gemini API 客户端
├── docs/
│   ├── providers/           # 视频平台 API 文档
│   ├── TODO.md              # 待办事项
│   └── REQUIREMENTS.md      # 需求文档
├── data/                    # 数据库文件
├── story_generator.md       # 故事生成器文档
└── README.md                # 本文件
```

## 技术栈

**当前 (Phase 1)**:
- AI 模型: Google Gemini 3 Flash
- UI: Streamlit
- 数据库: SQLite
- 语言: Python 3.13+

**目标 (Phase 4)**:
- 前端: Next.js
- 后端: FastAPI
- 数据库: PostgreSQL
- 任务队列: Celery + Redis

## 相关文档

- [故事生成器详细文档](./story_generator.md)
- [需求与设计文档](./docs/REQUIREMENTS.md)
- [待办事项](./docs/TODO.md)
- [视频平台 API 文档](./docs/providers/README.md)

## 原始想法

> 我想做一个AI电影生成器，首先生成一部电影最主要的是视频分镜的生成，而视频分镜的生成又依赖于图片分镜的生成。同时由于现在主流平台主要支持几种视频生成模式：
> 1. 图生视频：用户提供首帧，或首尾帧，加上文字提示词
> 2. 文生视频：用户仅提供提示词来控制视频内容的生成
> 3. 主体参考：上传主体角色的图片，保持人物的一致性
>
> 我希望做一个开源的，可以接入可灵、通义万相、即梦AI和海螺视频。剧本的生成可以接入阿里的千问平台、豆包、智普平台、ChatGPT和Gemini。
>
> 我希望做的一个特色功能就是可以每一个功能让用户使用不同模型供应商的模型和API。同时用不同的方法来实现视频的前后一致性。
>
> 另外就是我们需要非常好的AI剧本生成编辑器，让用户可以生成、编辑管理很长的剧本（最终成片长达一到三小时）。

## License

MIT
