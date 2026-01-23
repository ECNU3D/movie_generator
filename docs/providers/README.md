# AI视频生成平台集成文档

本目录包含所有视频生成平台的API集成文档，每个平台都有详细的接口说明、参数文档和代码示例。

## 已支持平台

### 1. 可灵 (Kling AI) 📁 [kling/](./kling/)

- **文档大小**: 23KB
- **Base URL**: `https://api.klingai.com`
- **认证方式**: JWT Token (AK/SK)
- **主要功能**:
  - ✅ 文生视频 (Text to Video)
  - ✅ 图生视频 (Image to Video)
  - ✅ 多图生视频
  - ✅ 运动控制
  - ✅ 多模态生视频
  - ✅ 视频时长扩展
  - ✅ OmniVideo
- **支持分辨率**: 720P, 1080P, 多种比例
- **支持时长**: 5-10秒
- **角色一致性**: ✅ 支持主体参考
- **定价**: ~0.5-1元/次
- **特色**: 功能最全面，支持运动控制和多模态输入

[查看详细文档 →](./kling/README.md)

---

### 2. 通义万相 (Tongyi Wanxiang) 📁 [tongyi/](./tongyi/)

- **文档大小**: 15KB
- **Base URL**: `https://dashscope.aliyuncs.com/api/v1/`
- **认证方式**: Bearer Token
- **主要功能**:
  - ✅ 文生视频 (wanx2.1-t2v-turbo/plus)
  - ✅ 图生视频 (wanx2.1-i2v-turbo/plus)
  - ✅ 文生图 (wanx-v1)
  - ✅ 图像编辑
- **支持分辨率**: 720P, 1080P, 960x960, 1920x1080等
- **支持时长**: turbo版3-5秒，plus版3-10秒
- **角色一致性**: ⚠️ 有限支持（依赖提示词）
- **定价**:
  - 文生视频 turbo: ~0.1元/次
  - 文生视频 plus: ~0.3元/次
- **特色**: 阿里云生态集成，价格相对便宜

[查看详细文档 →](./tongyi/README.md)

---

### 3. 即梦AI (JiMeng AI) 📁 [jimeng/](./jimeng/)

- **文档大小**: 17KB
- **Base URL**: `https://visual.volcengineapi.com`
- **认证方式**: 火山引擎签名认证
- **主要功能**:
  - ✅ 文生视频 (3.0 Pro/720P/1080P)
  - ✅ 图生视频（首帧参考）
  - ✅ 多镜头叙事
  - ✅ 风格化表达
  - ✅ 动作模仿 (DreamActor M1)
  - ✅ 数字人生成 (OmniHuman)
- **支持分辨率**: 720P, 1080P, 竖屏
- **支持时长**: 标准版5秒，Pro版5-10秒
- **角色一致性**: ✅ 支持首帧参考，❌ 不支持多角色一致性
- **定价**:
  - 3.0 Pro: 1元/秒
  - 720P/1080P: ~0.6-0.8元/秒
- **特色**: 火山引擎技术，支持数字人和动作模仿

[查看详细文档 →](./jimeng/README.md)

---

### 4. 海螺视频 (Hailuo AI / MiniMax) 📁 [hailuo/](./hailuo/)

- **文档大小**: 13KB
- **Base URL**: `https://api.minimaxi.com`
- **认证方式**: Bearer Token
- **主要功能**:
  - ✅ 文生视频
  - ✅ 图生视频
  - ✅ 首尾帧生成视频
  - ✅ 主体参考生成视频
- **支持分辨率**: 720P, 1080P
- **支持时长**: 待补充
- **角色一致性**: ✅ 支持主体参考
- **速率限制**:
  - 免费用户: 5 RPM
  - 充值用户: 20 RPM
- **特色**: MiniMax大模型技术，主体参考能力强

[查看详细文档 →](./hailuo/README.md)

---

## 快速对比

| 平台 | 价格水平 | 功能丰富度 | 角色一致性 | 接入难度 | 推荐场景 |
|------|---------|-----------|-----------|---------|---------|
| **可灵** | 中等 | ⭐⭐⭐⭐⭐ | ✅ 强 | 中等 | 需要高级功能（运动控制、多模态） |
| **通义万相** | 便宜 | ⭐⭐⭐⭐ | ⚠️ 一般 | 简单 | 成本敏感、阿里云生态用户 |
| **即梦AI** | 中等 | ⭐⭐⭐⭐⭐ | ✅ 中 | 中等 | 需要数字人、动作模仿功能 |
| **海螺视频** | 待补充 | ⭐⭐⭐⭐ | ✅ 强 | 简单 | 需要强大主体参考能力 |

## 集成建议

### 1. 统一接口抽象

建议设计一个 `VideoProviderInterface`，让所有平台实现相同的接口：

```python
from abc import ABC, abstractmethod

class VideoProviderInterface(ABC):
    @abstractmethod
    def submit_task(self, prompt: str, **kwargs) -> str:
        """提交视频生成任务，返回task_id"""
        pass

    @abstractmethod
    def get_result(self, task_id: str) -> dict:
        """查询任务结果"""
        pass

    @abstractmethod
    def text_to_video(self, prompt: str, **kwargs) -> str:
        """文生视频"""
        pass

    @abstractmethod
    def image_to_video(self, image_url: str, prompt: str, **kwargs) -> str:
        """图生视频"""
        pass
```

### 2. 配置管理

使用配置文件管理所有平台的密钥和参数：

```yaml
providers:
  kling:
    enabled: true
    access_key: ${KLING_ACCESS_KEY}
    secret_key: ${KLING_SECRET_KEY}
    priority: 1
  tongyi:
    enabled: true
    api_key: ${TONGYI_API_KEY}
    priority: 2
  jimeng:
    enabled: true
    access_key: ${JIMENG_ACCESS_KEY}
    secret_key: ${JIMENG_SECRET_KEY}
    priority: 3
  hailuo:
    enabled: true
    api_key: ${HAILUO_API_KEY}
    priority: 4
```

### 3. 负载均衡策略

- **价格优先**: 优先使用价格最低的平台
- **速度优先**: 根据历史数据选择速度最快的平台
- **质量优先**: 根据用户评分选择质量最高的平台
- **降级策略**: 主平台失败时自动切换到备用平台

### 4. 成本控制

- 实现API调用配额管理
- 记录每次调用的成本
- 提供成本预估功能
- 设置预算告警

## 下一步工作

- [ ] 实现统一的Provider抽象层
- [ ] 为每个平台编写SDK封装
- [ ] 实现负载均衡和降级策略
- [ ] 添加单元测试和集成测试
- [ ] 完善错误处理和重试机制
- [ ] 实现成本统计和监控
- [ ] 补充海螺视频的定价信息

---

## 相关文档

- [项目需求文档](../REQUIREMENTS.md)
- [待办事项](../TODO.md)

---

*文档版本: 1.0*
*最后更新: 2026-01-19*
