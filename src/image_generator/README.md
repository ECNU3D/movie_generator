# AI Image Generator

AI 图像生成测试模块，支持通义图像模型的各种图像生成功能。

## 功能

### 1. 文生图 (Text-to-Image)
- 根据文本描述生成图像
- 支持多种尺寸和风格
- 智能提示词增强

### 2. 帧生成 (Frame Generation)
- 为视频生成首帧/尾帧图像
- 支持纯文本生成或角色参考模式
- 保持角色一致性

### 3. 角色设计 (Character Design)
- **正面图生成**: 根据描述生成角色正面图
- **三视图生成**: 支持三种模式
  - 单张三视图: 一张图包含正面/侧面/背面
  - 三张独立图: 分别生成三个角度
  - 转面设定图: 专业游戏/动画角色设定图

### 4. 图像编辑 (Image Editing)
- 多图融合
- 内容修改
- 风格迁移

## 支持的模型

| 模型 | 类型 | 说明 |
|------|------|------|
| qwen-image-plus | 文生图 | 通义千问 Plus，支持复杂文字 |
| qwen-image-max | 文生图 | 通义千问 Max，最高质量 |
| wan2.6-t2i | 文生图 | 通义万相2.6，写实摄影风格 |
| qwen-image-edit-max | 图像编辑 | 多图输入输出 |
| qwen-image-edit-plus | 图像编辑 | 通用编辑 |
| wan2.5-i2i-preview | 图像编辑 | 多图融合 |

## 快速开始

### 安装依赖

```bash
pip install dashscope
```

### 配置 API Key

在 `src/providers/config.local.yaml` 中配置:

```yaml
providers:
  tongyi:
    enabled: true
    api_key: "sk-xxx"  # DashScope API Key
```

### 启动测试 App

```bash
./scripts/run_image_generator.sh
# 或
streamlit run src/image_generator/app.py --server.port 8503
```

访问 http://localhost:8503

### 代码调用

```python
from src.providers.image import TongyiImageProvider, CharacterViewMode

# 初始化
provider = TongyiImageProvider()
provider.initialize()

# 文生图
task = provider.text_to_image(
    prompt="一只可爱的橘猫",
    size="1328*1328",
)
print(task.image_url)

# 生成视频帧
task = provider.generate_frame(
    prompt="樱花树下的少女",
    size="1664*928",  # 16:9
    style="cinematic",
)

# 生成角色正面图
task = provider.generate_character_front_view(
    character_description="25岁亚洲女性，长黑发，穿白色连衣裙",
    style="realistic",
)

# 生成角色三视图
task = provider.generate_character_views(
    front_image_url=task.image_url,
    character_description="同上",
    mode=CharacterViewMode.SINGLE_IMAGE_THREE_VIEWS,
)
```

## 图像尺寸

### 通义千问 (Qwen-Image)
- 1664*928 (16:9)
- 928*1664 (9:16)
- 1328*1328 (1:1)
- 1472*1104 (4:3)
- 1104*1472 (3:4)

### 通义万相 (Wanx)
- 1024*1024 (1:1)
- 1440*810 (16:9)
- 810*1440 (9:16)
- 1440*1080 (4:3)
- 1080*1440 (3:4)

## 注意事项

- 生成的图像 URL 有效期为 24 小时，请及时下载
- 内容需符合安全审核要求
- API 调用有限流限制，请合理使用

## 相关文档

- [Image Provider 详细文档](../../docs/IMAGE_PROVIDER.md)
- [Tongyi API 文档](https://help.aliyun.com/zh/model-studio/)
- [Image Provider 源码](../providers/image/)
