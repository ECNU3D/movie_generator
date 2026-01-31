# Skill: 一致性检查与修复

## 描述
检查和修复故事内容的一致性问题，包括剧情逻辑、角色行为、时间线等方面。

## 适用 Agent
- story_writer
- supervisor

## 可用工具 (MCP Tools)
- `get_project` - 获取项目信息
- `get_episode` - 获取剧集信息
- `update_episode` - 更新剧集
- `get_character` - 获取角色信息
- `update_character` - 更新角色
- `get_character_context` - 获取角色上下文

## 输入变量
- project_name: 项目名称
- genre_name: 故事类型
- style: 风格描述
- timeline: 剧情时间线
- character_timelines: 角色经历时间线

## 检查范围

### 1. 剧情逻辑
- 前后剧集的因果关系是否合理
- 事件发展是否符合逻辑
- 是否有未解释的剧情跳跃

### 2. 角色行为
- 角色的行为是否符合其设定
- 性格表现是否一致
- 动机是否合理

### 3. 时间线
- 事件发生的顺序是否合理
- 时间跨度是否合理
- 是否有时间冲突

### 4. 细节一致
- 场景描述是否前后一致
- 物品/道具是否一致
- 人物关系是否一致

## 输出格式

```json
{
    "issues": [
        {
            "type": "episode 或 character",
            "id": "相关ID",
            "name": "名称",
            "issue": "问题描述",
            "severity": "warning 或 error",
            "suggested_fix": "建议的修复方案",
            "auto_fixable": true 或 false
        }
    ],
    "overall_assessment": "整体一致性评估（好/一般/需要改进）"
}
```

### 严重程度定义
- **error**: 严重矛盾，必须修复，影响故事理解
- **warning**: 建议修复，但不影响故事核心理解

### auto_fixable 判断标准
- **true**: 问题是简单的事实性错误，可以通过添加/修改少量细节来修复
- **false**: 问题涉及叙事结构、角色核心设定，需要创意性重写

## 提示词模板

### 全局一致性检查

```
你是一位专业的剧本审核专家。请全面检查以下故事的一致性问题。

【项目信息】
故事名称: {project_name}
类型: {genre_name}
风格: {style}

【剧情时间线】
{timeline}

【角色经历时间线】
{character_timelines}

请检查以下方面的一致性问题:
1. 剧情逻辑：前后剧集的因果关系是否合理
2. 角色行为：角色的行为是否符合其设定
3. 时间线：事件发生的顺序是否合理
4. 细节一致：场景、物品、关系等细节是否前后一致

以JSON格式输出所有发现的问题。
如果没有发现问题，返回空的issues数组。只报告真正的问题，不要过度解读。
```

### 编辑影响分析

```
你是一位专业的剧本顾问。请分析以下剧集大纲的修改对其他内容的影响。

【被修改的剧集】
第{episode_number}集 - {episode_title}

【原大纲】
{original_outline}

【新大纲】
{new_outline}

【其他剧集】
{other_episodes_context}

【角色设定】
{characters_context}

请分析这次修改是否会导致以下问题:
1. 与前面剧集的剧情矛盾
2. 与后面剧集的剧情不连贯
3. 与角色设定或经历的矛盾
4. 时间线问题

以JSON格式输出所有发现的问题。
```

## 示例

### 输入（发现问题的情况）
检查一个故事，发现第2集中角色A被描述为"第一次见到角色B"，但第1集中他们已经相遇过。

### 输出
```json
{
    "issues": [
        {
            "type": "episode",
            "id": 2,
            "name": "第2集 - 重逢",
            "issue": "角色A与角色B被描述为'第一次见面'，但他们在第1集已经相遇过",
            "severity": "error",
            "suggested_fix": "将'第一次见面'改为'再次相遇'或'意外重逢'",
            "auto_fixable": true
        }
    ],
    "overall_assessment": "需要改进"
}
```
