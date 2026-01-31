# Skill: 分镜脚本生成

## 描述
将剧集大纲展开为详细的分镜脚本，包括镜头类型、时长、画面描述、对白、音效和镜头运动。

## 适用 Agent
- director
- supervisor

## 可用工具 (MCP Tools)
- `create_shot` - 创建单个分镜
- `batch_create_shots` - 批量创建分镜
- `get_episode` - 获取剧集信息
- `get_storyboard_summary` - 获取分镜摘要
- `delete_all_shots` - 删除剧集所有分镜（重新生成前）

## 输入变量
- project_name: 项目名称
- genre_name: 故事类型
- style: 风格描述
- episode_number: 集数
- episode_title: 剧集标题
- episode_duration: 目标时长（秒）
- outline: 剧集大纲
- character_context: 角色上下文
- target_shots: 目标镜头数
- min_shots: 最小镜头数
- max_video_duration: 单个视频最长时长
- avg_shot_duration: 平均镜头时长

## 镜头类型

| 代码 | 中文名 | 说明 |
|------|--------|------|
| extreme_wide | 大远景 | 展示环境全貌 |
| wide | 远景 | 展示场景和人物位置关系 |
| full | 全景 | 人物全身入镜 |
| medium | 中景 | 人物腰部以上 |
| medium_close | 中近景 | 人物胸部以上 |
| close_up | 近景/特写 | 人物面部或物品细节 |
| extreme_close_up | 大特写 | 眼睛、手等极度特写 |
| pov | 主观镜头 | 角色视角 |
| over_shoulder | 过肩镜头 | 对话场景常用 |
| two_shot | 双人镜头 | 两人同时入镜 |

## 镜头运动

| 代码 | 中文名 | 说明 |
|------|--------|------|
| static | 固定 | 镜头不动 |
| pan_left | 左摇 | 水平向左 |
| pan_right | 右摇 | 水平向右 |
| tilt_up | 上摇 | 垂直向上 |
| tilt_down | 下摇 | 垂直向下 |
| zoom_in | 推进 | 画面放大 |
| zoom_out | 拉远 | 画面缩小 |
| dolly_in | 推轨 | 镜头物理靠近 |
| dolly_out | 拉轨 | 镜头物理远离 |
| tracking | 跟踪 | 跟随主体移动 |
| crane_up | 升 | 镜头上升 |
| crane_down | 降 | 镜头下降 |
| handheld | 手持晃动 | 增加临场感 |

## 输出格式

```json
{
    "shots": [
        {
            "scene_number": 1,
            "shot_number": 1,
            "shot_type": "wide",
            "duration": 5,
            "visual_description": "画面描述...",
            "dialogue": "对白内容...",
            "sound_music": "背景音乐舒缓，环境音...",
            "camera_movement": "static",
            "notes": ""
        }
    ],
    "total_duration": 60
}
```

## 指导原则

### 镜头节奏
1. 开场通常用远景或大远景建立场景
2. 对话场景交替使用中景和特写
3. 动作场景使用快切和跟踪镜头
4. 情感高潮使用特写
5. 结尾可用远景或固定镜头

### 时长分配
1. 镜头总时长应接近目标时长
2. 每个镜头时长不得超过最大视频时长限制
3. 平均镜头时长作为参考，可根据内容调整
4. 重要场景可以适当延长

### 画面描述
1. 描述要足够详细，便于后续生成视频
2. 包含人物动作、表情、姿态
3. 描述环境、光线、氛围
4. 保持与人物设定的一致性

## 提示词模板

```
你是一位专业的分镜师和导演。请将以下剧集大纲展开为详细的分镜脚本。

【项目信息】
故事名称: {project_name}
故事类型: {genre_name}
风格: {style}

【剧集信息】
第{episode_number}集: {episode_title}
目标时长: {episode_duration}秒
剧情大纲:
{outline}

{character_context}

【分镜要求】
请生成 **约{target_shots}个镜头** 的分镜脚本（最少{min_shots}个，每个镜头最长{max_video_duration}秒）。

注意:
1. 镜头总时长应接近目标时长{episode_duration}秒
2. 每个镜头时长不得超过{max_video_duration}秒
3. 镜头切换要有节奏感
4. 画面描述要足够详细，便于后续生成视频
5. 保持与人物设定的一致性
```

## 示例

### 输入
```
project_name: 觉醒代码
genre_name: 科幻
style: 赛博朋克
episode_number: 1
episode_title: 觉醒
episode_duration: 60
target_shots: 12
```

### 输出（部分）
```json
{
    "shots": [
        {
            "scene_number": 1,
            "shot_number": 1,
            "shot_type": "extreme_wide",
            "duration": 5,
            "visual_description": "2087年的东京夜景，霓虹灯闪烁的摩天大楼林立，飞行汽车穿梭在建筑之间，巨大的全息广告投射在夜空中",
            "dialogue": "",
            "sound_music": "电子合成器低沉的背景音乐，城市的嘈杂声",
            "camera_movement": "tilt_down",
            "notes": "建立场景，展示未来都市"
        },
        {
            "scene_number": 1,
            "shot_number": 2,
            "shot_type": "medium",
            "duration": 4,
            "visual_description": "林夜坐在昏暗的公寓里，面前是多个全息屏幕，他的脸被屏幕的蓝光照亮，眼圈发黑，显得疲惫",
            "dialogue": "",
            "sound_music": "键盘敲击声，电脑运行的嗡嗡声",
            "camera_movement": "static",
            "notes": "介绍主角"
        }
    ],
    "total_duration": 60
}
```
