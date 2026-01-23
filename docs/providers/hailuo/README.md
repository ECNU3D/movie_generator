# 海螺视频 (Hailuo AI / MiniMax) API 文档

## 概述

海螺视频是 MiniMax 推出的 AI 视频生成服务，支持文生视频、图生视频、首尾帧生成视频以及主体参考生成视频等多种功能。

## API 基础信息

### Base URL

```
https://api.minimaxi.com
```

### 认证方式

使用 HTTP Bearer 认证，在请求头中添加：

```
Authorization: Bearer <YOUR_API_KEY>
```

API Key 可在 [MiniMax 平台](https://platform.minimaxi.com) 的账户管理 - 接口密钥页面获取。

### 请求格式

```
Content-Type: application/json
```

---

## 速率限制和配额

### 视频生成 API 限制

| 用户类型 | RPM (每分钟请求数) |
|----------|-------------------|
| 免费用户 | 5 RPM |
| 充值用户 | 20 RPM |

### 说明

- 主账号与子账号共享速率限制配额
- 触发限制时，API 将返回错误码 `1002`（限流）
- 如需提升限制，可联系官方客服或发送邮件至 api@minimaxi.com（通常需 3-5 个工作日审批）

---

## 支持的功能列表

| 功能 | 说明 | 支持的模型 |
|------|------|-----------|
| 文生视频 (T2V) | 通过文本描述生成视频 | MiniMax-Hailuo-2.3, MiniMax-Hailuo-02, T2V-01-Director, T2V-01 |
| 图生视频 (I2V) | 以图片作为首帧生成视频 | MiniMax-Hailuo-2.3, MiniMax-Hailuo-2.3-Fast, MiniMax-Hailuo-02, I2V-01-Director, I2V-01-live, I2V-01 |
| 首尾帧生成视频 (FL2V) | 指定首帧和尾帧图片生成过渡视频 | MiniMax-Hailuo-02 |
| 主体参考生成视频 (S2V) | 基于人物主体图片保持角色一致性 | S2V-01 |

---

## API 端点详细说明

### 1. 视频生成 (通用端点)

所有视频生成任务使用同一端点，通过参数区分不同功能。

**端点：** `POST /v1/video_generation`

#### 1.1 文生视频 (Text-to-Video)

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称：`MiniMax-Hailuo-2.3`、`MiniMax-Hailuo-02`、`T2V-01-Director`、`T2V-01` |
| `prompt` | string | 是 | 视频文本描述，最大 2000 字符 |
| `duration` | integer | 否 | 视频时长（秒），默认 6，支持 6 或 10 |
| `resolution` | string | 否 | 分辨率：`720P`、`768P`、`1080P` |
| `prompt_optimizer` | boolean | 否 | 是否自动优化 prompt，默认 `true` |
| `fast_pretreatment` | boolean | 否 | 缩短优化耗时，默认 `false` |
| `callback_url` | string | 否 | 异步回调地址 |
| `aigc_watermark` | boolean | 否 | 是否添加水印，默认 `false` |

**代码示例：**

```bash
curl --request POST \
  --url https://api.minimaxi.com/v1/video_generation \
  --header 'Authorization: Bearer <YOUR_API_KEY>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "MiniMax-Hailuo-2.3",
    "prompt": "A man picks up a book [Pedestal up], then reads [Static shot].",
    "duration": 6,
    "resolution": "1080P"
  }'
```

#### 1.2 图生视频 (Image-to-Video)

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称（见上方支持的模型列表） |
| `first_frame_image` | string | 是 | 首帧图片 URL 或 Base64 Data URL |
| `prompt` | string | 否 | 视频文本描述，最大 2000 字符 |
| `duration` | integer | 否 | 视频时长（秒），默认 6 |
| `resolution` | string | 否 | 分辨率 |
| `prompt_optimizer` | boolean | 否 | 是否自动优化 prompt，默认 `true` |
| `fast_pretreatment` | boolean | 否 | 缩短优化耗时，默认 `false` |
| `callback_url` | string | 否 | 异步回调地址 |
| `aigc_watermark` | boolean | 否 | 是否添加水印，默认 `false` |

**图片要求：**
- 格式：JPG、JPEG、PNG、WebP
- 体积：小于 20MB
- 尺寸：短边像素大于 300px，长宽比在 2:5 至 5:2 之间

**代码示例：**

```bash
curl --request POST \
  --url https://api.minimaxi.com/v1/video_generation \
  --header 'Authorization: Bearer <YOUR_API_KEY>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "MiniMax-Hailuo-2.3",
    "prompt": "A mouse runs toward the camera.",
    "first_frame_image": "https://example.com/image.jpg",
    "duration": 6,
    "resolution": "1080P"
  }'
```

#### 1.3 首尾帧生成视频 (First-Last-to-Video)

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 固定为 `MiniMax-Hailuo-02` |
| `first_frame_image` | string | 是 | 首帧图片 URL 或 Base64 Data URL |
| `last_frame_image` | string | 是 | 尾帧图片 URL 或 Base64 Data URL |
| `prompt` | string | 否 | 视频文本描述，最大 2000 字符 |
| `duration` | integer | 否 | 视频时长（秒），支持 6 或 10 |
| `resolution` | string | 否 | 分辨率：`768P`（默认）或 `1080P`，不支持 `512P` |
| `prompt_optimizer` | boolean | 否 | 是否自动优化 prompt，默认 `true` |
| `callback_url` | string | 否 | 异步回调地址 |
| `aigc_watermark` | boolean | 否 | 是否添加水印，默认 `false` |

**注意：** 生成视频尺寸遵循首帧图片。当首帧和尾帧尺寸不一致时，模型将参考首帧对尾帧进行裁剪。

**代码示例：**

```bash
curl --request POST \
  --url https://api.minimaxi.com/v1/video_generation \
  --header 'Authorization: Bearer <YOUR_API_KEY>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "MiniMax-Hailuo-02",
    "prompt": "A little girl grows up.",
    "first_frame_image": "https://example.com/first.jpg",
    "last_frame_image": "https://example.com/last.jpg",
    "duration": 6,
    "resolution": "1080P"
  }'
```

#### 1.4 主体参考生成视频 (Subject-to-Video)

**请求参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 固定为 `S2V-01` |
| `subject_reference` | array | 是 | 主体参考信息，目前仅支持单个主体 |
| `prompt` | string | 否 | 视频文本描述，最大 2000 字符 |
| `prompt_optimizer` | boolean | 否 | 是否自动优化 prompt，默认 `true` |
| `callback_url` | string | 否 | 异步回调地址 |
| `aigc_watermark` | boolean | 否 | 是否添加水印，默认 `false` |

**主体参考结构：**

```json
{
  "subject_reference": [
    {
      "type": "character",
      "image": ["https://example.com/character.jpg"]
    }
  ]
}
```

- `type`：参考类型，设置为 `"character"`（人物主体）
- `image`：参考图片数组

**代码示例：**

```bash
curl --request POST \
  --url https://api.minimaxi.com/v1/video_generation \
  --header 'Authorization: Bearer <YOUR_API_KEY>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "S2V-01",
    "prompt": "A girl runs toward the camera and winks with a smile.",
    "subject_reference": [
      {
        "type": "character",
        "image": ["https://example.com/character.jpg"]
      }
    ]
  }'
```

---

### 2. 查询任务状态

**端点：** `GET /v1/query/video_generation`

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | 是 | 待查询的任务 ID |

**响应字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 被查询的任务 ID |
| `status` | string | 任务当前状态 |
| `file_id` | string | 任务成功时返回，用于获取视频文件 |
| `video_width` | integer | 任务成功时返回，视频宽度（像素） |
| `video_height` | integer | 任务成功时返回，视频高度（像素） |
| `base_resp` | object | 包含 `status_code` 和 `status_msg` |

**任务状态说明：**

| 状态 | 说明 |
|------|------|
| `Preparing` | 准备中 |
| `Queueing` | 队列中 |
| `Processing` | 生成中 |
| `Success` | 成功 |
| `Fail` | 失败 |

**代码示例：**

```bash
curl --request GET \
  --url 'https://api.minimaxi.com/v1/query/video_generation?task_id=176843862716480' \
  --header 'Authorization: Bearer <YOUR_API_KEY>'
```

**响应示例：**

```json
{
  "task_id": "176843862716480",
  "status": "Success",
  "file_id": "176844028768320",
  "video_width": 1920,
  "video_height": 1080,
  "base_resp": {
    "status_code": 0,
    "status_msg": "success"
  }
}
```

---

### 3. 下载视频文件

**端点：** `GET /v1/files/retrieve_content`

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file_id` | integer | 是 | 需要下载的文件 ID |

**代码示例：**

```bash
curl --request GET \
  --url 'https://api.minimaxi.com/v1/files/retrieve_content?file_id=176844028768320' \
  --header 'Authorization: Bearer <YOUR_API_KEY>' \
  --output video.mp4
```

---

## 视频生成参数选项

### 分辨率支持

| 模型 | 6 秒时长 | 10 秒时长 |
|------|---------|---------|
| MiniMax-Hailuo-2.3 | 768P / 1080P | 768P |
| MiniMax-Hailuo-02 | 512P / 768P / 1080P | 512P / 768P |
| T2V-01 / I2V-01 等 | 720P | 不支持 |

### 运镜指令

Prompt 支持 15 种运镜指令（可在提示词中使用 `[指令]` 格式）：

| 类别 | 指令 |
|------|------|
| 平移 | `[左移]` `[右移]` |
| 摇摄 | `[左摇]` `[右摇]` `[上摇]` `[下摇]` |
| 推拉 | `[推进]` `[拉远]` |
| 升降 | `[上升]` `[下降]` |
| 变焦 | `[变焦推近]` `[变焦拉远]` |
| 其他 | `[晃动]` `[跟随]` `[固定]` |

**使用示例：**
```
A man walks down the street [跟随], then turns around [左摇].
```

可以组合使用多个指令，如 `[左摇,上升]`，建议不超过 3 个。

---

## 主体参考/角色一致性

海螺视频通过 **S2V-01** 模型支持主体参考功能，可以保持视频中角色的一致性。

### 功能特点

- 支持人物主体类型（`type: "character"`）
- 目前仅支持单个主体参考
- 通过提供角色参考图片，生成的视频将保持该角色的外观特征

### 使用方法

1. 准备角色参考图片
2. 在请求中使用 `subject_reference` 参数
3. 设置 `model` 为 `S2V-01`

---

## 回调机制

配置 `callback_url` 后，MiniMax 服务器会在任务状态变化时推送通知。

**回调状态：**

| 状态 | 说明 |
|------|------|
| `processing` | 生成中 |
| `success` | 成功 |
| `failed` | 失败 |

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1002 | 限流（触发速率限制） |
| 1004 | 认证失败 |
| 1008 | 余额不足 |
| 1026 | 敏感内容 |
| 2013 | 参数异常 |
| 2049 | 无效 API Key |

---

## 定价信息

### 资源包套餐

| 套餐 | 价格 | 有效期 | 积分 | RPM | 折扣 |
|------|------|--------|------|-----|------|
| 视频基础包 | ¥7,000 | 1 个月 | 3,680 | 20 | 5% |
| 视频高级包 | ¥15,000 | 1 个月 | 8,330 | 30 | 10% |
| 视频进阶包 | ¥30,000 | 1 个月 | 17,650 | 40 | 15% |
| 视频企业包 | ¥40,000 | 1 个月 | 25,000 | 50 | 20% |

### 积分消耗标准

| 模型 | 分辨率 | 时长 | 消耗积分 |
|------|--------|------|----------|
| Hailuo-2.3-Fast | 768P | 6 秒 | 0.7 |
| Hailuo-2.3-Fast | 768P | 10 秒 | 1.1 |
| Hailuo-2.3-Fast | 1080P | 6 秒 | 1.3 |
| Hailuo-02 | 512P | 6 秒 | 0.3 |
| Hailuo-02 | 512P | 10 秒 | 0.5 |
| Hailuo-02/2.3 | 768P | 6 秒 | 1.0 |
| Hailuo-02/2.3 | 768P | 10 秒 | 2.0 |
| Hailuo-02/2.3 | 1080P | 6 秒 | 2.0 |

### 计费说明

- 生成失败或审核不通过的视频不扣积分
- 资源包积分不继承，过期自动清零

---

## 完整代码示例

### Python 示例

```python
import requests
import time

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.minimaxi.com"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 1. 创建视频生成任务
def create_video_task(prompt, model="MiniMax-Hailuo-2.3", duration=6, resolution="1080P"):
    url = f"{BASE_URL}/v1/video_generation"
    data = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# 2. 查询任务状态
def query_task(task_id):
    url = f"{BASE_URL}/v1/query/video_generation"
    params = {"task_id": task_id}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 3. 下载视频
def download_video(file_id, output_path):
    url = f"{BASE_URL}/v1/files/retrieve_content"
    params = {"file_id": file_id}
    response = requests.get(url, headers=headers, params=params)
    with open(output_path, "wb") as f:
        f.write(response.content)

# 主流程
def generate_video(prompt):
    # 创建任务
    result = create_video_task(prompt)
    task_id = result["task_id"]
    print(f"Task created: {task_id}")

    # 轮询查询状态
    while True:
        status_result = query_task(task_id)
        status = status_result["status"]
        print(f"Status: {status}")

        if status == "Success":
            file_id = status_result["file_id"]
            download_video(file_id, "output.mp4")
            print("Video downloaded successfully!")
            break
        elif status == "Fail":
            print("Video generation failed!")
            break

        time.sleep(10)  # 等待 10 秒后再次查询

# 使用示例
generate_video("A beautiful sunset over the ocean [推进]")
```

---

## 相关链接

- [MiniMax 开发者平台](https://platform.minimaxi.com)
- [API 文档](https://platform.minimaxi.com/docs)
- [海螺视频官网](https://hailuoai.com)
