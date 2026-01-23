#!/usr/bin/env python3
"""
Test script for video generation providers.

Usage:
    # Test all providers
    python test_providers.py

    # Test specific provider
    python test_providers.py --provider kling

    # Run text-to-video test
    python test_providers.py --provider kling --test t2v

    # Run image-to-video test
    python test_providers.py --provider tongyi --test i2v --image-url https://example.com/image.jpg

    # Test connection only
    python test_providers.py --provider jimeng --test connection

    # List all configured providers
    python test_providers.py --list

Configuration:
    Copy config.yaml to config.local.yaml and fill in your API keys.
    You can also use environment variables:
    - KLING_ACCESS_KEY, KLING_SECRET_KEY
    - TONGYI_API_KEY
    - JIMENG_ACCESS_KEY, JIMENG_SECRET_KEY
    - HAILUO_API_KEY
"""

import argparse
import sys
import time
from typing import Optional

from config import get_config, reload_config
from base import VideoTask, TaskStatus


# Color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.END}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {text}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}[ERROR]{Colors.END} {text}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {text}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}[INFO]{Colors.END} {text}")


def print_task_status(task: VideoTask):
    """Print task status in a formatted way."""
    status_colors = {
        TaskStatus.PENDING: Colors.YELLOW,
        TaskStatus.PROCESSING: Colors.BLUE,
        TaskStatus.COMPLETED: Colors.GREEN,
        TaskStatus.FAILED: Colors.RED,
        TaskStatus.CANCELLED: Colors.YELLOW,
    }

    color = status_colors.get(task.status, Colors.END)
    print(f"\n{Colors.BOLD}Task Status:{Colors.END}")
    print(f"  Task ID:  {task.task_id}")
    print(f"  Provider: {task.provider}")
    print(f"  Status:   {color}{task.status.value}{Colors.END}")
    print(f"  Progress: {task.progress}%")

    if task.video_url:
        print(f"  Video URL: {Colors.GREEN}{task.video_url}{Colors.END}")

    if task.error_message:
        print(f"  Error: {Colors.RED}{task.error_message}{Colors.END}")


def get_provider_instance(name: str):
    """Get a provider instance by name."""
    from kling import KlingProvider
    from tongyi import TongyiProvider
    from jimeng import JimengProvider
    from hailuo import HailuoProvider

    providers = {
        "kling": KlingProvider,
        "tongyi": TongyiProvider,
        "jimeng": JimengProvider,
        "hailuo": HailuoProvider,
    }

    if name not in providers:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")

    return providers[name]()


def test_connection(provider_name: str) -> bool:
    """Test connection to a provider."""
    print_info(f"Testing connection to {provider_name}...")

    try:
        provider = get_provider_instance(provider_name)
        result = provider.test_connection()

        if result.get("success"):
            print_success(f"{provider_name}: {result.get('message', 'Connection successful')}")
            if "key_preview" in result:
                print_info(f"  Key preview: {result['key_preview']}")
            if "token_preview" in result:
                print_info(f"  Token preview: {result['token_preview']}")
            return True
        else:
            print_error(f"{provider_name}: {result.get('error', 'Connection failed')}")
            return False

    except Exception as e:
        print_error(f"{provider_name}: {str(e)}")
        return False


