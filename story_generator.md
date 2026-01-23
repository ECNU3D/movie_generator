# AI 故事剧本生成器

基于 Google Gemini 大模型驱动的故事和分镜脚本生成工具。

## 功能概述

- **故事创意生成**: 用户输入创意或一键随机生成
- **故事大纲生成**: AI 自动生成完整故事大纲、角色设定、分集剧情
- **人物知识库**: 管理角色设定，追踪重大经历，保证剧本一致性
- **分镜脚本生成**: 将剧集大纲展开为详细的分镜脚本
- **视频提示词生成**: 为四大平台生成定制提示词（可灵、通义、即梦、海螺）

## 技术栈

- **AI 模型**: Google Gemini 3 Flash (`gemini-3-flash-preview`)
- **SDK**: `google-genai` (新版 Google Gen AI SDK)
- **UI**: Streamlit
- **数据库**: SQLite
- **语言**: Python 3.13+

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API Key

将 Gemini API Key 保存到项目根目录的 `gemini_api_key` 文件中。

### 启动应用

```bash
./run_story_generator.sh
```

或手动启动:

```bash
streamlit run src/story_generator/app.py --server.port 8502
```

访问 http://localhost:8502

## 项目结构

```
src/story_generator/
├── __init__.py          # 模块导出
├── models.py            # 数据模型 (Project, Character, Episode, Shot)
├── database.py          # SQLite 数据库操作
├── gemini_client.py     # Gemini API 客户端
└── app.py               # Streamlit UI
```

## 数据模型

### Project (项目)
- 名称、描述、类型、风格、目标受众
- 集数、每集时长
- 关联角色和剧集

### Character (角色)
- 基本信息: 姓名、年龄、外貌、性格
- 背景故事、人物关系
- 视觉描述 (用于生成一致的图像/视频)
- **重大经历**: 追踪每集发生的重大事件，用于保持剧本一致性

### Episode (剧集)
- 集数、标题、大纲
- 目标时长、状态
- 关联分镜列表

### Shot (分镜)
- 场景编号、镜头编号
- 镜头类型: 大远景、远景、全景、中景、近景、特写等
- 镜头运动: 固定、左摇、右摇、推进、拉远、跟踪等
- 画面描述、对白、音效/配乐
- 生成的提示词 (按平台存储)

## 视频提示词生成

支持为以下平台生成定制提示词:

| 平台 | 特点 |
|------|------|
| **可灵 (Kling)** | 支持中英文，格式: [主体] + [动作] + [场景] + [风格] + [镜头] |
| **通义万相 (Tongyi)** | 支持中文，多镜头叙事 |
| **即梦 (Jimeng)** | 中英文混合，Pro版多镜头叙事 |
| **海螺 (Hailuo)** | 支持运镜指令: [左摇], [右摇], [推进], [拉远], [上升], [下降] 等 |

### 提示词类型

- **文生视频 (T2V)**: 直接生成视频的文字提示词
- **首帧图片 (I2V First)**: 图生视频的起始帧描述
- **尾帧图片 (I2V Last)**: 图生视频的结束帧描述

## API 配置

```python
from src.story_generator import GeminiClient, GeminiConfig

config = GeminiConfig(
    api_key="your-api-key",
    model_name="gemini-3-flash-preview",  # 默认模型
    temperature=0.8,
    max_output_tokens=8192
)
client = GeminiClient(config)
```

## 工作流程

1. **创建项目** - 设置故事类型、风格、集数等
2. **生成故事大纲** - 输入创意或随机生成，AI 生成完整大纲
3. **编辑角色设定** - 完善角色信息，建立人物知识库
4. **生成分镜脚本** - 为每集生成详细分镜
5. **编辑分镜** - 调整镜头细节
6. **生成视频提示词** - 选择平台，生成定制提示词
7. **导出使用** - 复制提示词到对应视频生成平台

## 人物知识库

角色的 `major_events` (重大经历) 功能用于追踪角色在每集中的重要事件:

```python
character.add_major_event(
    episode_number=1,
    description="遭遇车祸",
    impact="行动不便，需要康复"
)

# 获取角色知识库上下文 (用于 AI 生成时保持一致性)
context = character.get_knowledge_context(up_to_episode=3)
```

这确保了 AI 在生成后续剧本时能够考虑到角色之前发生的事件。

## 依赖包

```
google-genai>=1.0.0
streamlit>=1.28.0
```

## 更新日志

- **2026-01**: 迁移至新版 `google-genai` SDK，模型更新为 `gemini-3-flash-preview`
