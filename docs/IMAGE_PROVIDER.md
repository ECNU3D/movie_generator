# Image Provider 图像生成模块

AI 图像生成 Provider，支持角色设计、帧生成、图像编辑等功能。

## 功能概览

### 已实现功能

#### 核心方法
| 方法 | 描述 | 状态 |
|------|------|------|
| `text_to_image()` | 文生图 - 根据文本描述生成图像 | ✅ |
| `edit_image()` | 图像编辑 - 使用文本指令编辑图像 | ✅ |

#### 角色生成
| 方法 | 描述 | 状态 |
|------|------|------|
| `generate_character_front_view()` | 生成角色正面图（参考图） | ✅ |
| `generate_character_side_view()` | 生成角色侧面图 | ✅ |
| `generate_character_back_view()` | 生成角色背面图 | ✅ |
| `generate_character_three_views()` | 生成三张独立的视图（侧面/正面/背面） | ✅ |
| `generate_character_sheet()` | 生成单张三视图 | ✅ |
| `generate_character_turnaround()` | 生成游戏风格的角色设定图（5角度） | ✅ |

#### 帧生成
| 方法 | 描述 | 状态 |
|------|------|------|
| `generate_frame()` | 纯文本生成视频帧 | ✅ |
| `generate_frame_with_character()` | 带角色参考的帧生成（保持一致性） | ✅ |

#### 图像下载
| 方法 | 描述 | 状态 |
|------|------|------|
| `download_image()` | 下载单张图片到本地 | ✅ |
| `download_task_images()` | 下载任务中的所有图片 | ✅ |

#### 工具方法
| 方法 | 描述 | 状态 |
|------|------|------|
| `get_available_models()` | 获取可用模型列表 | ✅ |
| `get_supported_sizes()` | 获取模型支持的尺寸 | ✅ |
| `test_connection()` | 测试 API 连接 | ✅ |

### 计划功能

| 功能 | 描述 | 优先级 |
|------|------|--------|
| `generate_character_expression()` | 生成角色的不同表情变化（喜怒哀乐） | 高 |
| `generate_character_pose()` | 生成角色的不同姿势（站立/坐着/跑步等） | 高 |
| `change_character_outfit()` | 更换角色的服装 | 中 |
| `change_art_style()` | 将现有图片转换为不同艺术风格 | 中 |
| `generate_scene_variations()` | 生成同一场景的多个变体 | 中 |
| `generate_character_action()` | 生成角色执行特定动作的图像 | 中 |
| `composite_character_scene()` | 将角色合成到指定场景中 | 低 |

## 支持的平台

| 平台 | 文生图 | 图像编辑 | 状态 |
|------|:------:|:--------:|------|
| 通义 (Tongyi/DashScope) | ✅ | ✅ | 已实现 |
| Midjourney | - | - | 计划中 |
| Stable Diffusion | - | - | 计划中 |

### 通义模型

| 模型 | 类型 | 说明 |
|------|------|------|
| `qwen-image-plus` | 文生图 | 通义千问 Plus，支持复杂文字渲染 |
| `qwen-image-max` | 文生图 | 通义千问 Max，最高质量 |
| `wan2.6-t2i` | 文生图 | 通义万相2.6，写实摄影风格 |
| `qwen-image-edit-max` | 图像编辑 | 多图输入输出 |
| `qwen-image-edit-plus` | 图像编辑 | 通用编辑 |
| `wan2.5-i2i-preview` | 图像编辑 | 多图融合 |

## 快速开始

### 安装依赖

```bash
pip install dashscope
```

### 配置 API Key

在 `src/providers/config.local.yaml` 中配置：

```yaml
providers:
  tongyi:
    enabled: true
    api_key: "sk-xxx"  # DashScope API Key
```

或设置环境变量：

```bash
export DASHSCOPE_API_KEY="sk-xxx"
```

### 代码示例

