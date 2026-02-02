#!/usr/bin/env python3
"""
Test script for Image Providers

Tests:
1. Text-to-Image generation
2. Frame generation
3. Character front view generation
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.providers.image import (
    TongyiImageProvider,
    TONGYI_IMAGE_MODELS,
    CharacterViewMode,
    ImageTaskStatus,
)


def test_connection():
    """Test provider connection."""
    print("=" * 60)
    print("Test 1: Provider Connection")
    print("=" * 60)

    provider = TongyiImageProvider()
    provider.initialize()

    result = provider.test_connection()
    if result["success"]:
        print("✓ Connection successful")
        return provider
    else:
        print(f"✗ Connection failed: {result.get('error')}")
        return None


def test_text_to_image(provider):
    """Test text-to-image generation."""
    print("\n" + "=" * 60)
    print("Test 2: Text-to-Image")
    print("=" * 60)

    prompt = "一只可爱的橘猫躺在阳光下的窗台上，窗外是蓝天白云"

    print(f"Prompt: {prompt}")
    print("Generating image...")

    task = provider.text_to_image(
        prompt=prompt,
        size="1328*1328",
        n=1,
        prompt_extend=True,
    )

    if task.is_successful():
        print(f"✓ Image generated successfully")
        print(f"  URL: {task.image_url[:80]}...")
        return task.image_url
    else:
        print(f"✗ Failed: {task.error_message}")
        return None


def test_frame_generation(provider):
    """Test frame generation for video."""
    print("\n" + "=" * 60)
    print("Test 3: Frame Generation")
    print("=" * 60)

    prompt = "一位年轻女子站在樱花树下，微风吹过，粉色花瓣在空中飘落，柔和的春日阳光"

    print(f"Scene: {prompt}")
    print("Generating frame...")

    task = provider.generate_frame(
        prompt=prompt,
        size="1664*928",
        style="cinematic",
    )

    if task.is_successful():
        print(f"✓ Frame generated successfully")
        print(f"  URL: {task.image_url[:80]}...")
        return task.image_url
    else:
        print(f"✗ Failed: {task.error_message}")
        return None


def test_character_front_view(provider):
    """Test character front view generation."""
    print("\n" + "=" * 60)
    print("Test 4: Character Front View")
    print("=" * 60)

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
        print(f"✓ Character front view generated successfully")
        print(f"  URL: {task.image_url[:80]}...")
        return task.image_url
    else:
        print(f"✗ Failed: {task.error_message}")
        return None


def test_models_info():
    """Test model information retrieval."""
    print("\n" + "=" * 60)
    print("Test 5: Available Models")
    print("=" * 60)

    models = TongyiImageProvider.get_available_models()
    print(f"✓ Found {len(models)} models:")

    for name, info in models.items():
        print(f"  - {name}: {info.description}")
        print(f"    Type: {info.model_type}, Sync: {info.sync_supported}")


def main():
    print("\n" + "=" * 60)
    print("Image Provider Test Suite")
    print("=" * 60)

    # Test connection
    provider = test_connection()
    if not provider:
        print("\n❌ Cannot proceed without connection")
        return

    # Test models info
    test_models_info()

    # Test text-to-image
    image_url = test_text_to_image(provider)

    # Test frame generation
    frame_url = test_frame_generation(provider)

    # Test character generation
    char_url = test_character_front_view(provider)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"  Connection: ✓")
    print(f"  Models Info: ✓")
    print(f"  Text-to-Image: {'✓' if image_url else '✗'}")
    print(f"  Frame Generation: {'✓' if frame_url else '✗'}")
    print(f"  Character Front View: {'✓' if char_url else '✗'}")

    print("\n💡 Generated image URLs are valid for 24 hours")
    print("   Download them before they expire!")


if __name__ == "__main__":
    main()
