#!/usr/bin/env python3
"""
Comprehensive Test Suite for JiMeng (即梦/Seedream) Image Provider

Tests:
Part 1: Basic Functions
  1.1 Connection test
  1.2 Text-to-Image (basic)
  1.3 Text-to-Image (multi-image n=2)

Part 2: Character Views
  2.1 Character front view generation
  2.2 Character three views (separate images)
  2.3 Character sheet (single image)
  2.4 Character turnaround

Part 3: Frame Generation
  3.1 Basic frame generation
  3.2 Frame with character reference

Part 4: Image Editing
  4.1 Single image editing (style transfer)
  4.2 Multi-image fusion (2 images)

Part 5: Scene Composition (JiMeng supports up to 14 characters!)
  5.1 Single character in scene
  5.2 Two characters interacting
  5.3 Three characters in scene
  5.4 Five characters in scene (JiMeng advantage)
  5.5 Angle consistency test

All generated images are saved to output/jimeng_comprehensive_test/
Using Seedream 4.5 model (doubao-seedream-4-5-251128)
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.providers.image import (
    JiMengImageProvider,
    JIMENG_IMAGE_MODELS,
    CharacterViewMode,
    CharacterRef,
    ImageTaskStatus,
)

OUTPUT_DIR = PROJECT_ROOT / "output" / "jimeng_comprehensive_test"
MODEL = "doubao-seedream-4-5-251128"


def print_header(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def save_images(provider, task, prefix: str) -> list:
    """Download and save task images. Returns list of saved paths."""
    if not task.is_successful():
        return []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = provider.download_task_images(task, save_dir=str(OUTPUT_DIR), prefix=prefix)
    for p in paths:
        print(f"    Saved: {Path(p).name}")
    return paths


# =============================================================================
# Part 1: Basic Functions
# =============================================================================

def test_connection(provider) -> bool:
    """Test 1.1: Provider connection."""
    print_header("Test 1.1: Provider Connection")

    result = provider.test_connection()
    if result["success"]:
        print(f"  API key: {result.get('api_key_preview', 'N/A')}")
        print(f"  Models: {result.get('supported_models', [])}")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {result.get('error')}")
        print("  Result: FAIL")
        return False


def test_text_to_image_basic(provider) -> str:
    """Test 1.2: Text-to-Image basic."""
    print_header("Test 1.2: Text-to-Image (Basic)")

    prompt = "一只可爱的橘猫躺在阳光下的窗台上，窗外是蓝天白云"
    print(f"  Prompt: {prompt}")
    print(f"  Model: {MODEL}")
    print("  Generating...")

    task = provider.text_to_image(
        prompt=prompt,
        size="2K",
        n=1,
        model=MODEL,
    )

    if task.is_successful():
        save_images(provider, task, "1_2_t2i_basic")
        print("  Result: PASS")
        return task.image_urls[0] if task.image_urls else None
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return None


def test_text_to_image_multi(provider) -> bool:
    """Test 1.3: Text-to-Image multi-image."""
    print_header("Test 1.3: Text-to-Image (Multi-Image n=2)")

    prompt = "一位身穿汉服的年轻女子，站在古风建筑前，背景是飘落的桃花"
    print(f"  Prompt: {prompt}")
    print(f"  n: 2 (sequential generation)")
    print("  Generating...")

    task = provider.text_to_image(
        prompt=prompt,
        size="2K",
        n=2,
        model=MODEL,
    )

    if task.is_successful():
        print(f"  Generated {len(task.image_urls)} images")
        save_images(provider, task, "1_3_t2i_multi")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


# =============================================================================
# Part 2: Character Views
# =============================================================================

def test_character_front_view(provider) -> str:
    """Test 2.1: Character front view generation."""
    print_header("Test 2.1: Character Front View")

    description = (
        "一位22岁的亚洲女性，长黑色直发，刘海，"
        "大眼睛，精致的五官，穿着浅蓝色连衣裙，"
        "气质清新甜美，面带微笑"
    )
    print(f"  Character: {description}")
    print("  Generating front view...")

    task = provider.generate_character_front_view(
        character_description=description,
        style="realistic",
        size="2K",
    )

    if task.is_successful():
        save_images(provider, task, "2_1_char_front")
        print("  Result: PASS")
        return task.image_urls[0] if task.image_urls else None
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return None


def test_character_three_views(provider, front_url: str) -> bool:
    """Test 2.2: Character three views (separate images)."""
    print_header("Test 2.2: Character Three Views (Separate Images)")

    if not front_url:
        print("  Skipped: No front view URL")
        return False

    description = "保持与正面图完全一致的角色外貌、服装和比例"
    print("  Mode: THREE_SEPARATE_IMAGES")
    print("  Generating side, front, back views...")

    task = provider.generate_character_three_views(
        character_reference=front_url,
        character_description=description,
        style="realistic",
        size="2K",
    )

    if task.is_successful():
        print(f"  Generated {len(task.image_urls)} images")
        save_images(provider, task, "2_2_char_three_views")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_character_sheet(provider, front_url: str) -> bool:
    """Test 2.3: Character sheet (single image with three views)."""
    print_header("Test 2.3: Character Sheet (Single Image)")

    if not front_url:
        print("  Skipped: No front view URL")
        return False

    description = "角色三视图参考，保持完全一致的外貌和服装"
    print("  Mode: SINGLE_IMAGE_THREE_VIEWS")
    print("  Generating character sheet...")

    task = provider.generate_character_sheet(
        character_reference=front_url,
        character_description=description,
        style="realistic",
        size="2560x1440",
    )

    if task.is_successful():
        save_images(provider, task, "2_3_char_sheet")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_character_turnaround(provider, front_url: str) -> bool:
    """Test 2.4: Character turnaround sheet."""
    print_header("Test 2.4: Character Turnaround Sheet")

    if not front_url:
        print("  Skipped: No front view URL")
        return False

    description = "专业游戏角色设定图，包含多角度视图"
    print("  Mode: TURNAROUND_SHEET")
    print("  Generating turnaround sheet...")

    task = provider.generate_character_turnaround(
        character_reference=front_url,
        character_description=description,
        style="realistic",
        size="2560x1440",
    )

    if task.is_successful():
        save_images(provider, task, "2_4_char_turnaround")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


# =============================================================================
# Part 3: Frame Generation
# =============================================================================

def test_frame_generation(provider) -> str:
    """Test 3.1: Basic frame generation."""
    print_header("Test 3.1: Frame Generation (Basic)")

    prompt = "一位年轻女子站在樱花树下，微风吹过，粉色花瓣在空中飘落，柔和的春日阳光，电影画面"
    print(f"  Scene: {prompt}")
    print("  Generating frame...")

    task = provider.generate_frame(
        prompt=prompt,
        size="2560x1440",
        style="cinematic",
    )

    if task.is_successful():
        save_images(provider, task, "3_1_frame_basic")
        print("  Result: PASS")
        return task.image_urls[0] if task.image_urls else None
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return None


def test_frame_with_character(provider, char_url: str) -> bool:
    """Test 3.2: Frame with character reference."""
    print_header("Test 3.2: Frame with Character Reference")

    if not char_url:
        print("  Skipped: No character URL")
        return False

    prompt = "角色站在海边，夕阳西下，金色光芒洒在海面上"
    print(f"  Scene: {prompt}")
    print("  Generating frame with character...")

    task = provider.generate_frame_with_character(
        prompt=prompt,
        character_reference=char_url,
        size="2560x1440",
        style="cinematic",
    )

    if task.is_successful():
        save_images(provider, task, "3_2_frame_with_char")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


# =============================================================================
# Part 4: Image Editing
# =============================================================================

def test_image_editing_style(provider, ref_url: str) -> bool:
    """Test 4.1: Single image editing (style transfer)."""
    print_header("Test 4.1: Image Editing (Style Transfer)")

    if not ref_url:
        print("  Skipped: No reference URL")
        return False

    prompt = "将这张图片转换为水彩画风格，保持主体不变，增加艺术感"
    print(f"  Prompt: {prompt}")
    print("  Editing...")

    task = provider.edit_image(
        images=[ref_url],
        prompt=prompt,
        model=MODEL,
    )

    if task.is_successful():
        save_images(provider, task, "4_1_edit_style")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_image_editing_fusion(provider, char_url: str, frame_url: str) -> bool:
    """Test 4.2: Multi-image fusion."""
    print_header("Test 4.2: Image Editing (Multi-Image Fusion)")

    if not char_url or not frame_url:
        print("  Skipped: Missing reference URLs")
        return False

    prompt = "把图1中的人物放到图2的场景中，保持人物外貌不变，自然融入场景"
    print(f"  Prompt: {prompt}")
    print("  Fusing images...")

    task = provider.edit_image(
        images=[char_url, frame_url],
        prompt=prompt,
        model=MODEL,
    )

    if task.is_successful():
        save_images(provider, task, "4_2_edit_fusion")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


# =============================================================================
# Part 5: Scene Composition
# =============================================================================

def generate_characters(provider, count: int) -> dict:
    """Generate multiple character references for scene composition tests."""
    print_header(f"Generating {count} Character References")

    char_descriptions = [
        ("xiaomei", "一位22岁的亚洲女性，长黑色直发，刘海，穿着浅蓝色连衣裙，气质清新甜美"),
        ("xiaoming", "一位25岁的亚洲男性，短黑发，戴黑框眼镜，穿着白色衬衫和深色西裤，斯文干净"),
        ("teacher", "一位45岁的亚洲女性，短卷发，穿着深蓝色职业套装，温和慈祥的表情"),
        ("student1", "一位18岁的亚洲男生，寸头，穿着蓝白校服，阳光开朗"),
        ("student2", "一位19岁的亚洲女生，马尾辫，穿着蓝白校服，活泼可爱"),
        ("grandpa", "一位65岁的亚洲男性，白发，穿着深灰色中山装，慈祥睿智"),
    ]

    char_urls = {}
    for i, (name, desc) in enumerate(char_descriptions[:count]):
        print(f"  [{i+1}/{count}] Generating {name}...")
        task = provider.generate_character_front_view(
            character_description=desc,
            style="realistic",
            size="2K",
        )
        if task.is_successful():
            save_images(provider, task, f"5_0_ref_{name}")
            char_urls[name] = task.image_urls[0]
            print(f"    OK")
        else:
            print(f"    FAILED: {task.error_message}")
            return None

    return char_urls


def test_scene_1_char(provider, char_urls: dict) -> bool:
    """Test 5.1: Single character in scene."""
    print_header("Test 5.1: Scene Composition (1 Character)")

    if "xiaomei" not in char_urls:
        print("  Skipped: No character URL")
        return False

    characters = [
        CharacterRef(
            name="小美",
            image_url=char_urls["xiaomei"],
            action="坐在咖啡桌前微笑着看向镜头",
            position="画面中央",
        )
    ]

    scene = "一间温馨的咖啡厅，柔和的午后阳光透过落地窗照进来，桌上摆着一杯拿铁"
    print(f"  Scene: {scene}")
    print(f"  Character: {characters[0].name} - {characters[0].action}")
    print("  Compositing...")

    task = provider.composite_character_scene(
        characters=characters,
        scene_description=scene,
        style="cinematic",
        size="2560x1440",
        n=1,
        model=MODEL,
    )

    if task.is_successful():
        save_images(provider, task, "5_1_scene_1char")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_scene_2_chars(provider, char_urls: dict) -> bool:
    """Test 5.2: Two characters interacting."""
    print_header("Test 5.2: Scene Composition (2 Characters)")

    if not all(k in char_urls for k in ["xiaomei", "xiaoming"]):
        print("  Skipped: Missing character URLs")
        return False

    characters = [
        CharacterRef(
            name="小美",
            image_url=char_urls["xiaomei"],
            action="正在递给对方一本书",
            position="左侧",
        ),
        CharacterRef(
            name="小明",
            image_url=char_urls["xiaoming"],
            action="伸手接过书，面带微笑",
            position="右侧",
        ),
    ]

    scene = "安静的图书馆内，背景是整齐的书架，温暖的灯光"
    print(f"  Scene: {scene}")
    for c in characters:
        print(f"    {c.name}: {c.action} ({c.position})")
    print("  Compositing...")

    task = provider.composite_character_scene(
        characters=characters,
        scene_description=scene,
        style="cinematic",
        size="2560x1440",
        n=1,
        model=MODEL,
    )

    if task.is_successful():
        save_images(provider, task, "5_2_scene_2chars")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_scene_3_chars(provider, char_urls: dict) -> bool:
    """Test 5.3: Three characters in scene."""
    print_header("Test 5.3: Scene Composition (3 Characters)")

    if not all(k in char_urls for k in ["xiaomei", "xiaoming", "teacher"]):
        print("  Skipped: Missing character URLs")
        return False

    characters = [
        CharacterRef(
            name="小美",
            image_url=char_urls["xiaomei"],
            action="举起奖杯庆祝",
            position="中间",
        ),
        CharacterRef(
            name="小明",
            image_url=char_urls["xiaoming"],
            action="鼓掌祝贺",
            position="左侧",
        ),
        CharacterRef(
            name="老师",
            image_url=char_urls["teacher"],
            action="微笑看着学生们",
            position="右侧",
        ),
    ]

    scene = "学校礼堂的颁奖典礼舞台上，背景有红色幕布和装饰花"
    print(f"  Scene: {scene}")
    for c in characters:
        print(f"    {c.name}: {c.action} ({c.position})")
    print("  Compositing...")

    task = provider.composite_character_scene(
        characters=characters,
        scene_description=scene,
        style="cinematic",
        size="2560x1440",
        n=1,
        model=MODEL,
    )

    if task.is_successful():
        save_images(provider, task, "5_3_scene_3chars")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_scene_5_chars(provider, char_urls: dict) -> bool:
    """Test 5.4: Five characters in scene (JiMeng advantage - more than Tongyi's limit of 3)."""
    print_header("Test 5.4: Scene Composition (5 Characters - JiMeng Advantage!)")

    required = ["xiaomei", "xiaoming", "teacher", "student1", "student2"]
    if not all(k in char_urls for k in required):
        print("  Skipped: Missing character URLs")
        return False

    characters = [
        CharacterRef(
            name="老师",
            image_url=char_urls["teacher"],
            action="站在讲台前讲解",
            position="中间偏左",
        ),
        CharacterRef(
            name="小美",
            image_url=char_urls["xiaomei"],
            action="认真听讲，做笔记",
            position="前排左侧",
        ),
        CharacterRef(
            name="小明",
            image_url=char_urls["xiaoming"],
            action="举手提问",
            position="前排右侧",
        ),
        CharacterRef(
            name="学生1",
            image_url=char_urls["student1"],
            action="看着黑板思考",
            position="后排左侧",
        ),
        CharacterRef(
            name="学生2",
            image_url=char_urls["student2"],
            action="和同学小声讨论",
            position="后排右侧",
        ),
    ]

    scene = "明亮的大学教室，黑板上写着数学公式，阳光从窗户照进来"
    print(f"  Scene: {scene}")
    print(f"  Characters: {len(characters)} (Tongyi limit is 3, JiMeng supports up to 14!)")
    for c in characters:
        print(f"    {c.name}: {c.action} ({c.position})")
    print("  Compositing...")

    task = provider.composite_character_scene(
        characters=characters,
        scene_description=scene,
        style="cinematic",
        size="2560x1440",
        n=1,
        model=MODEL,
    )

    if task.is_successful():
        save_images(provider, task, "5_4_scene_5chars")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_scene_angle_consistency(provider, char_urls: dict) -> bool:
    """Test 5.5: Same character in different scene angles."""
    print_header("Test 5.5: Scene Composition (Angle Consistency)")

    if "xiaomei" not in char_urls:
        print("  Skipped: No character URL")
        return False

    scenes = [
        ("面向镜头微笑，双手自然放在身侧", "城市街道上，阳光明媚", "5_5_angle_front"),
        ("侧身站立，望向远方", "公园的长椅旁，背景是绿树", "5_5_angle_side"),
        ("背对镜头，走向远方", "海边沙滩上，夕阳余晖", "5_5_angle_back"),
    ]

    all_ok = True
    for action, scene, prefix in scenes:
        characters = [
            CharacterRef(
                name="小美",
                image_url=char_urls["xiaomei"],
                action=action,
            )
        ]

        print(f"\n  Scene: {scene}")
        print(f"  Action: {action}")
        print("  Compositing...")

        task = provider.composite_character_scene(
            characters=characters,
            scene_description=scene,
            style="cinematic",
            size="2560x1440",
            n=1,
            model=MODEL,
        )

        if task.is_successful():
            save_images(provider, task, prefix)
            print("    OK")
        else:
            print(f"    FAILED: {task.error_message}")
            all_ok = False

    print(f"\n  Result: {'PASS' if all_ok else 'FAIL'}")
    return all_ok


# =============================================================================
# Main
# =============================================================================

def main():
    print_header("JiMeng (即梦/Seedream 4.5) Comprehensive Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {MODEL}")
    print(f"Output: {OUTPUT_DIR}")

    # Initialize provider
    provider = JiMengImageProvider()
    provider.initialize()

    results = {}

    # Part 1: Basic Functions
    results["1.1_connection"] = test_connection(provider)
    if not results["1.1_connection"]:
        print("\nCannot proceed without connection")
        print_summary(results)
        return 1

    t2i_url = test_text_to_image_basic(provider)
    results["1.2_t2i_basic"] = t2i_url is not None
    results["1.3_t2i_multi"] = test_text_to_image_multi(provider)

    # Part 2: Character Views
    char_front_url = test_character_front_view(provider)
    results["2.1_char_front"] = char_front_url is not None
    results["2.2_char_three_views"] = test_character_three_views(provider, char_front_url)
    results["2.3_char_sheet"] = test_character_sheet(provider, char_front_url)
    results["2.4_char_turnaround"] = test_character_turnaround(provider, char_front_url)

    # Part 3: Frame Generation
    frame_url = test_frame_generation(provider)
    results["3.1_frame_basic"] = frame_url is not None
    results["3.2_frame_with_char"] = test_frame_with_character(provider, char_front_url)

    # Part 4: Image Editing
    results["4.1_edit_style"] = test_image_editing_style(provider, t2i_url)
    results["4.2_edit_fusion"] = test_image_editing_fusion(provider, char_front_url, frame_url)

    # Part 5: Scene Composition (need to generate multiple characters)
    char_urls = generate_characters(provider, 5)
    if char_urls:
        results["5.1_scene_1char"] = test_scene_1_char(provider, char_urls)
        results["5.2_scene_2chars"] = test_scene_2_chars(provider, char_urls)
        results["5.3_scene_3chars"] = test_scene_3_chars(provider, char_urls)
        results["5.4_scene_5chars"] = test_scene_5_chars(provider, char_urls)
        results["5.5_angle_consistency"] = test_scene_angle_consistency(provider, char_urls)
    else:
        print("\nFailed to generate character references, skipping scene composition tests")
        for k in ["5.1_scene_1char", "5.2_scene_2chars", "5.3_scene_3chars",
                  "5.4_scene_5chars", "5.5_angle_consistency"]:
            results[k] = False

    print_summary(results)

    return 0 if all(results.values()) else 1


def print_summary(results):
    """Print test results summary."""
    print_header("Test Summary")

    categories = {
        "Part 1: Basic Functions": ["1.1_connection", "1.2_t2i_basic", "1.3_t2i_multi"],
        "Part 2: Character Views": ["2.1_char_front", "2.2_char_three_views",
                                    "2.3_char_sheet", "2.4_char_turnaround"],
        "Part 3: Frame Generation": ["3.1_frame_basic", "3.2_frame_with_char"],
        "Part 4: Image Editing": ["4.1_edit_style", "4.2_edit_fusion"],
        "Part 5: Scene Composition": ["5.1_scene_1char", "5.2_scene_2chars",
                                       "5.3_scene_3chars", "5.4_scene_5chars",
                                       "5.5_angle_consistency"],
    }

    passed = 0
    total = 0

    for category, keys in categories.items():
        print(f"\n{category}:")
        for key in keys:
            if key in results:
                status = "PASS" if results[key] else "FAIL"
                icon = "  " if results[key] else "  "
                label = key.split("_", 1)[1] if "_" in key else key
                print(f"  {icon} {label}: {status}")
                total += 1
                if results[key]:
                    passed += 1

    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} passed")

    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.glob("*.jpeg")) + list(OUTPUT_DIR.glob("*.png"))
        print(f"Output files: {len(files)} images in {OUTPUT_DIR}")

    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    sys.exit(main())
