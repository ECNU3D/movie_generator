#!/usr/bin/env python3
"""
Test script for Scene Composition (composite_character_scene)

Tests:
1. Single character in a scene
2. Two characters interacting
3. Three characters in a scene
4. Different model comparison
5. Angle consistency test
6. Validation errors

All generated images are downloaded to output/scene_composition_test/
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.providers.image import (
    TongyiImageProvider,
    CharacterRef,
)


def print_header(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def generate_character(provider, description: str, name: str, output_dir: str) -> str:
    """Generate a character front view and download it. Return image URL."""
    print(f"  Generating character: {name}...")
    task = provider.generate_character_front_view(
        character_description=description,
        style="realistic",
        size="1328*1328",
    )
    if task.is_successful():
        provider.download_task_images(task, save_dir=output_dir, prefix=f"ref_{name}")
        print(f"  OK -> {task.image_url[:60]}...")
        return task.image_url
    else:
        print(f"  FAILED: {task.error_message}")
        return None


def test_single_character_scene(provider, char_urls: dict, output_dir: str) -> bool:
    """Test 1: Single character in a scene."""
    print_header("Test 1: Single Character in Scene")

    characters = [
        CharacterRef(
            name="小美",
            image_url=char_urls["xiaomei"],
            action="坐在咖啡桌前微笑着看向镜头",
            position="画面中央",
        )
    ]

    print(f"Scene: 温馨的咖啡厅")
    print(f"Character: {characters[0].name} - {characters[0].action}")

    task = provider.composite_character_scene(
        characters=characters,
        scene_description="一间温馨的咖啡厅，柔和的午后阳光透过落地窗照进来，桌上摆着一杯拿铁",
        style="cinematic",
        size="1664*928",
        n=2,
    )

    if task.is_successful():
        paths = provider.download_task_images(task, save_dir=output_dir, prefix="01_single_char")
        print(f"OK: Generated {len(task.image_urls)} images")
        for p in paths:
            print(f"  -> {p}")
        return True
    else:
        print(f"FAILED: {task.error_message}")
        return False


def test_two_characters_interacting(provider, char_urls: dict, output_dir: str) -> bool:
    """Test 2: Two characters interacting."""
    print_header("Test 2: Two Characters Interacting")

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

    print(f"Scene: 图书馆")
    for c in characters:
        print(f"  {c.name}: {c.action} ({c.position})")

    task = provider.composite_character_scene(
        characters=characters,
        scene_description="安静的图书馆内，背景是整齐的书架，温暖的灯光",
        style="cinematic",
        size="1664*928",
        n=2,
    )

    if task.is_successful():
        paths = provider.download_task_images(task, save_dir=output_dir, prefix="02_two_chars")
        print(f"OK: Generated {len(task.image_urls)} images")
        for p in paths:
            print(f"  -> {p}")
        return True
    else:
        print(f"FAILED: {task.error_message}")
        return False


def test_three_characters_scene(provider, char_urls: dict, output_dir: str) -> bool:
    """Test 3: Three characters in a scene."""
    print_header("Test 3: Three Characters in Scene")

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

    print(f"Scene: 颁奖典礼")
    for c in characters:
        print(f"  {c.name}: {c.action} ({c.position})")

    task = provider.composite_character_scene(
        characters=characters,
        scene_description="学校礼堂的颁奖典礼舞台上，背景有红色幕布和装饰花",
        style="cinematic",
        size="1664*928",
        n=2,
    )

    if task.is_successful():
        paths = provider.download_task_images(task, save_dir=output_dir, prefix="03_three_chars")
        print(f"OK: Generated {len(task.image_urls)} images")
        for p in paths:
            print(f"  -> {p}")
        return True
    else:
        print(f"FAILED: {task.error_message}")
        return False


def test_angle_consistency(provider, char_urls: dict, output_dir: str) -> bool:
    """Test 4: Same character in different scene angles."""
    print_header("Test 4: Angle Consistency (same character, different scenes)")

    scenes = [
        ("面向镜头微笑，双手自然放在身侧", "城市街道上，阳光明媚", "04_angle_front"),
        ("侧身站立，望向远方", "公园的长椅旁，背景是绿树", "04_angle_side"),
        ("背对镜头，走向远方", "海边沙滩上，夕阳余晖", "04_angle_back"),
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

        print(f"  Scene: {scene} | Action: {action}")

        task = provider.composite_character_scene(
            characters=characters,
            scene_description=scene,
            style="cinematic",
            size="1664*928",
            n=1,
        )

        if task.is_successful():
            paths = provider.download_task_images(task, save_dir=output_dir, prefix=prefix)
            print(f"    OK -> {paths[0]}")
        else:
            print(f"    FAILED: {task.error_message}")
            all_ok = False

    return all_ok


def test_model_comparison(provider, char_urls: dict, output_dir: str) -> bool:
    """Test 5: Compare different models."""
    print_header("Test 5: Model Comparison")

    characters = [
        CharacterRef(
            name="小美",
            image_url=char_urls["xiaomei"],
            action="在花丛中微笑",
            position="画面中央",
        )
    ]
    scene = "春天的花园中，樱花盛开，花瓣飘落"

    models = ["qwen-image-edit-max", "qwen-image-edit-plus"]
    all_ok = True

    for model_name in models:
        print(f"  Model: {model_name}")

        task = provider.composite_character_scene(
            characters=characters,
            scene_description=scene,
            style="cinematic",
            size="1664*928",
            n=1,
            model=model_name,
        )

        if task.is_successful():
            prefix = f"05_model_{model_name.replace('.', '_').replace('-', '_')}"
            paths = provider.download_task_images(task, save_dir=output_dir, prefix=prefix)
            print(f"    OK -> {paths[0]}")
        else:
            print(f"    FAILED: {task.error_message}")
            all_ok = False

    return all_ok


def test_validation(provider) -> bool:
    """Test 6: Validation errors."""
    print_header("Test 6: Validation Errors")

    ok = True

    # Test: 0 characters
    try:
        provider.composite_character_scene(
            characters=[],
            scene_description="empty",
        )
        print("  FAILED: Should have raised ValueError for 0 characters")
        ok = False
    except ValueError as e:
        print(f"  OK: 0 characters -> {e}")

    # Test: 4 characters
    try:
        chars = [
            CharacterRef(name=f"c{i}", image_url=f"http://example.com/{i}.png")
            for i in range(4)
        ]
        provider.composite_character_scene(
            characters=chars,
            scene_description="too many",
        )
        print("  FAILED: Should have raised ValueError for 4 characters")
        ok = False
    except ValueError as e:
        print(f"  OK: 4 characters -> {e}")

    return ok


def main():
    print_header("Scene Composition Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    output_dir = str(PROJECT_ROOT / "output" / "scene_composition_test")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Initialize provider
    provider = TongyiImageProvider()
    provider.initialize()

    result = provider.test_connection()
    if not result["success"]:
        print(f"Connection failed: {result.get('error')}")
        return 1
    print("Provider connected")

    # Generate reference characters
    print_header("Generating Character References")

    char_descriptions = {
        "xiaomei": "一位22岁的亚洲女性，长黑色直发，刘海，大眼睛，穿着浅蓝色连衣裙，气质清新甜美",
        "xiaoming": "一位25岁的亚洲男性，短黑发，戴黑框眼镜，穿着白色衬衫和深色西裤，斯文干净",
        "teacher": "一位45岁的亚洲女性，短卷发，穿着深蓝色职业套装，温和慈祥的表情",
    }

    char_urls = {}
    for name, desc in char_descriptions.items():
        url = generate_character(provider, desc, name, output_dir)
        if not url:
            print(f"\nFailed to generate character {name}, cannot continue")
            return 1
        char_urls[name] = url

    # Run tests
    results = {}
    results["single_char"] = test_single_character_scene(provider, char_urls, output_dir)
    results["two_chars"] = test_two_characters_interacting(provider, char_urls, output_dir)
    results["three_chars"] = test_three_characters_scene(provider, char_urls, output_dir)
    results["angle_consistency"] = test_angle_consistency(provider, char_urls, output_dir)
    results["model_comparison"] = test_model_comparison(provider, char_urls, output_dir)
    results["validation"] = test_validation(provider)

    # Summary
    print_header("Test Summary")
    for name, passed in results.items():
        print(f"  {name:25s} {'PASS' if passed else 'FAIL'}")

    all_passed = all(results.values())
    print(f"\nOverall: {'All tests passed' if all_passed else 'Some tests failed'}")
    print(f"Images saved to: {output_dir}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
