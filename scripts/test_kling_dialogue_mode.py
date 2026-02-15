#!/usr/bin/env python3
"""
Test script for Kling 3.0 Dialogue Mode

Tests:
1. Generate storyboard with dialogue
2. Generate single-shot dialogue prompt
3. Generate multi-shot dialogue prompt

All results saved to output/kling_dialogue_test/
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "output" / "kling_dialogue_test"


def init_gemini_client():
    """Initialize Gemini client"""
    from src.story_generator.gemini_client import GeminiClient, GeminiConfig

    # Try to get API key
    api_key = None

    # From file
    key_file = PROJECT_ROOT / "gemini_api_key"
    if key_file.exists():
        api_key = key_file.read_text().strip()

    # From environment
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("Error: No Gemini API key found")
        print("Please create 'gemini_api_key' file or set GEMINI_API_KEY environment variable")
        return None

    config = GeminiConfig(api_key=api_key)
    return GeminiClient(config)


def create_test_project():
    """Create a test project with characters"""
    from src.story_generator.models import Project, Character, Episode, Shot

    # Create project
    project = Project(
        id=1,
        name="咖啡馆的邂逅",
        description="一个关于两个年轻人在咖啡馆偶遇并产生情感的温馨故事",
        genre="romance",
        style="温馨治愈、电影感、柔和暖色调",
        target_audience="年轻人",
        num_episodes=1,
        episode_duration=30,
        max_video_duration=15
    )

    # Create characters
    char1 = Character(
        id=1,
        project_id=1,
        name="小明",
        age="25岁",
        appearance="身高178cm，短发，戴黑框眼镜，穿休闲衬衫",
        personality="内向但善良，喜欢阅读，有点害羞",
        background="在科技公司工作的程序员，独自来到城市打拼",
        relationships="与小红互相有好感",
        visual_description="Young Asian man, 25, short black hair, black-rimmed glasses, casual shirt, gentle smile"
    )

    char2 = Character(
        id=2,
        project_id=1,
        name="小红",
        age="23岁",
        appearance="身高165cm，长发，穿白色连衣裙，气质优雅",
        personality="开朗活泼，喜欢咖啡和艺术，善于交流",
        background="咖啡馆的兼职店员，同时是美术专业的学生",
        relationships="与小明互相有好感",
        visual_description="Young Asian woman, 23, long black hair, white dress, elegant temperament, warm smile"
    )

    project.characters = [char1, char2]

    # Create episode
    episode = Episode(
        id=1,
        project_id=1,
        episode_number=1,
        title="雨天的相遇",
        outline="在一个下雨的午后，小明独自来到咖啡馆躲雨。小红是这家咖啡馆的店员，她热情地招待了小明。两人因为一本书产生了交流，发现彼此有很多共同话题。雨停后，小明离开前，两人交换了联系方式。",
        duration=30,
        status="draft"
    )

    # Create shots with dialogue
    shots = [
        Shot(
            id=1,
            episode_id=1,
            scene_number=1,
            shot_number=1,
            shot_type="wide",
            duration=3,
            visual_description="下雨的午后，街道上行人稀少。小明撑着伞快步走进一家温馨的咖啡馆。",
            dialogue="",
            sound_music="雨声，咖啡馆门铃声",
            camera_movement="tracking",
            notes=""
        ),
        Shot(
            id=2,
            episode_id=1,
            scene_number=1,
            shot_number=2,
            shot_type="medium",
            duration=4,
            visual_description="咖啡馆内，暖黄的灯光，小红站在吧台后面，看到小明进来，微笑着打招呼。",
            dialogue="欢迎光临，今天雨好大呢。",
            sound_music="轻柔的爵士乐",
            camera_movement="static",
            notes="小红的台词"
        ),
        Shot(
            id=3,
            episode_id=1,
            scene_number=1,
            shot_number=3,
            shot_type="medium_close",
            duration=3,
            visual_description="小明收起雨伞，看向小红，有些害羞地回应。",
            dialogue="是啊，来杯热拿铁吧。",
            sound_music="咖啡机声音",
            camera_movement="static",
            notes="小明的台词"
        ),
        Shot(
            id=4,
            episode_id=1,
            scene_number=2,
            shot_number=1,
            shot_type="medium",
            duration=5,
            visual_description="小明坐在靠窗的位置，手里拿着一本书。小红端着咖啡走过来，注意到书的封面。",
            dialogue="《小王子》？这是我最喜欢的书！",
            sound_music="轻柔背景音乐",
            camera_movement="dolly_in",
            notes="小红惊喜地说"
        ),
        Shot(
            id=5,
            episode_id=1,
            scene_number=2,
            shot_number=2,
            shot_type="two_shot",
            duration=4,
            visual_description="两人面对面，小明惊讶地抬头，眼神中带着欣喜。",
            dialogue="真的吗？我也很喜欢这本书。",
            sound_music="温暖的弦乐",
            camera_movement="static",
            notes="两人对视微笑"
        ),
        Shot(
            id=6,
            episode_id=1,
            scene_number=3,
            shot_number=1,
            shot_type="wide",
            duration=3,
            visual_description="窗外雨停了，阳光透过云层照进来。小明起身准备离开。",
            dialogue="雨停了，我该走了。",
            sound_music="雨后鸟鸣",
            camera_movement="crane_up",
            notes=""
        ),
        Shot(
            id=7,
            episode_id=1,
            scene_number=3,
            shot_number=2,
            shot_type="close_up",
            duration=4,
            visual_description="小红递给小明一张名片，两人的手指轻轻触碰。",
            dialogue="这是我的联系方式，有空可以一起聊聊书。",
            sound_music="温暖的钢琴",
            camera_movement="static",
            notes="小红微笑着说"
        ),
        Shot(
            id=8,
            episode_id=1,
            scene_number=3,
            shot_number=3,
            shot_type="medium",
            duration=4,
            visual_description="小明接过名片，脸上露出温暖的笑容，点头答应。",
            dialogue="一定会的。",
            sound_music="温馨的结尾音乐",
            camera_movement="zoom_out",
            notes="两人相视而笑"
        ),
    ]

    episode.shots = shots
    project.episodes = [episode]

    return project


def test_single_shot_dialogue_prompt(gemini, project, shot):
    """Test 1: Generate single shot dialogue prompt"""
    print("\n" + "=" * 60)
    print("Test 1: Single Shot Dialogue Prompt")
    print("=" * 60)

    character_context = project.get_all_characters_context()

    print(f"Shot: Scene {shot.scene_number} - Shot {shot.shot_number}")
    print(f"Dialogue: {shot.dialogue}")
    print("Generating dialogue mode prompt...")

    prompt = gemini.generate_video_prompt(
        shot=shot,
        platform="kling",
        character_context=character_context,
        style=project.style,
        prompt_type="t2v",
        dialogue_mode=True
    )

    print("\n--- Generated Prompt ---")
    print(prompt)

    return prompt


def test_multishot_dialogue_prompt(gemini, project, shots):
    """Test 2: Generate multi-shot dialogue prompt"""
    print("\n" + "=" * 60)
    print("Test 2: Multi-Shot Dialogue Prompt")
    print("=" * 60)

    character_context = project.get_all_characters_context()

    print(f"Shots: {len(shots)} shots")
    total_duration = sum(s.duration for s in shots)
    print(f"Total duration: {total_duration}s")
    print("Generating multi-shot dialogue prompt...")

    prompt = gemini.generate_multishot_dialogue_prompt(
        shots=shots,
        character_context=character_context,
        style=project.style,
        max_duration=15
    )

    print("\n--- Generated Multi-Shot Prompt ---")
    print(prompt)

    return prompt


def test_standard_vs_dialogue_comparison(gemini, project, shot):
    """Test 3: Compare standard vs dialogue mode prompts"""
    print("\n" + "=" * 60)
    print("Test 3: Standard vs Dialogue Mode Comparison")
    print("=" * 60)

    character_context = project.get_all_characters_context()

    print(f"Shot: Scene {shot.scene_number} - Shot {shot.shot_number}")
    print(f"Dialogue: {shot.dialogue}")

    # Standard mode
    print("\nGenerating standard T2V prompt...")
    standard_prompt = gemini.generate_video_prompt(
        shot=shot,
        platform="kling",
        character_context=character_context,
        style=project.style,
        prompt_type="t2v",
        dialogue_mode=False
    )

    # Dialogue mode
    print("Generating dialogue mode prompt...")
    dialogue_prompt = gemini.generate_video_prompt(
        shot=shot,
        platform="kling",
        character_context=character_context,
        style=project.style,
        prompt_type="t2v",
        dialogue_mode=True
    )

    return {
        "standard": standard_prompt,
        "dialogue": dialogue_prompt
    }


def save_results(results: dict, filename: str):
    """Save results to file"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(results["content"])

    print(f"Saved to: {filepath}")
    return filepath