```python
from src.providers.image import TongyiImageProvider, CharacterViewMode

# 初始化
provider = TongyiImageProvider()
provider.initialize()

# 1. 文生图
task = provider.text_to_image(
    prompt="一只可爱的橘猫躺在阳光下",
    size="1328*1328",
)
print(task.image_url)

# 2. 生成角色正面图
task = provider.generate_character_front_view(
    character_description="25岁亚洲女性，长黑发，穿白色连衣裙",
    style="realistic",
    size="1328*1328",
)

# 下载图片
paths = provider.download_task_images(task, save_dir="./output", prefix="character")
print(f"Downloaded: {paths}")

# 3. 生成三张独立视图
task = provider.generate_character_three_views(
    character_reference=task.image_url,
    character_description="同上",
    style="realistic",
)
# task.image_urls = [side_view, front_view, back_view]

# 4. 生成单张三视图
task = provider.generate_character_sheet(
    character_reference=task.image_url,
    character_description="同上",
    style="realistic",
    size="1664*928",  # 宽幅
)

# 5. 生成角色设定图（游戏风格）
task = provider.generate_character_turnaround(
    character_reference=task.image_url,
    character_description="同上",
    style="realistic",
    size="1664*928",
)

# 6. 生成视频帧
task = provider.generate_frame(
    prompt="樱花树下的少女，微风吹过",
    size="1664*928",  # 16:9
    style="cinematic",
)

# 7. 带角色参考的帧生成
task = provider.generate_frame_with_character(
    prompt="角色站在海边，夕阳西下",
    character_reference=character_url,
    size="1664*928",
    style="cinematic",
)
```

## 图像尺寸

### 通义千问 (Qwen-Image)
| 尺寸 | 比例 | 用途 |
|------|------|------|
| 1664×928 | 16:9 | 视频帧、横屏场景 |
| 928×1664 | 9:16 | 竖屏场景 |
| 1328×1328 | 1:1 | 角色设计、头像 |
| 1472×1104 | 4:3 | 传统照片比例 |
| 1104×1472 | 3:4 | 竖版照片 |

### 通义万相 (Wanx)
| 尺寸 | 比例 |
|------|------|
| 1024×1024 | 1:1 |
| 1440×810 | 16:9 |
| 810×1440 | 9:16 |

## 艺术风格

支持的预设风格：

| 风格 | 说明 |
|------|------|
| `realistic` | 写实摄影风格 |
| `anime` | 日本动漫风格 |
| `cartoon` | 卡通风格 |
| `3d` | 3D 渲染 (Pixar 风格) |
| `watercolor` | 水彩画风格 |
| `oil_painting` | 油画风格 |
| `sketch` | 素描风格 |
| `pixel_art` | 像素艺术风格 |
| `cinematic` | 电影画面风格 |

## 测试

```bash
# 运行图像生成测试
python scripts/test_image_provider.py

# 运行角色视图测试
python scripts/test_character_views.py

# 启动测试 App (Streamlit)
./scripts/run_image_generator.sh
# 或
streamlit run src/image_generator/app.py --server.port 8503
```

## 架构

```
src/providers/image/
├── __init__.py          # 模块导出
├── base.py              # ImageProvider 基类
│   ├── ImageTask        # 任务数据类
│   ├── ImageTaskStatus  # 任务状态枚举
│   ├── CharacterViewMode # 角色视图模式枚举
│   ├── ArtStyle         # 艺术风格枚举
│   └── ImageSize        # 图像尺寸枚举
└── tongyi.py            # 通义实现
    ├── TongyiImageProvider
    └── TONGYI_IMAGE_MODELS
```

## 注意事项

- 生成的图像 URL 有效期为 24 小时，请及时下载
- 内容需符合安全审核要求
- API 调用有限流限制，请合理使用
- 角色三视图生成会调用 3 次 API（每个视角一次）

## 相关文档

- [Tongyi API 文档](https://help.aliyun.com/zh/model-studio/)
- [Image Generator App README](../src/image_generator/README.md)
