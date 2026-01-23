# 可灵 (Kling AI) API 集成文档

> 注意：本文档基于可灵AI开放平台的公开API文档整理。由于API可能会更新，请以官方文档为准。
> 官方文档地址：https://app.klingai.com/cn/dev/document-api

## 目录

- [API基础信息](#api基础信息)
- [认证方式](#认证方式)
- [速率限制和配额](#速率限制和配额)
- [支持的功能列表](#支持的功能列表)
- [API端点详细说明](#api端点详细说明)
  - [文生视频 (Text to Video)](#文生视频-text-to-video)
  - [图生视频 (Image to Video)](#图生视频-image-to-video)
  - [多图生视频 (Multi-Image to Video)](#多图生视频-multi-image-to-video)
  - [运动控制 (Motion Control)](#运动控制-motion-control)
  - [多模态生视频 (Multimodal to Video)](#多模态生视频-multimodal-to-video)
  - [视频时长扩展 (Video Duration Extension)](#视频时长扩展-video-duration-extension)
  - [OmniVideo](#omnivideo)
  - [查询任务状态](#查询任务状态)
- [视频生成参数选项](#视频生成参数选项)
- [主体参考与角色一致性](#主体参考与角色一致性)
- [代码示例](#代码示例)
- [错误码说明](#错误码说明)

---

## API基础信息

### Base URL

| 区域 | Base URL |
|------|----------|
| 中国区 | `https://api.klingai.com` |
| 国际版 | `https://api.klingai.com` |

### 请求格式

- **协议**: HTTPS
- **请求方法**: POST (创建任务), GET (查询状态)
- **内容类型**: `application/json`
- **字符编码**: UTF-8

### 响应格式

所有API响应均为JSON格式，基本结构如下：

```json
{
  "code": 0,
  "message": "success",
  "request_id": "xxx-xxx-xxx",
  "data": {
    // 具体数据
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | integer | 状态码，0表示成功 |
| message | string | 状态描述 |
| request_id | string | 请求唯一标识 |
| data | object | 返回数据 |

---

## 认证方式

### API Key 认证

可灵API使用JWT Token进行认证。需要使用Access Key (AK) 和 Secret Key (SK) 生成JWT Token。

#### 获取密钥

1. 登录 [可灵AI开放平台](https://klingai.com)
2. 进入「开发者中心」
3. 创建应用并获取 Access Key 和 Secret Key

#### JWT Token 生成

```python
import jwt
import time

def generate_jwt_token(access_key: str, secret_key: str) -> str:
    """
    生成JWT Token

    Args:
        access_key: 访问密钥
        secret_key: 秘密密钥

    Returns:
        JWT Token字符串
    """
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    payload = {
        "iss": access_key,
        "exp": int(time.time()) + 1800,  # 30分钟过期
        "nbf": int(time.time()) - 5
    }

    token = jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)
    return token
```

#### 请求头设置

```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## 速率限制和配额

### 并发限制

| 服务等级 | 并发任务数 | QPM (每分钟请求数) |
|----------|------------|-------------------|
| 免费版 | 1 | 10 |
| 基础版 | 5 | 60 |
| 专业版 | 20 | 200 |
| 企业版 | 自定义 | 自定义 |

### 配额说明

- **免费配额**: 注册后赠送一定数量的免费点数
- **付费配额**: 按需购买，支持包月和按量付费
- **配额消耗**: 不同功能和参数消耗不同点数

### 速率限制响应

当超出速率限制时，API返回：

```json
{
  "code": 429,
  "message": "Rate limit exceeded",
  "request_id": "xxx"
}
```

---

## 支持的功能列表

### 视频生成功能

| 功能 | 说明 | 模型版本 |
|------|------|---------|
| 文生视频 | 根据文本描述生成视频 | kling-v1, kling-v1-5, kling-v1-6 |
| 图生视频 | 根据参考图片生成视频 | kling-v1, kling-v1-5, kling-v1-6 |
| 多图生视频 | 多张图片融合生成视频 | kling-v1-5, kling-v1-6 |
| 运动控制 | 控制视频中物体的运动轨迹 | kling-v1-5, kling-v1-6 |
| 多模态生视频 | 结合图片、文本、音频生成视频 | kling-v1-6 |
| 视频时长扩展 | 延长已生成视频的时长 | kling-v1, kling-v1-5, kling-v1-6 |
| OmniVideo | 全能视频生成（最新） | kling-v2 |

### 图像生成功能

| 功能 | 说明 |
|------|------|
| 文生图 | 根据文本描述生成图片 |
| 图生图 | 基于参考图片生成新图片 |
| 虚拟试穿 | AI换装功能 |

---

## API端点详细说明

### 文生视频 (Text to Video)

**端点**: `POST /v1/videos/text2video`

根据文本提示词生成视频。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称：kling-v1, kling-v1-5, kling-v1-6 |
| prompt | string | 是 | 视频描述提示词，最大2000字符 |
| negative_prompt | string | 否 | 负面提示词，描述不希望出现的内容 |
| cfg_scale | float | 否 | 提示词相关性，范围0-1，默认0.5 |
| mode | string | 否 | 生成模式：std(标准), pro(专业) |
| aspect_ratio | string | 否 | 宽高比：16:9, 9:16, 1:1 |
| duration | string | 否 | 时长：5, 10 (秒) |
| camera_control | object | 否 | 摄像机控制参数 |
| callback_url | string | 否 | 任务完成回调URL |

#### 摄像机控制参数

```json
{
  "camera_control": {
    "type": "simple",  // simple, custom
    "config": {
      "horizontal": 0,   // 水平移动 -10 到 10
      "vertical": 0,     // 垂直移动 -10 到 10
      "zoom": 0,         // 缩放 -10 到 10
      "tilt": 0,         // 倾斜 -10 到 10
      "pan": 0,          // 平移 -10 到 10
      "roll": 0          // 旋转 -10 到 10
    }
  }
}
```

#### 请求示例

```json
{
  "model": "kling-v1-6",
  "prompt": "一只可爱的金毛犬在草地上奔跑，阳光明媚，4K画质",
  "negative_prompt": "模糊,低质量,变形",
  "cfg_scale": 0.5,
  "mode": "pro",
  "aspect_ratio": "16:9",
  "duration": "5"
}
```

#### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "request_id": "req_abc123",
  "data": {
    "task_id": "task_xyz789",
    "task_status": "submitted",
    "created_at": 1705500000
  }
}
```

---

### 图生视频 (Image to Video)

**端点**: `POST /v1/videos/image2video`

根据参考图片生成视频。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称 |
| image | string | 是 | 图片URL或Base64编码 |
| image_tail | string | 否 | 尾帧图片（用于首尾帧控制） |
| prompt | string | 否 | 运动描述提示词 |
| negative_prompt | string | 否 | 负面提示词 |
| cfg_scale | float | 否 | 提示词相关性 |
| mode | string | 否 | 生成模式 |
| duration | string | 否 | 时长：5, 10 |
| camera_control | object | 否 | 摄像机控制 |
| callback_url | string | 否 | 回调URL |

#### 请求示例

```json
{
  "model": "kling-v1-6",
  "image": "https://example.com/image.jpg",
  "prompt": "人物微笑并向镜头挥手",
  "mode": "pro",
  "duration": "5"
}
```

---

### 多图生视频 (Multi-Image to Video)

**端点**: `POST /v1/videos/multi-image2video`

使用多张图片生成视频，支持关键帧控制。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称 |
| images | array | 是 | 图片数组（最多4张） |
| prompt | string | 否 | 运动描述 |
| negative_prompt | string | 否 | 负面提示词 |
| mode | string | 否 | 生成模式 |
| duration | string | 否 | 时长 |
| callback_url | string | 否 | 回调URL |

#### 图片数组格式

```json
{
  "images": [
    {
      "url": "https://example.com/frame1.jpg",
      "timestamp": 0
    },
    {
      "url": "https://example.com/frame2.jpg",
      "timestamp": 2.5
    },
    {
      "url": "https://example.com/frame3.jpg",
      "timestamp": 5
    }
  ]
}
```

---

### 运动控制 (Motion Control)

**端点**: `POST /v1/videos/motion-control`

通过轨迹或区域控制视频中物体的运动。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称 |
| image | string | 是 | 参考图片 |
| prompt | string | 否 | 运动描述 |
| motion_brush | object | 否 | 运动笔刷控制 |
| trajectory | array | 否 | 运动轨迹点 |
| callback_url | string | 否 | 回调URL |

#### 运动轨迹格式

```json
{
  "trajectory": [
    {"x": 0.2, "y": 0.5, "t": 0},
    {"x": 0.5, "y": 0.3, "t": 0.5},
    {"x": 0.8, "y": 0.5, "t": 1.0}
  ]
}
```

---

### 多模态生视频 (Multimodal to Video)

**端点**: `POST /v1/videos/multimodal2video`

结合图片、文本、音频等多模态输入生成视频。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称 |
| inputs | array | 是 | 多模态输入数组 |
| prompt | string | 否 | 总体描述 |
| mode | string | 否 | 生成模式 |
| duration | string | 否 | 时长 |
| callback_url | string | 否 | 回调URL |

#### 多模态输入格式

```json
{
  "inputs": [
    {
      "type": "image",
      "url": "https://example.com/bg.jpg",
      "role": "background"
    },
    {
      "type": "image",
      "url": "https://example.com/character.jpg",
      "role": "subject"
    },
    {
      "type": "audio",
      "url": "https://example.com/bgm.mp3",
      "role": "background_music"
    }
  ]
}
```

---

### 视频时长扩展 (Video Duration Extension)

**端点**: `POST /v1/videos/extend`

延长已生成视频的时长。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型名称 |
| video_id | string | 是 | 原视频任务ID |
| prompt | string | 否 | 扩展内容描述 |
| extend_duration | string | 否 | 扩展时长：5, 10 |
| callback_url | string | 否 | 回调URL |

#### 请求示例

```json
{
  "model": "kling-v1-6",
  "video_id": "task_xyz789",
  "prompt": "继续奔跑，然后停下来看向镜头",
  "extend_duration": "5"
}
```

---

### OmniVideo

**端点**: `POST /v1/videos/omni`

最新的全能视频生成接口，支持更灵活的输入和更高质量的输出。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | kling-v2 |
| prompt | string | 是 | 视频描述 |
| reference_images | array | 否 | 参考图片数组 |
| style | string | 否 | 风格预设 |
| quality | string | 否 | 质量：standard, high |
| aspect_ratio | string | 否 | 宽高比 |
| duration | integer | 否 | 时长（秒） |
| fps | integer | 否 | 帧率：24, 30, 60 |
| callback_url | string | 否 | 回调URL |

---

### 查询任务状态

**端点**: `GET /v1/videos/tasks/{task_id}`

查询视频生成任务的状态和结果。

#### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "task_xyz789",
    "task_status": "completed",
    "task_status_msg": "生成成功",
    "created_at": 1705500000,
    "updated_at": 1705500300,
    "task_result": {
      "videos": [
        {
          "id": "video_001",
          "url": "https://cdn.klingai.com/videos/xxx.mp4",
          "cover_url": "https://cdn.klingai.com/covers/xxx.jpg",
          "duration": 5,
          "width": 1920,
          "height": 1080
        }
      ]
    }
  }
}
```

#### 任务状态说明

| 状态 | 说明 |
|------|------|
| submitted | 已提交 |
| processing | 处理中 |
| completed | 已完成 |
| failed | 失败 |

---

## 视频生成参数选项

### 分辨率与宽高比

| 宽高比 | 分辨率 | 说明 |
|--------|--------|------|
| 16:9 | 1920x1080, 1280x720 | 横屏，适合电影/YouTube |
| 9:16 | 1080x1920, 720x1280 | 竖屏，适合短视频/抖音 |
| 1:1 | 1080x1080, 720x720 | 方形，适合社交媒体 |
| 4:3 | 1440x1080 | 传统比例 |
| 3:4 | 1080x1440 | 竖屏传统比例 |
| 21:9 | 2560x1080 | 超宽屏 |

### 视频时长

| 模式 | 支持时长 |
|------|----------|
| 标准模式 | 5秒 |
| 专业模式 | 5秒, 10秒 |
| 时长扩展 | 可扩展至最长60秒 |

### 生成模式

| 模式 | 说明 | 消耗点数 |
|------|------|----------|
| std (标准) | 快速生成，基础质量 | 1x |
| pro (专业) | 慢速生成，高质量 | 2x |

### 风格预设

可灵支持多种风格预设：

- `realistic` - 写实风格
- `anime` - 动漫风格
- `3d_cartoon` - 3D卡通
- `cinematic` - 电影风格
- `artistic` - 艺术风格

---

## 主体参考与角色一致性

可灵AI支持主体参考功能，可以在多个视频中保持角色/主体的一致性。

### 使用方法

1. **上传参考图片**: 提供清晰的角色/主体参考图
2. **设置主体类型**: 指定是人物、动物还是物品
3. **在提示词中引用**: 使用特定语法引用主体

### 主体参考参数

```json
{
  "subject_reference": {
    "enabled": true,
    "images": [
      {
        "url": "https://example.com/character.jpg",
        "type": "character",
        "name": "主角"
      }
    ],
    "strength": 0.8
  }
}
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| enabled | boolean | 是否启用主体参考 |
| images | array | 参考图片数组 |
| type | string | 主体类型：character, animal, object |
| name | string | 主体名称，用于提示词引用 |
| strength | float | 参考强度，0-1 |

### 使用示例

```json
{
  "model": "kling-v1-6",
  "prompt": "[主角]在咖啡馆里喝咖啡，看向窗外",
  "subject_reference": {
    "enabled": true,
    "images": [
      {
        "url": "https://example.com/my-character.jpg",
        "type": "character",
        "name": "主角"
      }
    ],
    "strength": 0.85
  },
  "mode": "pro",
  "duration": "5"
}
```

---

## 代码示例

### Python 完整示例

```python
import jwt
import time
import requests
from typing import Optional, Dict, Any

class KlingAIClient:
    """可灵AI API客户端"""

    def __init__(self, access_key: str, secret_key: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://api.klingai.com"

    def _generate_token(self) -> str:
        """生成JWT Token"""
        headers = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": self.access_key,
            "exp": int(time.time()) + 1800,
            "nbf": int(time.time()) - 5
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256", headers=headers)

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._generate_token()}",
            "Content-Type": "application/json"
        }

        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=data)

        response.raise_for_status()
        return response.json()

    def text_to_video(
        self,
        prompt: str,
        model: str = "kling-v1-6",
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9",
        duration: str = "5",
        mode: str = "std",
        cfg_scale: float = 0.5,
        camera_control: Optional[Dict] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """文生视频"""
        data = {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "mode": mode,
            "cfg_scale": cfg_scale
        }

        if negative_prompt:
            data["negative_prompt"] = negative_prompt
        if camera_control:
            data["camera_control"] = camera_control
        if callback_url:
            data["callback_url"] = callback_url

        return self._request("POST", "/v1/videos/text2video", data)

    def image_to_video(
        self,
        image: str,
        prompt: Optional[str] = None,
        model: str = "kling-v1-6",
        duration: str = "5",
        mode: str = "std",
        image_tail: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """图生视频"""
        data = {
            "model": model,
            "image": image,
            "duration": duration,
            "mode": mode
        }

        if prompt:
            data["prompt"] = prompt
        if image_tail:
            data["image_tail"] = image_tail
        if callback_url:
            data["callback_url"] = callback_url

        return self._request("POST", "/v1/videos/image2video", data)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        return self._request("GET", f"/v1/videos/tasks/{task_id}")

    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = 600,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """等待任务完成"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.get_task_status(task_id)
            status = result.get("data", {}).get("task_status")

            if status == "completed":
                return result
            elif status == "failed":
                raise Exception(f"Task failed: {result}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Task {task_id} timed out after {timeout} seconds")


# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = KlingAIClient(
        access_key="your_access_key",
        secret_key="your_secret_key"
    )

    # 文生视频
    result = client.text_to_video(
        prompt="一只可爱的柴犬在樱花树下奔跑，春天的阳光洒落",
        aspect_ratio="16:9",
        duration="5",
        mode="pro"
    )

    task_id = result["data"]["task_id"]
    print(f"任务已提交，ID: {task_id}")

    # 等待完成
    final_result = client.wait_for_completion(task_id)
    video_url = final_result["data"]["task_result"]["videos"][0]["url"]
    print(f"视频生成完成: {video_url}")
```

### Node.js 示例

```javascript
const jwt = require('jsonwebtoken');
const axios = require('axios');

class KlingAIClient {
  constructor(accessKey, secretKey) {
    this.accessKey = accessKey;
    this.secretKey = secretKey;
    this.baseUrl = 'https://api.klingai.com';
  }

  generateToken() {
    const now = Math.floor(Date.now() / 1000);
    const payload = {
      iss: this.accessKey,
      exp: now + 1800,
      nbf: now - 5
    };
    return jwt.sign(payload, this.secretKey, { algorithm: 'HS256' });
  }

  async request(method, endpoint, data = null) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Authorization': `Bearer ${this.generateToken()}`,
      'Content-Type': 'application/json'
    };

    const config = { method, url, headers };
    if (data) config.data = data;

    const response = await axios(config);
    return response.data;
  }

  async textToVideo(options) {
    const data = {
      model: options.model || 'kling-v1-6',
      prompt: options.prompt,
      aspect_ratio: options.aspectRatio || '16:9',
      duration: options.duration || '5',
      mode: options.mode || 'std',
      cfg_scale: options.cfgScale || 0.5
    };

    if (options.negativePrompt) data.negative_prompt = options.negativePrompt;
    if (options.cameraControl) data.camera_control = options.cameraControl;
    if (options.callbackUrl) data.callback_url = options.callbackUrl;

    return this.request('POST', '/v1/videos/text2video', data);
  }

  async getTaskStatus(taskId) {
    return this.request('GET', `/v1/videos/tasks/${taskId}`);
  }
}

// 使用示例
async function main() {
  const client = new KlingAIClient('your_access_key', 'your_secret_key');

  const result = await client.textToVideo({
    prompt: '日落时分，海边的灯塔，海鸥飞过',
    aspectRatio: '16:9',
    duration: '5',
    mode: 'pro'
  });

  console.log('任务ID:', result.data.task_id);
}

main().catch(console.error);
```

### cURL 示例

```bash
# 生成JWT Token (需要自行实现或使用工具)
JWT_TOKEN="your_jwt_token"

# 文生视频
curl -X POST "https://api.klingai.com/v1/videos/text2video" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kling-v1-6",
    "prompt": "一只猫咪在窗台上晒太阳，温暖的午后",
    "aspect_ratio": "16:9",
    "duration": "5",
    "mode": "std"
  }'

# 查询任务状态
curl -X GET "https://api.klingai.com/v1/videos/tasks/task_xyz789" \
  -H "Authorization: Bearer ${JWT_TOKEN}"
```

---

## 错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式和必填项 |
| 401 | 认证失败 | 检查JWT Token是否正确/过期 |
| 403 | 权限不足 | 检查账户权限和配额 |
| 404 | 资源不存在 | 检查任务ID是否正确 |
| 429 | 超出速率限制 | 降低请求频率，稍后重试 |
| 500 | 服务器内部错误 | 稍后重试，如持续请联系支持 |
| 503 | 服务不可用 | 服务器维护中，稍后重试 |

### 业务错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 提示词包含敏感内容 |
| 1002 | 图片格式不支持 |
| 1003 | 图片尺寸超出限制 |
| 1004 | 配额不足 |
| 1005 | 任务队列已满 |
| 1006 | 模型不可用 |

---

## 最佳实践

### 1. 提示词优化

- 使用详细的场景描述
- 包含主体、动作、环境、光线等要素
- 使用负面提示词排除不想要的元素
- 参考示例：「一位年轻女性在咖啡馆窗边阅读，柔和的自然光，浅景深，电影质感」

### 2. 错误处理

```python
try:
    result = client.text_to_video(prompt="...")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # 速率限制，等待后重试
        time.sleep(60)
        result = client.text_to_video(prompt="...")
    else:
        raise
```

### 3. 异步处理

对于批量任务，建议使用回调URL或异步轮询：

```python
# 提交多个任务
task_ids = []
for prompt in prompts:
    result = client.text_to_video(prompt=prompt)
    task_ids.append(result["data"]["task_id"])

# 批量检查状态
completed = []
while len(completed) < len(task_ids):
    for task_id in task_ids:
        if task_id not in completed:
            status = client.get_task_status(task_id)
            if status["data"]["task_status"] == "completed":
                completed.append(task_id)
    time.sleep(10)
```

---

## 参考链接

- [可灵AI官网](https://klingai.com)
- [开发者中心](https://app.klingai.com/cn/dev/document-api)
- [API状态页面](https://status.klingai.com)

---

> 文档版本: 1.0
> 最后更新: 2026-01-18
>
> 注意：本文档基于公开信息整理，API规格可能随时更新，请以官方文档为准。
