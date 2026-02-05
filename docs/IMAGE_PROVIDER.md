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

#### 场景合成
| 方法 | 描述 | 状态 |
|------|------|------|
| `composite_character_scene()` | 将角色合成到指定场景中，保持外貌一致性 | ✅ |

**约束（因 Provider 而异）：**
- **通义 (Tongyi)**: 最多 3 张输入图片，支持 1-3 个角色，推荐 `qwen-image-edit-max` 模型
- **即梦 (JiMeng)**: 最多 14 张输入图片，支持 1-14 个角色
- 角色参考图应使用**正面单人图**（不是三面图）
- 角色数较少时可额外传入背景参考图

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

## 支持的平台

| 平台 | 文生图 | 图像编辑 | 最大输入图 | 状态 |
|------|:------:|:--------:|:----------:|------|
| 通义 (Tongyi/DashScope) | ✅ | ✅ | 3 | 已实现 |
| 即梦 Seedream (JiMeng/Ark) | ✅ | ✅ | 14 | 已实现 |
| Midjourney | - | - | - | 计划中 |
| Stable Diffusion | - | - | - | 计划中 |

### 通义模型

| 模型 | 类型 | 说明 |
|------|------|------|
| `qwen-image-plus` | 文生图 | 通义千问 Plus，支持复杂文字渲染 |
| `qwen-image-max` | 文生图 | 通义千问 Max，最高质量 |
| `wan2.6-t2i` | 文生图 | 通义万相2.6，写实摄影风格 |
| `qwen-image-edit-max` | 图像编辑 | 多图输入输出 |
| `qwen-image-edit-plus` | 图像编辑 | 通用编辑 |
| `wan2.5-i2i-preview` | 图像编辑 | 多图融合 |

### 即梦 Seedream 模型

| 模型 | 说明 | 特点 |
|------|------|------|
| `doubao-seedream-4-5-251128` | Seedream 4.5 | 最新最强，编辑一致性佳 |
| `doubao-seedream-4-0-250828` | Seedream 4.0 | 平衡预算与质量 |

**即梦特点：**
- 同一端点同时支持文生图和图像编辑（通过 `image` 参数区分）
- 同步返回结果（无需轮询）
- 最多 14 张输入图片
- 不支持 negative_prompt
- 支持 `sequential_image_generation` 批量生成多图
- 支持提示词优化（`optimize_prompt`: standard / fast）

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
  jimeng:
    enabled: true
    ark_api_key: "xxx"  # Volcengine Ark API Key (for Seedream)
```

或设置环境变量：

```bash
# 通义
export DASHSCOPE_API_KEY="sk-xxx"

# 即梦
export ARK_API_KEY="xxx"
```

### 代码示例 - 通义 (Tongyi)

```python
from src.providers.image import TongyiImageProvider, CharacterViewMode, CharacterRef

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
    character_image=character_url,
    size="1664*928",
    style="cinematic",
)

# 8. 场景合成 - 单角色
characters = [
    CharacterRef(
        name="小美",
        image_url=front_view_url,  # 正面参考图
        action="坐在咖啡桌前微笑着看向镜头",
        position="画面中央",
    )
]
task = provider.composite_character_scene(
    characters=characters,
    scene_description="一间温馨的咖啡厅，柔和的午后阳光透过落地窗照进来",
    style="cinematic",
    size="1664*928",
    n=2,
)

# 9. 场景合成 - 多角色互动
characters = [
    CharacterRef(name="小美", image_url=url_a, action="正在递给对方一本书", position="左侧"),
    CharacterRef(name="小明", image_url=url_b, action="伸手接过书，面带微笑", position="右侧"),
]
task = provider.composite_character_scene(
    characters=characters,
    scene_description="安静的图书馆内，背景是整齐的书架，温暖的灯光",
    style="cinematic",
    size="1664*928",
)
```

### 代码示例 - 即梦 Seedream (JiMeng)

```python
from src.providers.image import JiMengImageProvider, CharacterRef

