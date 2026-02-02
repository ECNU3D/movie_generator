#!/usr/bin/env python3
"""
Test script for Character View Generation

Tests:
1. Generate character front view (reference image)
2. Generate three separate views
3. Generate single image with three views
4. Generate character turnaround sheet

All generated images will be downloaded to output/character_test/
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
    CharacterViewMode,
    ImageTaskStatus,
)


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_character_front_view(provider, output_dir: str) -> str:
    """Test character front view generation."""
    print_header("Step 1: Generate Character Front View")

    description = """
    一位25岁左右的亚洲女性，
    长黑色直发，齐刘海，
    大眼睛，精致的五官，
    穿着白色衬衫和蓝色牛仔裤，
    气质优雅，面带微笑
    """

    print(f"Character: {description.strip()}")
    print("Generating character front view...")

    task = provider.generate_character_front_view(
        character_description=description,
        style="realistic",
        size="1328*1328",
    )

    if task.is_successful():
        print(f"✓ Front view generated successfully")
        print(f"  URL: {task.image_url[:80]}...")

        # Download image
        paths = provider.download_task_images(
            task,
            save_dir=output_dir,
            prefix="01_front_view"
        )
        print(f"  Downloaded: {paths[0]}")
        return task.image_url
    else:
        print(f"✗ Failed: {task.error_message}")
        return None


def test_three_separate_images(provider, front_image_url: str, output_dir: str):
    """Test three separate character views generation."""
    print_header("Step 2: Generate Three Separate Views")

    description = "保持与正面图完全一致的角色外貌、服装和比例"

    print("Mode: THREE_SEPARATE_IMAGES")
    print("Generating front, side, and back views as separate images...")

    task = provider.generate_character_views(
        front_image_url=front_image_url,
        character_description=description,
        mode=CharacterViewMode.THREE_SEPARATE_IMAGES,
        style="realistic",
        size="1328*1328",
    )

    if task.is_successful():
        print(f"✓ Three separate views generated successfully")
        print(f"  Generated {len(task.image_urls)} images")

        # Download images
        paths = provider.download_task_images(
            task,
            save_dir=output_dir,
            prefix="02_separate_view"
        )
        for path in paths:
            print(f"  Downloaded: {path}")
        return True
    else:
        print(f"✗ Failed: {task.error_message}")
        return False


def test_single_image_three_views(provider, front_image_url: str, output_dir: str):
    """Test single image with three views."""
    print_header("Step 3: Generate Single Image with Three Views")

    description = "角色三视图参考，保持完全一致的外貌和服装"

    print("Mode: SINGLE_IMAGE_THREE_VIEWS")
    print("Generating one image containing front, side, and back views...")

    task = provider.generate_character_views(
        front_image_url=front_image_url,
        character_description=description,
        mode=CharacterViewMode.SINGLE_IMAGE_THREE_VIEWS,
        style="realistic",
        size="1664*928",  # Wide format for three views
    )

    if task.is_successful():
        print(f"✓ Single image three views generated successfully")
        print(f"  URL: {task.image_url[:80]}...")

        # Download image
        paths = provider.download_task_images(
            task,
            save_dir=output_dir,
            prefix="03_three_views_single"
        )
        print(f"  Downloaded: {paths[0]}")
        return True
    else:
        print(f"✗ Failed: {task.error_message}")
        return False


def test_turnaround_sheet(provider, front_image_url: str, output_dir: str):
    """Test character turnaround sheet generation."""
    print_header("Step 4: Generate Character Turnaround Sheet")

    description = "专业游戏角色设定图，包含多角度视图"

    print("Mode: TURNAROUND_SHEET")
    print("Generating professional character turnaround sheet...")

    task = provider.generate_character_views(
        front_image_url=front_image_url,
        character_description=description,
        mode=CharacterViewMode.TURNAROUND_SHEET,
        style="realistic",
        size="1664*928",  # Wide format for turnaround
    )

    if task.is_successful():
        print(f"✓ Turnaround sheet generated successfully")
        print(f"  URL: {task.image_url[:80]}...")

        # Download image
        paths = provider.download_task_images(
            task,
            save_dir=output_dir,
            prefix="04_turnaround_sheet"
        )
        print(f"  Downloaded: {paths[0]}")
        return True
    else:
        print(f"✗ Failed: {task.error_message}")
        return False


def main():
    print_header("Character View Generation Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Setup output directory
    output_dir = PROJECT_ROOT / "output" / "character_test"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")

    # Initialize provider
    provider = TongyiImageProvider()
    provider.initialize()

    result = provider.test_connection()
    if not result["success"]:
        print(f"✗ Connection failed: {result.get('error')}")
        return

    print("✓ Provider connected successfully")

    # Test results
    results = {
        "front_view": False,
        "three_separate": False,
        "single_three_views": False,
        "turnaround_sheet": False,
    }

    # Step 1: Generate front view
    front_image_url = test_character_front_view(provider, str(output_dir))
    if front_image_url:
        results["front_view"] = True

        # Step 2: Three separate images
        results["three_separate"] = test_three_separate_images(
            provider, front_image_url, str(output_dir)
        )

        # Step 3: Single image with three views
        results["single_three_views"] = test_single_image_three_views(
            provider, front_image_url, str(output_dir)
        )

        # Step 4: Turnaround sheet
        results["turnaround_sheet"] = test_turnaround_sheet(
            provider, front_image_url, str(output_dir)
        )

    # Summary
    print_header("Test Summary")
    print(f"  Front View:         {'✓' if results['front_view'] else '✗'}")
    print(f"  Three Separate:     {'✓' if results['three_separate'] else '✗'}")
    print(f"  Single Three Views: {'✓' if results['single_three_views'] else '✗'}")
    print(f"  Turnaround Sheet:   {'✓' if results['turnaround_sheet'] else '✗'}")

    all_passed = all(results.values())
    print(f"\nOverall: {'✓ All tests passed' if all_passed else '✗ Some tests failed'}")
    print(f"\nImages saved to: {output_dir}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
