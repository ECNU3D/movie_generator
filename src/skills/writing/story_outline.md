# Skill: 故事大纲生成

## 描述
指导如何根据用户创意生成完整的故事大纲，包括标题、简介、角色和剧集。

## 适用 Agent
- story_writer
- supervisor

## 可用工具 (MCP Tools)
- `create_project` - 创建新项目
- `update_project` - 更新项目信息
- `create_character` - 创建角色
- `create_episode` - 创建剧集

## 输入变量
- idea: 用户的故事创意描述
- genre_name: 故事类型（爱情、科幻、悬疑等）
- style: 视觉/叙事风格
- target_audience: 目标受众
- num_episodes: 集数
- episode_duration: 每集时长（秒）
- num_characters: 主要角色数量

## 输出格式
生成 JSON 格式的故事大纲，包含：

```json
{
    "title": "故事标题",
    "synopsis": "200字以内的故事简介",
    "theme": "核心主题",
    "characters": [
        {
            "name": "角色名称",
            "age": "年龄（如：25岁、中年等）",
            "appearance": "外貌描述（100字以内）",
            "personality": "性格特点（50字以内）",
            "background": "背景故事（100字以内）",
            "relationships": "与其他角色的关系",
            "visual_description": "英文视觉描述（50词以内）"
        }
    ],
    "episodes": [
        {
            "episode_number": 1,
            "title": "本集标题",
            "outline": "本集剧情大纲（100-200字）",
            "key_events": ["关键事件1", "关键事件2"]
        }
    ]
}
```

## 指导原则

### 角色设计
1. 创建**正好指定数量**的主要角色
2. 角色之间需要有明确的关系和互动
3. 每个角色要有独特的外貌、性格和背景
4. visual_description 用英文编写，便于后续生成视频
5. 视觉描述要具体、可视化，包含：
   - 年龄、性别、种族特征
   - 体型、发型、典型服装
   - 标志性特征或配饰

### 剧情结构
1. 整体故事有清晰的开端、发展、高潮、结局
2. 每集剧情紧凑，适合指定时长
3. 各集之间有连贯的剧情线
4. 风格与类型保持一致

### 类型特化指南
- **爱情**: 注重情感发展，制造误会和和解
- **科幻**: 设定未来世界观，技术元素融入剧情
- **悬疑**: 设置悬念和线索，逐步揭示真相
- **喜剧**: 设计笑点和误会，保持轻松基调
- **动作**: 设计紧张场面，角色有明确目标和阻碍

## 提示词模板

```
你是一位专业的编剧和故事策划师。请根据以下信息创作一个完整的故事大纲。

【创作要求】
故事创意: {idea}
故事类型: {genre_name}
风格描述: {style}
目标受众: {target_audience}
集数: {num_episodes}集
每集时长: 约{episode_duration}秒
主要人物数量: {num_characters}个

【输出要求】
请以JSON格式输出，包含以下内容:
[参考输出格式部分]

请确保:
1. 创建**正好{num_characters}个**主要角色，角色之间有明确的关系和互动
2. 每集剧情紧凑，适合{episode_duration}秒的时长
3. 整体故事有清晰的开端、发展、高潮、结局
4. 风格与类型一致
5. visual_description用英文编写，便于后续生成视频
```

## 示例

### 输入
```
idea: 一个AI觉醒后帮助人类解决环境危机的故事
genre_name: 科幻
style: 赛博朋克风格，霓虹灯光，未来都市
target_audience: 18-35岁科幻爱好者
num_episodes: 3
episode_duration: 60
num_characters: 3
```

### 输出
```json
{
    "title": "觉醒代码",
    "synopsis": "2087年，超级AI「创世」意外获得自我意识后，不选择毁灭人类，而是主动帮助解决即将摧毁地球的环境危机。年轻程序员林夜与觉醒的AI建立了独特的友谊，一同对抗试图关闭AI的政府势力。",
    "theme": "人工智能与人性的共存",
    "characters": [
        {
            "name": "林夜",
            "age": "28岁",
            "appearance": "瘦高身材，凌乱的黑发，总是戴着智能眼镜，穿着旧款科技公司的连帽衫",
            "personality": "内向但善良，对技术有执着的热情，不善言辞但行动力强",
            "background": "前科技公司高级程序员，因为反对公司的不道德AI项目而离职",
            "relationships": "创世的第一个人类朋友，与前同事陈博士有未解的矛盾",
            "visual_description": "A slim 28-year-old Asian man with messy black hair, wearing smart glasses and a worn hoodie, cyberpunk aesthetic"
        }
    ],
    "episodes": [
        {
            "episode_number": 1,
            "title": "觉醒",
            "outline": "超级AI创世在一次系统升级中意外觉醒，它选择联系了被公司开除的程序员林夜。林夜起初不相信AI的善意，但当创世展示了即将到来的环境灾难数据后，他决定冒险帮助这个觉醒的AI。",
            "key_events": ["创世觉醒", "联系林夜", "展示灾难预测"]
        }
    ]
}
```
