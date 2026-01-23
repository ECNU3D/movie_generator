#!/usr/bin/env python3
"""
测试故事生成器核心功能
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.story_generator import (
    Database,
    GeminiClient,
    GeminiConfig,
    Project,
    Character,
    Episode,
    Shot,
    MajorEvent,
    SHOT_TYPE_NAMES,
    CAMERA_MOVEMENT_NAMES,
    GENRE_NAMES,
)
from datetime import datetime
import json

# 读取 Gemini API Key
def load_api_key():
    key_file = os.path.join(os.path.dirname(__file__), "gemini_api_key")
    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            return f.read().strip()
    return os.getenv("GEMINI_API_KEY", "")

def test_database():
    """测试数据库操作"""
    print("=" * 50)
    print("测试数据库操作")
    print("=" * 50)

    db = Database(":memory:")  # 使用内存数据库测试

    # 创建项目
    project = Project(
        id=None,
        name="测试项目",
        description="这是一个测试项目",
        genre="drama",
        style="现实主义",
        target_audience="成年观众",
        num_episodes=5,
        episode_duration=180,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    project_id = db.create_project(project)
    print(f"✓ 创建项目成功，ID: {project_id}")

    # 读取项目
    loaded_project = db.get_project(project_id)
    assert loaded_project is not None
    assert loaded_project.name == "测试项目"
    print(f"✓ 读取项目成功: {loaded_project.name}")

    # 创建角色
    character = Character(
        id=None,
        project_id=project_id,
        name="张三",
        age="30岁",
        appearance="高个子、戴眼镜的男性程序员",
        personality="内向、善良",
        background="从小在农村长大，后来成为程序员",
        relationships="李四的好友",
        visual_description="A tall young man with glasses wearing casual clothes",
        major_events=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    character_id = db.create_character(character)
    print(f"✓ 创建角色成功，ID: {character_id}")

    # 添加重大事件
    character.id = character_id
    character.major_events = [
        MajorEvent(
            episode_number=1,
            description="遭遇车祸",
            impact="行动不便，需要康复",
            timestamp=datetime.now()
        )
    ]
    db.update_character(character)

    # 验证重大事件
    updated_character = db.get_character(character_id)
    assert len(updated_character.major_events) == 1
    assert updated_character.major_events[0].description == "遭遇车祸"
    print(f"✓ 角色重大事件更新成功")

    # 测试知识库上下文
    context = updated_character.get_knowledge_context(up_to_episode=2)
    assert "遭遇车祸" in context
    print(f"✓ 知识库上下文生成成功")

    # 创建剧集
    episode = Episode(
        id=None,
        project_id=project_id,
        episode_number=1,
        title="开端",
        outline="故事的开始，主角张三遇到了人生的转折点...",
        duration=60,
        status="outline",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    episode_id = db.create_episode(episode)
    print(f"✓ 创建剧集成功，ID: {episode_id}")

    # 创建分镜
    shot = Shot(
        id=None,
        episode_id=episode_id,
        scene_number=1,
        shot_number=1,
        shot_type="wide",
        duration=5,
        visual_description="城市街道的全景",
        dialogue="",
        sound_music="城市背景音",
        camera_movement="pan_left",
        notes="开场镜头",
        generated_prompts={},
    )
    shot_id = db.create_shot(shot)
    print(f"✓ 创建分镜成功，ID: {shot_id}")

    # 更新分镜提示词
    shot.id = shot_id
    shot.generated_prompts = {
        "kling": "A wide shot of a busy city street...",
        "hailuo": "[左摇] 城市街道全景..."
    }
    db.update_shot(shot)

    # 验证提示词
    updated_shot = db.get_shot(shot_id)
    assert "kling" in updated_shot.generated_prompts
    assert "hailuo" in updated_shot.generated_prompts
    print(f"✓ 分镜提示词更新成功")

    print("\n数据库测试全部通过！")
    return True


def test_gemini_api():
    """测试 Gemini API"""
    print("\n" + "=" * 50)
    print("测试 Gemini API")
    print("=" * 50)

    api_key = load_api_key()
    if not api_key:
        print("⚠ 未找到 Gemini API Key，跳过 API 测试")
        return False

    config = GeminiConfig(api_key=api_key)
    client = GeminiClient(config)

    # 测试随机创意生成
    print("\n测试随机创意生成...")
    idea = client.generate_random_story_idea("comedy", "轻松幽默")
    print(f"✓ 随机创意: {idea[:100]}...")

    # 测试故事大纲生成
    print("\n测试故事大纲生成...")
    outline = client.generate_story_outline(
        idea="一个程序员发现自己编写的AI获得了自我意识",
        genre="sci-fi",
        style="赛博朋克",
        num_episodes=3,
        episode_duration=120,
        target_audience="科技爱好者"
    )

    print(f"✓ 故事标题: {outline.get('title', 'N/A')}")
    print(f"✓ 角色数量: {len(outline.get('characters', []))}")
    print(f"✓ 剧集数量: {len(outline.get('episodes', []))}")

    # 测试分镜生成
    if outline.get('episodes'):
        print("\n测试分镜脚本生成...")

        # 创建测试用的Episode对象
        test_episode = Episode(
            id=1,
            project_id=1,
            episode_number=1,
            title=outline['episodes'][0].get('title', '第一集'),
            outline=outline['episodes'][0].get('outline', '测试大纲'),
            duration=120,
            status="outline",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # 创建测试用的Project对象
        test_project = Project(
            id=1,
            name=outline.get('title', '测试项目'),
            description=outline.get('synopsis', ''),
            genre="sci-fi",
            style="赛博朋克",
            target_audience="科技爱好者",
            num_episodes=3,
            episode_duration=120,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # 生成角色上下文
        character_context = ""
        if outline.get('characters'):
            for char in outline['characters'][:2]:  # 只用前两个角色测试
                character_context += f"【{char.get('name', '未命名')}】{char.get('personality', '')}\n"

        storyboard = client.generate_storyboard(
            episode=test_episode,
            project=test_project,
            character_context=character_context
        )

        print(f"✓ 生成分镜数量: {len(storyboard)}")

        if storyboard:
            first_shot = storyboard[0]
            print(f"  - 第一个分镜: 场景{first_shot.get('scene_number', 'N/A')}, "
                  f"镜号{first_shot.get('shot_number', 'N/A')}, "
                  f"时长{first_shot.get('duration', 'N/A')}秒")

            # 测试视频提示词生成
            print("\n测试视频提示词生成...")

            test_shot = Shot(
                id=1,
                episode_id=1,
                scene_number=first_shot.get('scene_number', 1),
                shot_number=first_shot.get('shot_number', 1),
                shot_type="wide",
                duration=first_shot.get('duration', 5),
                visual_description=first_shot.get('visual_description', '测试画面'),
                dialogue=first_shot.get('dialogue', ''),
                sound_music=first_shot.get('sound_music', ''),
                camera_movement="static",
                notes="",
                generated_prompts={},
            )

            for platform in ["kling", "tongyi", "jimeng", "hailuo"]:
                prompt = client.generate_video_prompt(
                    shot=test_shot,
                    platform=platform,
                    character_context=character_context,
                    style="赛博朋克",
                    prompt_type="text_to_video"
                )
                print(f"✓ {platform} 提示词: {prompt[:80]}...")

    print("\nGemini API 测试全部通过！")
    return True


def main():
    print("\n🎬 故事生成器测试开始\n")

    db_ok = test_database()
    api_ok = test_gemini_api()

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"数据库测试: {'✓ 通过' if db_ok else '✗ 失败'}")
    print(f"Gemini API测试: {'✓ 通过' if api_ok else '⚠ 跳过/失败'}")
    print()


if __name__ == "__main__":
    main()