def main():
    print("\n" + "=" * 60)
    print("Kling 3.0 Dialogue Mode Test Suite")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")

    # Initialize
    gemini = init_gemini_client()
    if not gemini:
        return

    # Create test project
    print("\nCreating test project...")
    project = create_test_project()
    print(f"Project: {project.name}")
    print(f"Characters: {', '.join([c.name for c in project.characters])}")
    print(f"Shots: {len(project.episodes[0].shots)}")

    # Results storage
    all_results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Test 1: Single shot with dialogue
    shot_with_dialogue = project.episodes[0].shots[3]  # "《小王子》？这是我最喜欢的书！"
    single_prompt = test_single_shot_dialogue_prompt(gemini, project, shot_with_dialogue)
    all_results.append({
        "test": "Single Shot Dialogue",
        "prompt": single_prompt
    })

    # Test 2: Multi-shot dialogue (first 4 shots)
    first_shots = project.episodes[0].shots[:4]
    multi_prompt = test_multishot_dialogue_prompt(gemini, project, first_shots)
    all_results.append({
        "test": "Multi-Shot Dialogue (Shots 1-4)",
        "prompt": multi_prompt
    })

    # Test 3: Comparison
    comparison = test_standard_vs_dialogue_comparison(gemini, project, shot_with_dialogue)
    all_results.append({
        "test": "Standard vs Dialogue Comparison",
        "standard_prompt": comparison["standard"],
        "dialogue_prompt": comparison["dialogue"]
    })

    # Test 4: Full episode multi-shot (all 8 shots, will be split due to 15s limit)
    print("\n" + "=" * 60)
    print("Test 4: Full Episode Multi-Shot Prompt")
    print("=" * 60)

    all_shots = project.episodes[0].shots
    full_prompt = test_multishot_dialogue_prompt(gemini, project, all_shots)
    all_results.append({
        "test": "Full Episode (All Shots)",
        "prompt": full_prompt
    })

    # Save all results to markdown file
    md_content = f"""# 可灵 3.0 对白模式测试结果

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 项目信息

- **项目名称**: {project.name}
- **风格**: {project.style}
- **角色**: {', '.join([c.name for c in project.characters])}

## 人物设定

"""

    for char in project.characters:
        md_content += f"""### {char.name}

- **年龄**: {char.age}
- **外貌**: {char.appearance}
- **性格**: {char.personality}
- **视觉描述**: {char.visual_description}

"""

    md_content += """## 分镜脚本

| 场景 | 镜头 | 时长 | 画面 | 对白 |
|------|------|------|------|------|
"""

    for shot in project.episodes[0].shots:
        dialogue = shot.dialogue.replace("|", "\\|") if shot.dialogue else "-"
        desc = shot.visual_description[:50] + "..." if len(shot.visual_description) > 50 else shot.visual_description
        md_content += f"| {shot.scene_number} | {shot.shot_number} | {shot.duration}s | {desc} | {dialogue} |\n"

    md_content += "\n## 测试结果\n\n"

    for result in all_results:
        md_content += f"### {result['test']}\n\n"
        if "prompt" in result:
            md_content += f"```\n{result['prompt']}\n```\n\n"
        if "standard_prompt" in result:
            md_content += f"**标准模式:**\n```\n{result['standard_prompt']}\n```\n\n"
            md_content += f"**对白模式:**\n```\n{result['dialogue_prompt']}\n```\n\n"

    md_content += """## 使用说明

### 可灵 3.0 对白模式格式

```
镜头1，3s，中景，咖啡厅内，@小明 坐在窗边，@小明 说，"对白内容"
镜头2，2s，特写，@小红 端着咖啡走过来，她说，"对白内容"
镜头3，3s，切远景，两人对视微笑。
```

### 注意事项

1. 使用 `@角色名` 引用主体（需在可灵中创建对应主体）
2. 对白使用中文双引号 `""`
3. 说/问 后加逗号
4. 单次生成最长 15 秒
5. 支持音画同步，角色说话时嘴型自动同步
"""

    # Save markdown file
    save_results({"content": md_content}, f"dialogue_test_{timestamp}.md")

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Tests completed: {len(all_results)}")
    print(f"  Output saved to: {OUTPUT_DIR}")
    print(f"  Main result file: dialogue_test_{timestamp}.md")

    print("\n  All tests completed successfully!")


if __name__ == "__main__":
    main()
