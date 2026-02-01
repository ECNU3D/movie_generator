# Story Generator App

AI 驱动的剧本生成平台，基于 Streamlit + Google Gemini，支持从创意到分镜的完整剧本创作流程。

## 功能特点

### 故事创作
- **创意生成**: 随机生成或自定义故事创意
- **大纲生成**: 自动生成完整故事大纲（标题、简介、主题、设定）
- **角色设计**: 支持 1-10 个角色，自动生成外观、性格、背景
- **剧集管理**: 多剧集支持，每集可独立编辑

### 分镜脚本
- **智能分镜**: 根据剧情自动生成分镜脚本
- **密度控制**: 支持低/中/高三档分镜密度
- **视觉描述**: 每个镜头包含详细的视觉描述、对话、时长

### 视频提示词
- **多平台支持**: 为可灵、海螺、即梦、通义万相生成优化提示词
- **图生视频**: 支持首帧/首尾帧提示词生成
- **一键导出**: 导出完整剧本和提示词

### 编辑功能
- **直接编辑**: 手动修改任何内容
- **AI 辅助编辑**: 使用 AI 重写、扩展、修改
- **一致性检查**: 自动检测角色/情节不一致并修复
- **撤销/重做**: 完整的编辑历史支持

## 快速开始

### 环境配置

```bash
# 从项目根目录
cd movie_generator

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### API 配置

设置 Gemini API Key:

```bash
# 方式一：环境变量
export GEMINI_API_KEY="your-api-key"

# 方式二：配置文件
echo "your-api-key" > gemini_api_key
```

### 启动应用

```bash
# 方式一：使用脚本
./run_story_generator.sh

# 方式二：直接运行
streamlit run src/story_generator/app.py --server.port 8502
```

访问 http://localhost:8502

## 使用流程

### 1. 创建项目
- 输入故事创意或点击"随机创意"
- 设置角色数量（1-10）
- 点击"生成大纲"

### 2. 编辑角色
- 查看自动生成的角色设定
- 可编辑姓名、年龄、外观、性格、背景
- 使用 AI 辅助优化角色描述

### 3. 编写剧集
- 查看各剧集大纲
- 可直接编辑或使用 AI 扩写
- 运行一致性检查

### 4. 生成分镜
- 选择分镜密度（低/中/高）
- 点击"生成分镜"
- 编辑视觉描述、对话、镜头运动

### 5. 生成提示词
- 选择目标视频平台
- 生成优化后的视频提示词
- 导出完整剧本

## 项目结构

```
src/story_generator/
├── app.py           # Streamlit 主应用
├── models.py        # 数据模型 (Project, Character, Episode, Shot)
├── database.py      # SQLite 数据库操作
├── gemini_client.py # Google Gemini API 客户端
└── README.md        # 本文档
```

## 数据存储

- 数据库: `data/story_generator.db` (SQLite)
- 自动创建表结构
- 支持多项目管理
- 自动保存编辑历史

## 技术栈

- **UI**: Streamlit
- **AI 模型**: Google Gemini 2.0 Flash
- **数据库**: SQLite
- **语言**: Python 3.13+

## 相关文档

- [故事生成器详细文档](../../story_generator.md)
- [视频平台提示词指南](../../docs/providers/)
