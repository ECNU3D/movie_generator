# 即梦AI (JiMeng AI) API 集成文档

> 基于火山引擎的视频生成服务
> 官方文档: https://www.volcengine.com/docs/85621

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
| Base URL | `https://visual.volcengineapi.com` |
| 认证方式 | HMAC-SHA256 签名 |
| 请求格式 | JSON |
| Region | cn-north-1 |
| Service | cv |

### 响应格式

```json
{
  "ResponseMetadata": {
    "RequestId": "xxx-xxx-xxx",
    "Action": "CVSync2AsyncSubmitTask",
    "Version": "2022-08-31",
    "Service": "cv",
    "Region": "cn-north-1"
  },
  "data": {
    "task_id": "971901374197657342"
  }
}
```

---

## 认证方式

### 获取密钥

1. 登录 [火山引擎控制台](https://console.volcengine.com/)
2. 进入「访问控制」->「密钥管理」
3. 创建 Access Key ID 和 Secret Access Key

### HMAC-SHA256 签名

火山引擎使用 HMAC-SHA256 签名认证，签名过程：

```
1. 构建规范请求 (Canonical Request)
2. 构建待签名字符串 (String to Sign)
3. 计算签名 (Signature)
4. 构建 Authorization 头
```

### 请求头

```http
Host: visual.volcengineapi.com
X-Date: 20260121T134540Z
X-Content-Sha256: <body-sha256-hash>
Content-Type: application/json
Authorization: HMAC-SHA256 Credential=<access-key>/<date>/<region>/<service>/request, SignedHeaders=content-type;host;x-content-sha256;x-date, Signature=<signature>
```

---

## 支持的模型

### 文生视频 (Text-to-Video)

| req_key | 名称 | 分辨率 | 时长 | 说明 |
|---------|------|--------|------|------|
| `jimeng_t2v_v30` | 视频生成3.0 (720P) | 720P | 5s, 10s | 标准版 |
| `jimeng_t2v_v30_1080p` | 视频生成3.0 (1080P) | 1080P | 5s, 10s | 高清版 |
| `jimeng_t2v_v30_pro` | 视频生成3.0 Pro | 720P, 1080P | 5s, 10s | 多镜头叙事 |

### 图生视频 (Image-to-Video)

| req_key | 名称 | 分辨率 | 时长 | 说明 |
|---------|------|--------|------|------|
| `jimeng_ti2v_v30_pro` | 视频生成3.0 Pro (图生视频) | 720P, 1080P | 5s, 10s | 首帧参考 |

### 帧数与时长对应

| 时长 | frames 参数 |
|------|-------------|
| 5秒 | 121 |
| 10秒 | 241 |

### 支持的宽高比

- `16:9` - 横屏 (推荐)
- `9:16` - 竖屏/短视频
- `4:3` - 传统比例
- `3:4` - 竖版传统
- `1:1` - 正方形

---

## API端点

### 提交任务

```
POST https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31
```

### 查询任务状态

```
POST https://visual.volcengineapi.com?Action=CVSync2AsyncGetResult&Version=2022-08-31
```

---

## 请求参数

### 文生视频请求体

```json
{
  "req_key": "jimeng_t2v_v30_1080p",
  "prompt": "一只可爱的橘猫在阳光下打哈欠，慢镜头，电影级画质",
  "frames": 121,
  "aspect_ratio": "16:9",
  "seed": -1
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| req_key | string | ✅ | 模型标识 |
| prompt | string | ✅ | 视频描述，建议不超过800字 |
| frames | int | ❌ | 帧数: 121 (5秒) 或 241 (10秒) |
| aspect_ratio | string | ❌ | 宽高比，默认 "16:9" |
| seed | int | ❌ | 随机种子，-1 为随机 |

### 图生视频请求体

```json
{
  "req_key": "jimeng_ti2v_v30_pro",
  "prompt": "猫咪转头微笑，眼睛眨动",
  "image_urls": ["https://example.com/cat.jpg"],
  "frames": 121,
  "aspect_ratio": "16:9",
  "seed": -1
}
```

### 图生视频参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image_urls | array | ✅* | 首帧图片URL数组 |
| binary_data_base64 | array | ✅* | 首帧图片Base64数组 (二选一) |

### 查询任务请求体

```json
{
  "req_key": "jimeng_t2v_v30_1080p",
  "task_id": "971901374197657342"
}
```

### 任务状态响应

```json
{
  "data": {
    "task_id": "971901374197657342",
    "status": "done",
    "video_url": "https://v3-vvecloud.yangyi08.com/xxx.mp4"
  }
}
```

### 任务状态

| 状态 | 说明 |
|------|------|
| not_start | 未开始 |
| pending | 排队中 |
| running | 生成中 |
| done / success | 完成 |
| failed / fail | 失败 |

---

## 代码示例

### 使用 Provider 类

```python
import sys
sys.path.insert(0, 'src')

from providers.jimeng import JimengProvider

# 初始化
provider = JimengProvider()

# 测试连接
result = provider.test_connection()
print(f"Connection: {result}")

# 查看支持的模型
for model in provider.list_models():
    print(f"{model['req_key']}: {model['name']}")

# 文生视频 - 1080P
task = provider.submit_text_to_video(
    prompt="一只可爱的橘猫在阳光下打哈欠，慢镜头，电影级画质",
    duration=5,
    model="jimeng_t2v_v30_1080p",
    aspect_ratio="16:9"
)
print(f"Task ID: {task.task_id}")

# 等待完成
result = provider.wait_for_completion(task.task_id, timeout=180)
if result.video_url:
    print(f"Video URL: {result.video_url}")
```

### 图生视频

```python
task = provider.submit_image_to_video(
    image_url="https://example.com/portrait.jpg",
    prompt="人物微笑，头发随风飘动",
    duration=5,
    model="jimeng_ti2v_v30_pro",
    aspect_ratio="16:9"
)
```

### 使用 Pro 版本 (多镜头叙事)

```python
task = provider.submit_text_to_video(
    prompt="""
    镜头1：清晨的山间，云雾缭绕
    镜头2：一只白鹤展翅飞过湖面
    镜头3：远处的寺庙钟声响起
    """,
    duration=10,
    model="jimeng_t2v_v30_pro",
    aspect_ratio="16:9"
)
```

### 完整 HTTP 调用示例

```python
import hashlib
import hmac
import json
import requests
from datetime import datetime, timezone
from urllib.parse import quote

def sign_request(access_key, secret_key, method, params, body):
    """生成火山引擎API签名"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%dT%H%M%SZ")
    date_short = now.strftime("%Y%m%d")

    host = "visual.volcengineapi.com"
    region = "cn-north-1"
    service = "cv"

    # 计算body哈希
    body_hash = hashlib.sha256(body.encode()).hexdigest()

    # 规范请求
    sorted_params = sorted(params.items())
    query_string = "&".join(f"{quote(k)}={quote(str(v))}" for k, v in sorted_params)

    headers_to_sign = {
        "host": host,
        "x-date": date_str,
        "x-content-sha256": body_hash,
        "content-type": "application/json",
    }

    signed_headers = ";".join(sorted(headers_to_sign.keys()))
    canonical_headers = "\n".join(f"{k}:{v}" for k, v in sorted(headers_to_sign.items()))

    canonical_request = "\n".join([
        method, "/", query_string,
        canonical_headers + "\n",
        signed_headers, body_hash
    ])

    # 签名
    credential_scope = f"{date_short}/{region}/{service}/request"
    string_to_sign = "\n".join([
        "HMAC-SHA256", date_str, credential_scope,
        hashlib.sha256(canonical_request.encode()).hexdigest()
    ])

    def hmac_sha256(key, msg):
        return hmac.new(key, msg.encode(), hashlib.sha256).digest()

    k_date = hmac_sha256(secret_key.encode(), date_short)
    k_region = hmac_sha256(k_date, region)
    k_service = hmac_sha256(k_region, service)
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

    authorization = (
        f"HMAC-SHA256 Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    return {
        "Host": host,
        "X-Date": date_str,
        "X-Content-Sha256": body_hash,
        "Content-Type": "application/json",
        "Authorization": authorization,
    }

# 使用示例
ACCESS_KEY = "your-access-key"
SECRET_KEY = "your-secret-key"

# 提交任务
body = {
    "req_key": "jimeng_t2v_v30_1080p",
    "prompt": "一朵花在盛开，延时摄影",
    "frames": 121,
    "aspect_ratio": "16:9",
    "seed": -1
}
body_str = json.dumps(body)
params = {"Action": "CVSync2AsyncSubmitTask", "Version": "2022-08-31"}

headers = sign_request(ACCESS_KEY, SECRET_KEY, "POST", params, body_str)
url = f"https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31"

response = requests.post(url, data=body_str, headers=headers)
task_id = response.json()["data"]["task_id"]
print(f"Task ID: {task_id}")

# 查询状态
import time
while True:
    query_body = {"req_key": "jimeng_t2v_v30_1080p", "task_id": task_id}
    query_body_str = json.dumps(query_body)
    query_params = {"Action": "CVSync2AsyncGetResult", "Version": "2022-08-31"}

    headers = sign_request(ACCESS_KEY, SECRET_KEY, "POST", query_params, query_body_str)
    url = f"https://visual.volcengineapi.com?Action=CVSync2AsyncGetResult&Version=2022-08-31"

    response = requests.post(url, data=query_body_str, headers=headers)
    result = response.json()["data"]

    if result["status"] in ["done", "success"]:
        print(f"Video: {result['video_url']}")
        break
    elif result["status"] in ["failed", "fail"]:
        print("Failed!")
        break

    time.sleep(10)
```

---

## 定价信息

| 模型 | 计费方式 | 价格 |
|------|---------|------|
| jimeng_t2v_v30 (720P) | 按秒计费 | 约 0.6 元/秒 |
| jimeng_t2v_v30_1080p | 按秒计费 | 约 0.8 元/秒 |
| jimeng_t2v_v30_pro | 按秒计费 | 约 1 元/秒 |
| jimeng_ti2v_v30_pro | 按秒计费 | 约 1 元/秒 |

> 具体价格以 [火山引擎控制台](https://console.volcengine.com/) 为准

### 资源包

- 支持购买资源包获取折扣
- 资源包有效期 1 年
- 用完后自动按量计费

---

## 错误处理

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| InvalidParameter | 参数错误 | 检查 req_key、prompt 等参数 |
| InvalidSignature | 签名错误 | 检查 AK/SK 和签名算法 |
| QuotaExceeded | 配额超限 | 充值或等待配额重置 |
| ContentFiltered | 内容违规 | 修改提示词 |
| TaskNotFound | 任务不存在 | 检查 task_id |

---

## 最佳实践

### 1. 提示词优化

```
建议格式：[主体] + [动作] + [场景] + [风格] + [镜头]

示例：一只可爱的橘猫，在阳光下慢慢打哈欠，
温暖的室内环境，电影级画质，慢镜头，浅景深
```

### 2. 模型选择

- **jimeng_t2v_v30**: 720P 标准版，性价比高
- **jimeng_t2v_v30_1080p**: 1080P 高清版，画质更好
- **jimeng_t2v_v30_pro**: Pro 版，支持多镜头叙事

### 3. 时长选择

- 5秒 (frames=121): 适合单一场景
- 10秒 (frames=241): 适合有情节发展的内容

### 4. 成本控制

- 测试阶段使用 720P
- 正式项目使用 1080P 或 Pro
- 利用 seed 参数复现结果

---

## 相关链接

- [火山引擎控制台](https://console.volcengine.com/)
- [即梦AI文档中心](https://www.volcengine.com/docs/85621)
- [视频生成3.0 Pro文档](https://www.volcengine.com/docs/85621/1777001)
- [计费说明](https://www.volcengine.com/docs/85621/1544715)

---

*文档版本: 2.0*
*最后更新: 2026-01-21*
*测试状态: ✅ 已验证*
