# Skill: 角色设计

## 描述
根据故事大纲设计主要角色，包括外貌、性格、背景和角色关系。

## 适用 Agent
- story_writer
- character_designer

## 可用工具 (MCP Tools)
- `create_character` - 创建角色
- `update_character` - 更新角色信息
- `get_character` - 获取角色信息

## 输入变量
- story_summary: 故事大纲摘要
- num_characters: 需要设计的角色数量
- genre: 故事类型

## 输出格式

请以JSON格式输出角色列表:

```json
{
    "characters": [
        {
            "name": "角色姓名",
            "age": "年龄或年龄段",
            "appearance": "外貌描述（100字以内）",
            "personality": "性格特点（50字以内）",
            "background": "背景故事（100字以内）",
            "role": "在故事中的角色定位（主角/配角/反派等）",
            "visual_description": "用于AI视频生成的英文外貌描述"
        }
    ]
}
```

## 指导原则

### 角色设计要点
1. **名字**: 符合故事背景和文化设定
2. **外貌**: 具体可视化的描述，便于AI生成
3. **性格**: 鲜明的性格特点，有成长空间
4. **背景**: 与故事主题相关的经历
5. **关系**: 角色之间要有明确的关系和冲突

### 角色搭配原则
1. 主角需要明确的目标和动机
2. 配角应辅助或阻碍主角
3. 反派需要合理的动机
4. 角色间应有张力和互动

### visual_description 要求
- 使用英文，便于AI视频生成
- 包含：年龄特征、发型发色、服装风格、体型特征
- 例如: "Young Asian woman in her 20s, long black hair, wearing a white lab coat, slim build, determined expression"

## 提示词模板

```
请根据以下故事大纲设计{num_characters}个主要角色。

【故事大纲】
{story_summary}

【故事类型】
{genre}

【设计要求】
1. 每个角色需要有独特的外貌、性格和背景
2. 角色之间应有明确的关系
3. 角色设定应符合{genre}类型的特点
4. 为每个角色提供用于AI视频生成的英文外貌描述

请以JSON格式输出：
{
    "characters": [
        {
            "name": "角色姓名",
            "age": "年龄",
            "appearance": "外貌描述",
            "personality": "性格特点",
            "background": "背景故事",
            "role": "角色定位",
            "visual_description": "英文外貌描述"
        }
    ]
}

只输出JSON，不要有其他内容。
```

## 示例

### 输入
```
story_summary:
标题: 钢铁黎明
主题: 人类与外星虫族的生存之战
背景: 近未来地球遭遇外星入侵，人类研发机甲对抗

num_characters: 3
genre: 科幻
```

### 输出
```json
{
    "characters": [
        {
            "name": "林战",
            "age": "28岁",
            "appearance": "身材高大健壮，短发利落，脸上有一道战斗留下的伤疤，眼神坚毅",
            "personality": "沉默寡言但意志坚定，重视战友，有牺牲精神",
            "background": "前特种兵，家人死于虫族第一波入侵，加入机甲部队复仇",
            "role": "主角/机甲驾驶员",
            "visual_description": "Tall muscular Asian man, 28 years old, short black hair, scar on left cheek, wearing dark military uniform, determined gaze"
        },
        {
            "name": "苏晴",
            "age": "32岁",
            "appearance": "知性优雅，戴着细框眼镜，总是穿着白色研究服，举止沉稳",
            "personality": "冷静理性，专注科研，但内心充满对人类命运的担忧",
            "background": "天才机甲工程师，机甲项目首席科学家",
            "role": "配角/科学家",
            "visual_description": "Asian woman in her early 30s, elegant appearance, thin-framed glasses, wearing white lab coat, calm and intelligent expression"
        },
        {
            "name": "陈铁军",
            "age": "45岁",
            "appearance": "身材魁梧，满脸络腮胡，军装笔挺，气势威严",
            "personality": "铁血军人，纪律严明，但对下属如父",
            "background": "机甲部队指挥官，身经百战的老兵",
            "role": "配角/指挥官",
            "visual_description": "Middle-aged Asian man, 45 years old, muscular build, full beard, wearing military commander uniform with medals, authoritative presence"
        }
    ]
}
```