def test_text_to_video(
    provider_name: str,
    prompt: str,
    wait: bool = True,
    timeout: int = 300
) -> Optional[VideoTask]:
    """Test text-to-video generation."""
    print_header(f"Text-to-Video Test: {provider_name}")

    print_info(f"Prompt: {prompt[:100]}...")

    try:
        provider = get_provider_instance(provider_name)

        # Submit task
        print_info("Submitting task...")
        task = provider.submit_text_to_video(prompt)
        print_success(f"Task submitted: {task.task_id}")

        if not wait:
            print_info("Not waiting for completion. Use task ID to check status later.")
            return task

        # Wait for completion
        print_info(f"Waiting for completion (timeout: {timeout}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            task = provider.get_task_status(task.task_id)
            elapsed = int(time.time() - start_time)
            print(f"\r  Status: {task.status.value} | Progress: {task.progress}% | Elapsed: {elapsed}s    ", end="")

            if task.is_completed():
                print()  # New line
                break

            time.sleep(5)

        print_task_status(task)

        if task.is_successful():
            print_success("Video generated successfully!")
        elif task.status == TaskStatus.FAILED:
            print_error(f"Video generation failed: {task.error_message}")
        else:
            print_warning("Task did not complete within timeout")

        return task

    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return None


def test_image_to_video(
    provider_name: str,
    image_url: str,
    prompt: str,
    wait: bool = True,
    timeout: int = 300
) -> Optional[VideoTask]:
    """Test image-to-video generation."""
    print_header(f"Image-to-Video Test: {provider_name}")

    print_info(f"Image URL: {image_url[:80]}...")
    print_info(f"Prompt: {prompt[:100]}...")

    try:
        provider = get_provider_instance(provider_name)

        # Submit task
        print_info("Submitting task...")
        task = provider.submit_image_to_video(image_url, prompt)
        print_success(f"Task submitted: {task.task_id}")

        if not wait:
            print_info("Not waiting for completion. Use task ID to check status later.")
            return task

        # Wait for completion
        print_info(f"Waiting for completion (timeout: {timeout}s)...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            task = provider.get_task_status(task.task_id)
            elapsed = int(time.time() - start_time)
            print(f"\r  Status: {task.status.value} | Progress: {task.progress}% | Elapsed: {elapsed}s    ", end="")

            if task.is_completed():
                print()  # New line
                break

            time.sleep(5)

        print_task_status(task)

        if task.is_successful():
            print_success("Video generated successfully!")
        elif task.status == TaskStatus.FAILED:
            print_error(f"Video generation failed: {task.error_message}")
        else:
            print_warning("Task did not complete within timeout")

        return task

    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return None


def check_task_status(provider_name: str, task_id: str) -> Optional[VideoTask]:
    """Check status of an existing task."""
    print_header(f"Check Task Status: {provider_name}")

    print_info(f"Task ID: {task_id}")

    try:
        provider = get_provider_instance(provider_name)
        task = provider.get_task_status(task_id)
        print_task_status(task)
        return task

    except Exception as e:
        print_error(f"Status check failed: {str(e)}")
        return None


def list_providers():
    """List all configured providers and their status."""
    print_header("Configured Providers")

    config = get_config()
    providers = ["kling", "tongyi", "jimeng", "hailuo"]

    print(f"{'Provider':<15} {'Name':<25} {'Enabled':<10} {'Configured':<12}")
    print("-" * 62)

    for name in providers:
        try:
            provider_config = config.get_provider_config(name)
            enabled = "Yes" if provider_config.enabled else "No"
            configured = "Yes" if config.is_provider_configured(name) else "No"

            enabled_color = Colors.GREEN if provider_config.enabled else Colors.RED
            configured_color = Colors.GREEN if config.is_provider_configured(name) else Colors.RED

            print(f"{name:<15} {provider_config.name:<25} {enabled_color}{enabled:<10}{Colors.END} {configured_color}{configured:<12}{Colors.END}")
        except Exception as e:
            print(f"{name:<15} {'Error':<25} {Colors.RED}{'Error':<10}{Colors.END} {str(e)}")


def run_all_tests(providers: Optional[list] = None, test_type: str = "connection"):
    """Run tests for all or specified providers."""
    if providers is None:
        providers = ["kling", "tongyi", "jimeng", "hailuo"]

    print_header(f"Running {test_type} tests")

    results = {}
    for name in providers:
        if test_type == "connection":
            results[name] = test_connection(name)
        elif test_type == "t2v":
            prompt = "A cute orange cat yawning in the sunlight, slow motion, cinematic quality"
            task = test_text_to_video(name, prompt, wait=False)
            results[name] = task is not None

    # Summary
    print_header("Test Results Summary")
    print(f"{'Provider':<15} {'Result':<10}")
    print("-" * 25)

    for name, success in results.items():
        color = Colors.GREEN if success else Colors.RED
        status = "PASS" if success else "FAIL"
        print(f"{name:<15} {color}{status:<10}{Colors.END}")


def main():
    parser = argparse.ArgumentParser(
        description="Test video generation providers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--provider", "-p",
        choices=["kling", "tongyi", "jimeng", "hailuo", "all"],
        default="all",
        help="Provider to test (default: all)"
    )

    parser.add_argument(
        "--test", "-t",
        choices=["connection", "t2v", "i2v", "status"],
        default="connection",
        help="Test type (default: connection)"
    )

    parser.add_argument(
        "--prompt",
        default="A cute orange cat yawning in the sunlight, slow motion, cinematic quality",
        help="Prompt for video generation"
    )

    parser.add_argument(
        "--image-url",
        help="Image URL for image-to-video test"
    )

    parser.add_argument(
        "--task-id",
        help="Task ID for status check"
    )

    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for task completion"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)"
    )

    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all configured providers"
    )

    parser.add_argument(
        "--config",
        help="Path to config file"
    )

    args = parser.parse_args()

    # Load config
    if args.config:
        reload_config(args.config)

    # List providers
    if args.list:
        list_providers()
        return

    # Run tests
    if args.provider == "all":
        run_all_tests(test_type=args.test)
    else:
        if args.test == "connection":
            test_connection(args.provider)
        elif args.test == "t2v":
            test_text_to_video(
                args.provider,
                args.prompt,
                wait=not args.no_wait,
                timeout=args.timeout
            )
        elif args.test == "i2v":
            if not args.image_url:
                print_error("--image-url is required for i2v test")
                sys.exit(1)
            test_image_to_video(
                args.provider,
                args.image_url,
                args.prompt,
                wait=not args.no_wait,
                timeout=args.timeout
            )
        elif args.test == "status":
            if not args.task_id:
                print_error("--task-id is required for status check")
                sys.exit(1)
            check_task_status(args.provider, args.task_id)


if __name__ == "__main__":
    main()
