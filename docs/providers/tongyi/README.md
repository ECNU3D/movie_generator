# 通义万相 (Tongyi Wanxiang) API 集成文档

> 基于阿里云 DashScope 平台的视频生成服务
> 官方文档: https://help.aliyun.com/zh/dashscope/

## 目录

- [API基础信息](#api基础信息)
- [认证方式](#认证方式)
- [支持的模型](#支持的模型)
- [API端点](#api端点)
- [请求参数](#请求参数)
- [代码示例](#代码示例)
- [定价信息](#定价信息)

---

## API基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://dashscope.aliyuncs.com/api/v1` |
| 认证方式 | Bearer Token |
| 请求格式 | JSON |
| 异步模式 | `X-DashScope-Async: enable` |

---

## 认证方式

### 获取 API Key

1. 登录 [阿里云控制台](https://console.aliyun.com/)
2. 进入 [DashScope 控制台](https://dashscope.console.aliyun.com/)
3. 在 API-KEY 管理中创建密钥
4. API Key 格式: `sk-xxxxxxxxxxxxxxxx`

### 请求头

```http
Authorization: Bearer sk-your-api-key
Content-Type: application/json
X-DashScope-Async: enable
```

---

## 支持的模型

### 文生视频 (Text-to-Video)

| 模型 | 说明 | 音频 | 分辨率 | 时长 | 多镜头 |
|------|------|------|--------|------|--------|
| `wan2.6-t2v` | 万相2.6（推荐） | ✅ | 720P, 1080P | 5s, 10s, 15s | ✅ |
| `wan2.5-t2v-preview` | 万相2.5 preview | ✅ | 480P, 720P, 1080P | 5s, 10s | ❌ |
| `wan2.2-t2v-plus` | 万相2.2专业版 | ❌ | 480P, 1080P | 5s | ❌ |
| `wanx2.1-t2v-turbo` | 万相2.1极速版 | ❌ | 480P, 720P | 5s | ❌ |
| `wanx2.1-t2v-plus` | 万相2.1专业版 | ❌ | 720P | 5s | ❌ |

### 图生视频 (Image-to-Video)

| 模型 | 说明 | 音频 | 分辨率 | 时长 |
|------|------|------|--------|------|
| `wan2.6-i2v` | 万相2.6 图生视频 | ✅ | 720P, 1080P | 5s, 10s, 15s |

---

## API端点

### 提交视频生成任务

```
POST /services/aigc/video-generation/video-synthesis
```

### 查询任务状态

```
GET /tasks/{task_id}
```

---

## 请求参数

### 文生视频请求体

```json
{
  "model": "wan2.6-t2v",
  "input": {
    "prompt": "视频描述文本"
  },
  "parameters": {
    "resolution": "720P",
    "duration": 5,
    "prompt_extend": true,
    "audio": true,
    "shot_type": "multi"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | ✅ | 模型名称 |
| input.prompt | string | ✅ | 视频描述，建议50-500字 |
| parameters.resolution | string | ❌ | 分辨率: "480P", "720P", "1080P" |
| parameters.duration | int | ❌ | 时长: 5, 10, 15 (秒) |
| parameters.prompt_extend | bool | ❌ | 启用提示词增强 (默认 true) |
| parameters.audio | bool | ❌ | 启用音频生成 (2.5+模型) |
| parameters.shot_type | string | ❌ | "multi" 启用多镜头叙事 (wan2.6) |
| parameters.seed | int | ❌ | 随机种子 |

### 图生视频请求体

```json
{
  "model": "wan2.6-i2v",
  "input": {
    "prompt": "动作描述",
    "img_url": "https://example.com/image.jpg",
    "audio_url": "https://example.com/audio.mp3"
  },
  "parameters": {
    "resolution": "720P",
    "duration": 10,
    "prompt_extend": true,
    "audio": true
  }
}
```

### 响应格式

**提交任务响应:**
```json
{
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  },
  "request_id": "xxxxxxxx"
}
```

**查询状态响应:**
```json
{
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "SUCCEEDED",
    "video_url": "https://dashscope-result.oss.aliyuncs.com/xxx.mp4"
  }
}
```

### 任务状态

| 状态 | 说明 |
|------|------|
| PENDING | 排队中 |
| RUNNING | 生成中 |
| SUCCEEDED | 完成 |
| FAILED | 失败 |
| CANCELED | 已取消 |

---

## 代码示例

### 使用 Provider 类

```python
import sys
sys.path.insert(0, 'src')

from providers.tongyi import TongyiProvider

# 初始化
provider = TongyiProvider()

# 查看支持的模型
for model in provider.list_models():
    print(f"{model['name']}: {model['description']}")

# 文生视频
task = provider.submit_text_to_video(
    prompt="一只可爱的橘猫在阳光下打哈欠，慢镜头，电影级画质",
    duration=5,
    resolution="720P",
    model="wan2.6-t2v",
    audio=True,
    prompt_extend=True
)
print(f"Task ID: {task.task_id}")

# 等待完成
result = provider.wait_for_completion(task.task_id, timeout=300)
if result.video_url:
    print(f"Video URL: {result.video_url}")
```

### 图生视频

```python
task = provider.submit_image_to_video(
    image_url="https://example.com/cat.jpg",
    prompt="猫咪转头微笑，眼睛眨动",
    duration=5,
    model="wan2.6-i2v",
    audio=True
)
```

### 多镜头叙事 (wan2.6)

```python
task = provider.submit_text_to_video(
    prompt="""
    镜头1：清晨的咖啡馆，阳光透过窗户洒落
    镜头2：一位女孩推门而入，微笑着走向吧台
    镜头3：咖啡师熟练地制作拿铁，拉花成型
    """,
    duration=15,
    model="wan2.6-t2v",
    shot_type="multi",
    audio=True
)
```

### 直接 HTTP 调用

```python
import requests

API_KEY = "sk-your-api-key"
BASE_URL = "https://dashscope.aliyuncs.com/api/v1"

# 提交任务
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable"
}

data = {
    "model": "wan2.6-t2v",
    "input": {"prompt": "一朵花在盛开，延时摄影"},
    "parameters": {"duration": 5, "resolution": "720P", "audio": True}
}

response = requests.post(
    f"{BASE_URL}/services/aigc/video-generation/video-synthesis",
    headers=headers,
    json=data
)
task_id = response.json()["output"]["task_id"]

# 查询状态
import time
while True:
    response = requests.get(
        f"{BASE_URL}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    result = response.json()["output"]

    if result["task_status"] == "SUCCEEDED":
        print(f"Video: {result['video_url']}")
        break
    elif result["task_status"] == "FAILED":
        print("Failed!")
        break

    time.sleep(5)
```

---

## 定价信息

| 模型 | 计费方式 | 价格 |
|------|---------|------|
| wan2.6-t2v | 按次计费 | 约 0.5-1 元/次 |
| wan2.5-t2v-preview | 按次计费 | 约 0.3-0.5 元/次 |
| wan2.2-t2v-plus | 按次计费 | 约 0.2-0.3 元/次 |
| wanx2.1-t2v-turbo | 按次计费 | 约 0.1 元/次 |
| wanx2.1-t2v-plus | 按次计费 | 约 0.3 元/次 |

> 具体价格以 [DashScope 控制台](https://dashscope.console.aliyun.com/) 为准

---

## 最佳实践

### 1. 提示词优化

```
[主体] + [动作] + [场景] + [风格] + [镜头]

示例：一位年轻女性，穿着白色连衣裙，在海边漫步，
夕阳西下，电影级画质，浅景深，慢镜头，温暖色调
```

### 2. 模型选择

- **wan2.6-t2v**: 最新最强，支持音频和多镜头，推荐用于正式项目
- **wanx2.1-t2v-turbo**: 速度最快，价格最低，适合测试和原型

### 3. 成本控制

- 测试阶段使用 turbo 版本
- 生产环境使用 wan2.6 获得最佳质量
- 利用 seed 参数复现结果，避免重复生成

---

## 错误处理

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| InvalidApiKey | API Key 无效 | 检查 API Key 是否正确 |
| QuotaExhausted | 配额用尽 | 充值或等待配额重置 |
| InvalidParameter | 参数错误 | 检查请求参数格式 |
| ContentFiltered | 内容违规 | 修改提示词 |

---

## 相关链接

- [DashScope 控制台](https://dashscope.console.aliyun.com/)
- [API 文档](https://help.aliyun.com/zh/dashscope/)
- [模型广场](https://bailian.console.aliyun.com/#/model-market)

---

*文档版本: 2.0*
*最后更新: 2026-01-21*
*测试状态: ✅ 已验证*
