# Video Platform Comparison App

多视频平台生成效果对比工具，支持同一提示词在多个 AI 视频平台上的并行生成和效果对比。

## 功能特点

- **多平台支持**: 可灵(Kling)、海螺(Hailuo)、即梦(Jimeng)、通义万相(Tongyi)
- **并行生成**: 同一提示词同时提交到多个平台
- **效果对比**: 统一界面展示不同平台的生成结果
- **生成模式**: 支持文生视频和图生视频两种模式
- **任务管理**: 实时查看各平台生成进度和状态

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

创建 `src/providers/config.local.yaml`:

```yaml
providers:
  kling:
    access_key: "your-kling-access-key"
    secret_key: "your-kling-secret-key"
  hailuo:
    api_key: "your-hailuo-api-key"
  jimeng:
    access_key: "your-jimeng-access-key"
    secret_key: "your-jimeng-secret-key"
  tongyi:
    api_key: "your-tongyi-api-key"
```

### 启动应用

```bash
# 方式一：使用脚本
./run_comparison.sh

# 方式二：直接运行
streamlit run src/comparison/app.py --server.port 8501
```

访问 http://localhost:8501

## 使用说明

### 1. 选择平台
在侧边栏勾选要对比的视频平台（可多选）

### 2. 输入提示词
在主界面输入视频生成提示词，例如：
```
一只可爱的橘猫在阳光下打盹，毛发蓬松，画面温馨
```

### 3. 选择模式
- **文生视频**: 仅使用文字提示词生成视频
- **图生视频**: 上传参考图片 + 提示词生成视频

### 4. 开始生成
点击"生成"按钮，系统会并行向选中的平台提交任务

### 5. 查看结果
生成完成后，可在同一界面对比各平台的视频效果

## 支持的平台

| 平台 | 文生视频 | 图生视频 | 首尾帧 | 主体参考 |
|------|:--------:|:--------:|:------:|:--------:|
| 可灵 (Kling) | ✅ | ✅ | ✅ | ✅ |
| 海螺 (Hailuo) | ✅ | ✅ | ✅ | ✅ |
| 即梦 (Jimeng) | ✅ | ✅ | ❌ | ⚠️ |
| 通义万相 (Tongyi) | ✅ | ✅ | ❌ | ⚠️ |

## 项目结构

```
src/comparison/
├── app.py                 # Streamlit 主应用
├── model_capabilities.py  # 平台能力配置
└── README.md             # 本文档

src/providers/            # 视频平台 Provider
├── base.py              # 基类定义
├── kling.py             # 可灵 API
├── hailuo.py            # 海螺 API
├── jimeng.py            # 即梦 API
├── tongyi.py            # 通义万相 API
└── config.py            # 配置管理
```

## 输出目录

生成的视频保存在 `comparison_output/` 目录下。

## 相关文档

- [视频平台 API 文档](../../docs/providers/README.md)
- [平台能力对比](../../api_doc/)