# 初始化
provider = JiMengImageProvider()
provider.initialize()

# 1. 文生图 (同步返回)
task = provider.text_to_image(
    prompt="一只可爱的橘猫躺在阳光下",
    size="2K",
    model="doubao-seedream-4-5-251128",
)
print(task.image_url)  # 直接可用，无需轮询

# 2. 多图生成 (sequential generation)
task = provider.text_to_image(
    prompt="一位身穿汉服的年轻女子",
    size="2K",
    n=3,  # 自动启用 sequential_image_generation
)
# task.image_urls = [url1, url2, url3]

# 3. 图像编辑 (同一端点, 最多14张输入图)
task = provider.edit_image(
    images=[image_url],
    prompt="将这张图片转换为水彩画风格",
)

# 4. 多图融合编辑
task = provider.edit_image(
    images=[person_url, outfit_url],
    prompt="把图1中的人物换上图2中的衣服",
)

# 5. 场景合成 (最多14个角色)
characters = [
    CharacterRef(name="小美", image_url=url_a, action="微笑看向镜头", position="左侧"),
    CharacterRef(name="小明", image_url=url_b, action="伸手接过书", position="右侧"),
]
task = provider.composite_character_scene(
    characters=characters,
    scene_description="安静的图书馆内",
    style="cinematic",
    size="2K",
)

# 6. 下载图片
paths = provider.download_task_images(task, save_dir="./output", prefix="jimeng")
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

### 即梦 Seedream 4.5
| 尺寸 | 说明 |
|------|------|
| 2K | 预设，自动选择最佳分辨率 |
| 4K | 预设，超高分辨率 |
| 2560×1440 | 16:9 横屏 |
| 1440×2560 | 9:16 竖屏 |
| 2048×2048 | 1:1 正方形 |
| 3840×2160 | 4K 横屏 |

### 即梦 Seedream 4.0
| 尺寸 | 说明 |
|------|------|
| 1K | 预设 |
| 2K | 预设 |
| 4K | 预设 |
| 1280×720 | 16:9 横屏 |
| 720×1280 | 9:16 竖屏 |
| 1024×1024 | 1:1 正方形 |
| 2048×2048 | 1:1 高分辨率 |

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

# 运行场景合成测试（1-3角色、角度一致性、模型对比）
python scripts/test_scene_composition.py

# 运行即梦 Seedream 测试
python scripts/test_jimeng_image.py

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
│   ├── CharacterRef     # 场景合成角色引用
│   ├── ArtStyle         # 艺术风格枚举
│   └── ImageSize        # 图像尺寸枚举
├── tongyi.py            # 通义实现
│   ├── TongyiImageProvider
│   └── TONGYI_IMAGE_MODELS
└── jimeng.py            # 即梦 Seedream 实现
    ├── JiMengImageProvider
    └── JIMENG_IMAGE_MODELS
```

## 注意事项

- 生成的图像 URL 有效期为 24 小时，请及时下载
- 内容需符合安全审核要求
- API 调用有限流限制，请合理使用
- 角色三视图生成会调用 3 次 API（每个视角一次）
- 场景合成角色参考图应使用正面单人图，三面图会混淆模型
- **通义**: 场景合成最多 3 个角色（受限于 API 最多 3 张输入图片），推荐 `qwen-image-edit-max`
- **通义**: `wan2.5-i2i-preview` 与其他模型生成的图片 URL 可能不兼容
- **即梦**: 场景合成最多 14 个角色，同步返回，不支持 negative_prompt
- **即梦**: 使用 Ark 平台 API Key（与视频 API 的 Volcengine 签名认证不同）

## 相关文档

- [Tongyi API 文档](https://help.aliyun.com/zh/model-studio/)
- [JiMeng/Seedream API 文档](https://www.volcengine.com/docs/)
- [Image Generator App README](../src/image_generator/README.md)
