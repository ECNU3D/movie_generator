# AI电影生成器 - 待收集信息与待办事项

> 本文档记录项目开发所需的待收集信息、待确认事项和开发计划。

---

## 1. 待收集信息清单

### 1.1 API文档与密钥（必需）

#### 视频生成平台
- [ ] **可灵 (Kling AI)**
  - API文档链接：
  https://app.klingai.com/cn/dev/document-api/apiReference/commonInfo
  https://app.klingai.com/cn/dev/document-api/apiReference/rateLimits
  https://app.klingai.com/cn/dev/document-api/apiReference/model/skillsMap
  https://app.klingai.com/cn/dev/document-api/apiReference/model/OmniVideo
  https://app.klingai.com/cn/dev/document-api/apiReference/model/textToVideo
  https://app.klingai.com/cn/dev/document-api/apiReference/model/imageToVideo
  https://app.klingai.com/cn/dev/document-api/apiReference/model/multiImageToVideo
  https://app.klingai.com/cn/dev/document-api/apiReference/model/motionControl
  https://app.klingai.com/cn/dev/document-api/apiReference/model/multimodalToVideo
  https://app.klingai.com/cn/dev/document-api/apiReference/model/videoDuration
  - API Key
  - 支持的功能列表（图生视频、文生视频、主体参考等）
  - 定价信息

- [ ] **通义万相**
  - API文档链接：https://bailian.console.aliyun.com/cn-beijing/?tab=api#/api
  - API Key (阿里云账号)
  - 支持的功能列表
  - 定价信息

- [ ] **即梦AI**
  - API文档链接：https://www.volcengine.com/docs/85621/1544716?lang=zh
  - API Key
  - 支持的功能列表
  - 定价信息

- [ ] **海螺视频 (Hailuo AI)**
  - API文档链接：https://platform.minimaxi.com/docs/api-reference/video-generation-t2v
  - API Key
  - 支持的功能列表
  - 定价信息

#### LLM平台
- [ ] **阿里千问 (Qwen)**
  - API文档链接
  - API Key

- [ ] **字节豆包 (Doubao)**
  - API文档链接
  - API Key

- [ ] **智谱AI (Zhipu)**
  - API文档链接
  - API Key

- [ ] **OpenAI**
  - API Key

- [ ] **Google Gemini**
  - API Key

### 1.2 需要确认的技术细节

| 问题 | 影响范围 | 优先级 |
|------|----------|--------|
| 各平台视频生成的最大时长限制？ | 分镜拆分策略 | 高 |
| 各平台是否支持主体参考？支持几个主体？ | 角色一致性方案 | 高 |
| 各平台API的并发限制和QPS？ | 任务调度设计 | 中 |
| 各平台生成视频的分辨率选项？ | 前端配置项 | 中 |
| 各平台API的回调机制（轮询/Webhook）？ | 任务状态管理 | 中 |

### 1.3 业务需求确认

| 问题 | 说明 |
|------|------|
| 目标用户是谁？ | 个人创作者/小团队/企业？影响功能复杂度 |
| 是否需要多语言支持？ | 影响前端国际化设计 |
| 是否需要用户认证系统？ | 单用户/多用户模式 |
| 视频成片的导出格式要求？ | MP4/MOV/其他 |
| 是否需要配音/字幕功能？ | 后期可以扩展TTS |
| 预算范围？ | 影响云服务选择 |

---

## 2. 开发计划建议

### Phase 1: 基础架构（MVP）
1. 项目脚手架搭建（Next.js + FastAPI）
2. 数据库设计与实现
3. 基础API框架
4. 简单的项目管理功能

### Phase 2: AI接入
1. 统一AI接口抽象层设计
2. 接入1-2个LLM平台
3. 接入1-2个视频生成平台
4. 基础的剧本生成功能

### Phase 3: 核心功能
1. 剧本编辑器
2. 角色管理
3. 分镜生成与管理
4. 视频生成流程

### Phase 4: 完善与优化
1. 更多平台接入
2. 角色一致性优化
3. 素材管理
4. 视频合成与导出

---

## 3. 问题与建议

### 3.1 架构建议

1. **统一接口层**：建议设计一个Provider抽象层，所有AI服务提供商实现同一接口，便于扩展和切换。

2. **异步任务处理**：视频生成通常需要几十秒到几分钟，建议使用Celery+Redis处理异步任务，提供实时进度反馈。

3. **成本控制**：建议增加用量统计和预算控制功能，避免API调用费用失控。

### 3.2 待讨论问题

1. **视频拼接方案**：各平台生成的视频片段如何拼接成完整影片？
   - 方案A：使用FFmpeg在后端处理
   - 方案B：前端使用WebCodecs API
   - 方案C：接入专业视频编辑API

2. **音频处理**：
   - 是否需要AI配音功能？
   - 是否需要背景音乐生成？
   - 是否需要音效库？

3. **存储方案**：
   - 生成的视频和图片如何存储？
   - 是否需要CDN加速？
   - 存储容量预估？

4. **部署环境**：
   - 本地部署还是云部署？
   - 是否需要Docker化？
   - 预期的并发用户数？

---

## 附录

### A. 相关资源链接

| 平台 | 官网 | API文档 |
|------|------|---------|
| 可灵 | https://app.klingai.com/cn/ | 待补充 |
| 通义万相 | https://tongyi.aliyun.com/wanxiang | 待补充 |
| 即梦AI | https://jimeng.jianying.com/ai-tool/home/ | 待补充 |
| 海螺视频 | https://hailuoai.com | 待补充 |
| Elser AI | https://www.elser.ai/zh/home | 参考产品 |

### B. 技术文档参考
- Next.js: https://nextjs.org/docs
- FastAPI: https://fastapi.tiangolo.com/
- SQLite: https://www.sqlite.org/docs.html
- Celery: https://docs.celeryq.dev/

---

*文档版本: 1.0*
*最后更新: 2026-01-18*
