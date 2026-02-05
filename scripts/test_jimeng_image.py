#!/usr/bin/env python3
"""
Test script for JiMeng (即梦/Seedream) Image Provider

Tests:
1. Connection test
2. Text-to-Image - basic (2K)
3. Text-to-Image - size conversion (1280*720 -> auto-convert)
4. Text-to-Image - multi-image output (n=2, sequential)
5. Image editing - single image style transfer
6. Character front view generation
7. Frame generation
8. Model comparison (Seedream 4.5 vs 4.0)
9. Model info and parameter validation

All images saved to output/jimeng_image_test/
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.providers.image import (
    JiMengImageProvider,
    JIMENG_IMAGE_MODELS,
    ImageTaskStatus,
)

OUTPUT_DIR = PROJECT_ROOT / "output" / "jimeng_image_test"


def save_results(provider, task, prefix: str) -> list:
    """Download and save task images."""
    if not task.is_successful():
        return []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = provider.download_task_images(task, save_dir=str(OUTPUT_DIR), prefix=prefix)
    for p in paths:
        print(f"  Saved: {p}")
    return paths


def test_connection():
    """Test 1: Provider connection."""
    print("=" * 60)
    print("Test 1: Provider Connection")
    print("=" * 60)

    provider = JiMengImageProvider()
    provider.initialize()

    result = provider.test_connection()
    if result["success"]:
        print(f"  API key: {result.get('api_key_preview', 'N/A')}")
        print(f"  Models: {result.get('supported_models', [])}")
        print("  Result: PASS")
        return provider
    else:
        print(f"  Error: {result.get('error')}")
        print("  Result: FAIL")
        return None


def test_text_to_image_basic(provider):
    """Test 2: Text-to-Image - basic 2K generation."""
    print("\n" + "=" * 60)
    print("Test 2: Text-to-Image (Basic 2K)")
    print("=" * 60)

    prompt = "一只可爱的橘猫躺在阳光下的窗台上，窗外是蓝天白云，温暖的光线洒在它毛茸茸的身上"

    print(f"  Prompt: {prompt}")
    print(f"  Size: 2K")
    print(f"  Model: default (Seedream 4.5)")
    print("  Generating...")

    task = provider.text_to_image(
        prompt=prompt,
        size="2K",
        n=1,
    )

    if task.is_successful():
        print(f"  Status: COMPLETED")
        print(f"  Images: {len(task.image_urls)}")
        save_results(provider, task, "t2i_basic")
        print("  Result: PASS")
        return task.image_urls[0] if task.image_urls else None
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return None


def test_text_to_image_size_conversion(provider):
    """Test 3: Text-to-Image - size conversion from base class format."""
    print("\n" + "=" * 60)
    print("Test 3: Text-to-Image (Size Conversion)")
    print("=" * 60)

    prompt = "宁静的日式庭院，一棵红叶枫树映照在池塘中，秋日暖阳"

    print(f"  Prompt: {prompt}")
    print(f"  Input size: 1664*928 (base class format)")
    print(f"  Expected: auto-converted to JiMeng format")
    print("  Generating...")

    task = provider.text_to_image(
        prompt=prompt,
        size="1664*928",
        n=1,
    )

    if task.is_successful():
        actual_size = task.metadata.get("size", "unknown")
        print(f"  Actual size used: {actual_size}")
        print(f"  Images: {len(task.image_urls)}")
        save_results(provider, task, "t2i_size_convert")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_text_to_image_multi(provider):
    """Test 4: Text-to-Image - multi-image output with sequential generation."""
    print("\n" + "=" * 60)
    print("Test 4: Text-to-Image (Multi-Image, n=2)")
    print("=" * 60)

    prompt = "一位身穿汉服的年轻女子，站在古风建筑前，背景是飘落的桃花"

    print(f"  Prompt: {prompt}")
    print(f"  Size: 2K")
    print(f"  n: 2 (sequential generation)")
    print("  Generating...")

    task = provider.text_to_image(
        prompt=prompt,
        size="2K",
        n=2,
    )

    if task.is_successful():
        print(f"  Status: COMPLETED")
        print(f"  Images: {len(task.image_urls)}")
        save_results(provider, task, "t2i_multi")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_image_editing(provider, reference_url: str):
    """Test 5: Image editing - style transfer on a single image."""
    print("\n" + "=" * 60)
    print("Test 5: Image Editing (Style Transfer)")
    print("=" * 60)

    if not reference_url:
        print("  Skipped: No reference image from previous test")
        return False

    prompt = "将这张图片转换为水彩画风格，保持主体不变，增加艺术感"

    print(f"  Input: image from test 2")
    print(f"  Prompt: {prompt}")
    print("  Generating...")

    task = provider.edit_image(
        images=[reference_url],
        prompt=prompt,
        n=1,
    )

    if task.is_successful():
        print(f"  Status: COMPLETED")
        print(f"  Images: {len(task.image_urls)}")
        save_results(provider, task, "edit_style")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_character_front_view(provider):
    """Test 6: Character front view generation."""
    print("\n" + "=" * 60)
    print("Test 6: Character Front View")
    print("=" * 60)

    description = (
        "一位25岁左右的亚洲女性，"
        "长黑色直发，齐刘海，"
        "大眼睛，精致的五官，"
        "穿着白色衬衫和蓝色牛仔裤，"
        "气质优雅，面带微笑"
    )

    print(f"  Character: {description}")
    print("  Generating front view...")

    task = provider.generate_character_front_view(
        character_description=description,
        style="realistic",
        size="2K",
    )

    if task.is_successful():
        print(f"  Status: COMPLETED")
        print(f"  Images: {len(task.image_urls)}")
        save_results(provider, task, "char_front")
        print("  Result: PASS")
        return task.image_urls[0] if task.image_urls else None
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return None


def test_frame_generation(provider):
    """Test 7: Video frame generation."""
    print("\n" + "=" * 60)
    print("Test 7: Frame Generation")
    print("=" * 60)

    prompt = "一位年轻女子站在樱花树下，微风吹过，粉色花瓣在空中飘落，柔和的春日阳光，电影画面"

    print(f"  Scene: {prompt}")
    print("  Generating frame...")

    task = provider.generate_frame(
        prompt=prompt,
        size="2560x1440",
        style="cinematic",
    )

    if task.is_successful():
        print(f"  Status: COMPLETED")
        print(f"  Images: {len(task.image_urls)}")
        save_results(provider, task, "frame")
        print("  Result: PASS")
        return True
    else:
        print(f"  Error: {task.error_message}")
        print("  Result: FAIL")
        return False


def test_model_comparison(provider):
    """Test 8: Model comparison - Seedream 4.5 vs 4.0."""
    print("\n" + "=" * 60)
    print("Test 8: Model Comparison (4.5 vs 4.0)")
    print("=" * 60)

    prompt = "夕阳下的海边灯塔，金色光芒洒在波光粼粼的海面上，天空渐变为紫红色"
    models = ["doubao-seedream-4-5-251128", "doubao-seedream-4-0-250828"]

    results = {}
    for model in models:
        print(f"\n  Model: {model}")
        print("  Generating...")

        task = provider.text_to_image(
            prompt=prompt,
            size="2K",
            n=1,
            model=model,
        )

        if task.is_successful():
            print(f"  Status: COMPLETED")
            prefix = f"compare_{model.split('-')[1]}_{model.split('-')[2]}"
            save_results(provider, task, prefix)
            results[model] = True
        else:
            print(f"  Error: {task.error_message}")
            results[model] = False

    all_pass = all(results.values())
    print(f"\n  Result: {'PASS' if all_pass else 'PARTIAL'}")
    return all_pass


def test_models_info():
    """Test 9: Model information and parameter validation."""
    print("\n" + "=" * 60)
    print("Test 9: Model Info & Validation")
    print("=" * 60)

    models = JiMengImageProvider.get_available_models()
    print(f"  Available models: {len(models)}")

    for name, info in models.items():
        print(f"\n  Model: {name}")
        print(f"    Description: {info.description}")
        print(f"    Type: {info.model_type}")
        print(f"    Sizes: {info.sizes}")
        print(f"    Max input images: {info.max_input_images}")

    # Test size validation
    sizes_45 = JiMengImageProvider.get_supported_sizes("doubao-seedream-4-5-251128")
    sizes_40 = JiMengImageProvider.get_supported_sizes("doubao-seedream-4-0-250828")
    sizes_invalid = JiMengImageProvider.get_supported_sizes("nonexistent")

    print(f"\n  Seedream 4.5 sizes: {sizes_45}")
    print(f"  Seedream 4.0 sizes: {sizes_40}")
    print(f"  Invalid model sizes: {sizes_invalid} (expected empty)")

    # Test size conversion
    provider = JiMengImageProvider()
    test_sizes = [
        ("2K", "2K"),
        ("4K", "4K"),
        ("1664*928", "2560x1440"),
        ("1024*1024", "2048x2048"),
        ("2048x2048", "2048x2048"),
    ]
    print("\n  Size conversion tests:")
    all_pass = True
    for input_size, expected in test_sizes:
        actual = provider._convert_size(input_size)
        status = "PASS" if actual == expected else "FAIL"
        if actual != expected:
            all_pass = False
        print(f"    {input_size} -> {actual} (expected {expected}) [{status}]")

    print(f"\n  Result: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


def main():
    print("\n" + "=" * 60)
    print("JiMeng (即梦/Seedream) Image Provider Test Suite")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")

    results = {}

    # Test 9: Model info (no API needed)
    results["model_info"] = test_models_info()

    # Test 1: Connection
    provider = test_connection()
    if not provider:
        print("\n  Cannot proceed without connection")
        print_summary(results)
        return

    # Test 2: Text-to-Image basic
    ref_url = test_text_to_image_basic(provider)
    results["t2i_basic"] = ref_url is not None

    # Test 3: Size conversion
    results["t2i_size"] = test_text_to_image_size_conversion(provider)

    # Test 4: Multi-image
    results["t2i_multi"] = test_text_to_image_multi(provider)

    # Test 5: Image editing (uses image from test 2)
    results["edit"] = test_image_editing(provider, ref_url)

    # Test 6: Character front view
    char_url = test_character_front_view(provider)
    results["char_front"] = char_url is not None

    # Test 7: Frame generation
    results["frame"] = test_frame_generation(provider)

    # Test 8: Model comparison
    results["model_compare"] = test_model_comparison(provider)

    print_summary(results)


def print_summary(results):
    """Print test results summary."""
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    labels = {
        "model_info": "Model Info & Validation",
        "t2i_basic": "Text-to-Image (Basic)",
        "t2i_size": "Text-to-Image (Size Conversion)",
        "t2i_multi": "Text-to-Image (Multi-Image)",
        "edit": "Image Editing",
        "char_front": "Character Front View",
        "frame": "Frame Generation",
        "model_compare": "Model Comparison",
    }

    passed = 0
    total = len(results)
    for key, label in labels.items():
        if key in results:
            status = "PASS" if results[key] else "FAIL"
            icon = "  " if results[key] else "  "
            print(f"  {icon} {label}: {status}")
            if results[key]:
                passed += 1

    print(f"\n  Total: {passed}/{total} passed")
    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.iterdir())
        print(f"  Output files: {len(files)} in {OUTPUT_DIR}")

    print("\n  Note: Generated image URLs are valid for limited time.")
    print("  Images have been downloaded to the output directory.")


if __name__ == "__main__":
    main()
