"""
Video Generation Comparison Tool - Streamlit App

A tool for comparing video generation across multiple AI providers.
"""

import os
import sys
import time
import requests
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import streamlit as st

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from comparison.model_capabilities import (
    MODEL_CAPABILITIES,
    PROVIDER_NAMES,
    ModelCapability,
    GenerationType,
    get_all_models,
    get_models_by_provider,
    filter_models,
    check_model_compatibility,
    get_available_durations,
    get_available_resolutions,
    get_available_aspect_ratios,
    get_model_duration_in_range,
)

from providers.kling import KlingProvider
from providers.tongyi import TongyiProvider
from providers.jimeng import JimengProvider
from providers.hailuo import HailuoProvider
from providers.base import TaskStatus


@dataclass
class GenerationResult:
    """Result of a video generation task."""
    provider: str
    model_id: str
    model_name: str
    success: bool
    video_url: Optional[str] = None
    video_path: Optional[str] = None
    generation_time: float = 0.0
    estimated_cost: float = 0.0
    error_message: Optional[str] = None
    task_id: Optional[str] = None
    duration_used: Optional[int] = None  # Actual duration used for this model


# Provider instances cache
@st.cache_resource
def get_provider_instances() -> Dict:
    """Initialize and cache provider instances."""
    providers = {}

    try:
        providers["kling"] = KlingProvider()
    except Exception as e:
        st.warning(f"Kling provider initialization failed: {e}")

    try:
        providers["tongyi"] = TongyiProvider()
    except Exception as e:
        st.warning(f"Tongyi provider initialization failed: {e}")

    try:
        providers["jimeng"] = JimengProvider()
    except Exception as e:
        st.warning(f"Jimeng provider initialization failed: {e}")

    try:
        providers["hailuo"] = HailuoProvider()
    except Exception as e:
        st.warning(f"Hailuo provider initialization failed: {e}")

    return providers


def download_video(url: str, filename: str) -> Optional[str]:
    """Download video from URL and save to temp directory."""
    try:
        output_dir = Path("comparison_output")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / filename

        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return str(output_path)
    except Exception as e:
        st.error(f"Download failed: {e}")
        return None


def generate_video(
    provider_name: str,
    model: ModelCapability,
    generation_type: GenerationType,
    prompt: str,
    duration_range: Tuple[int, int],
    resolution: str,
    aspect_ratio: str,
    image_url: Optional[str] = None,
    mode: str = "std",
    progress_callback=None,
) -> GenerationResult:
    """Generate video using the specified provider and model."""

    providers = get_provider_instances()
    provider = providers.get(provider_name)

    if not provider:
        return GenerationResult(
            provider=provider_name,
            model_id=model.model_id,
            model_name=model.display_name,
            success=False,
            error_message="Provider not available"
        )

    # Get the best duration for this model within the range
    duration = get_model_duration_in_range(model, duration_range)
    if duration is None:
        return GenerationResult(
            provider=provider_name,
            model_id=model.model_id,
            model_name=model.display_name,
            success=False,
            error_message=f"No supported duration in range {duration_range}"
        )

    start_time = time.time()

    try:
        # Submit task based on generation type
        if generation_type == GenerationType.TEXT_TO_VIDEO:
            if provider_name == "kling":
                task = provider.submit_text_to_video(
                    prompt=prompt,
                    duration=duration,
                    model=model.model_id,
                    mode=mode,
                    aspect_ratio=aspect_ratio,
                )
            elif provider_name == "tongyi":
                task = provider.submit_text_to_video(
                    prompt=prompt,
                    duration=duration,
                    model=model.model_id,
                    resolution=resolution,
                )
            elif provider_name == "jimeng":
                task = provider.submit_text_to_video(
                    prompt=prompt,
                    duration=duration,
                    model=model.model_id,
                    aspect_ratio=aspect_ratio,
                )
            elif provider_name == "hailuo":
                task = provider.submit_text_to_video(
                    prompt=prompt,
                    duration=duration,
                    resolution=resolution,
                    model=model.model_id,
                )
            else:
                raise ValueError(f"Unknown provider: {provider_name}")

        elif generation_type == GenerationType.IMAGE_TO_VIDEO:
            if not image_url:
                raise ValueError("Image URL required for image-to-video")

            if provider_name == "kling":
                task = provider.submit_image_to_video(
                    image_url=image_url,
                    prompt=prompt,
                    duration=duration,
                    model=model.model_id,
                    mode=mode,
                )
            elif provider_name == "tongyi":
                task = provider.submit_image_to_video(
                    image_url=image_url,
                    prompt=prompt,
                    duration=duration,
                    model=model.model_id,
                    resolution=resolution,
                )
            elif provider_name == "jimeng":
                task = provider.submit_image_to_video(
                    image_url=image_url,
                    prompt=prompt,
                    duration=duration,
                    model=model.model_id,
                    aspect_ratio=aspect_ratio,
                )
            elif provider_name == "hailuo":
                task = provider.submit_image_to_video(
                    image_url=image_url,
                    prompt=prompt,
                    duration=duration,
                    resolution=resolution,
                    model=model.model_id,
                )
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        else:
            raise ValueError(f"Unsupported generation type: {generation_type}")

        if progress_callback:
            progress_callback(f"Task submitted: {task.task_id}")

        # Wait for completion
        result = provider.wait_for_completion(
            task.task_id,
            timeout=600,
            poll_interval=10
        )

        generation_time = time.time() - start_time
        estimated_cost = model.cost_per_second * duration

        if result.status == TaskStatus.COMPLETED and result.video_url:
            # Download video
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{provider_name}_{model.model_id}_{timestamp}.mp4"
            video_path = download_video(result.video_url, filename)

            return GenerationResult(
                provider=provider_name,
                model_id=model.model_id,
                model_name=model.display_name,
                success=True,
                video_url=result.video_url,
                video_path=video_path,
                generation_time=generation_time,
                estimated_cost=estimated_cost,
                task_id=task.task_id,
                duration_used=duration,
            )
        else:
            return GenerationResult(
                provider=provider_name,
                model_id=model.model_id,
                model_name=model.display_name,
                success=False,
                generation_time=generation_time,
                estimated_cost=0,
                error_message=result.error_message or "Generation failed",
                task_id=task.task_id,
            )

    except Exception as e:
        generation_time = time.time() - start_time
        return GenerationResult(
            provider=provider_name,
            model_id=model.model_id,
            model_name=model.display_name,
            success=False,
            generation_time=generation_time,
            error_message=str(e),
        )


def main():
    st.set_page_config(
        page_title="Video Generation Comparison Tool",
        page_icon="🎬",
        layout="wide",
    )

    st.title("🎬 Video Generation Comparison Tool")
    st.markdown("Compare video generation across multiple AI providers")

    # Initialize session state
    if "results" not in st.session_state:
        st.session_state.results = []
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

    # Sidebar for parameters
    with st.sidebar:
        st.header("Generation Parameters")

        # Generation type
        generation_type_options = {
            "Text to Video": GenerationType.TEXT_TO_VIDEO,
            "Image to Video": GenerationType.IMAGE_TO_VIDEO,
        }
        generation_type_name = st.selectbox(
            "Generation Type",
            options=list(generation_type_options.keys()),
            index=0,
        )
        generation_type = generation_type_options[generation_type_name]

        st.divider()

        # Duration Range
        available_durations = get_available_durations(generation_type)
        if available_durations:
            min_dur = min(available_durations)
            max_dur = max(available_durations)

            if min_dur == max_dur:
                duration_range = (min_dur, max_dur)
                st.info(f"Duration: {min_dur}s (only option)")
            else:
                duration_range = st.slider(
                    "Duration Range (seconds)",
                    min_value=min_dur,
                    max_value=max_dur,
                    value=(min_dur, max_dur),
                    help="Models supporting any duration in this range will be available"
                )
        else:
            duration_range = (5, 10)

        # Resolution
        available_resolutions = get_available_resolutions(generation_type)
        resolution = st.selectbox(
            "Resolution",
            options=available_resolutions,
            index=0 if available_resolutions else None,
        )

        # Aspect Ratio
        available_aspect_ratios = get_available_aspect_ratios(generation_type)
        if available_aspect_ratios:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                options=available_aspect_ratios,
                index=0,
            )
        else:
            aspect_ratio = "16:9"
            st.info("Aspect ratio determined by input image")

        st.divider()

        # Mode (for Kling)
        mode = st.selectbox(
            "Mode (Kling only)",
            options=["std", "pro"],
            index=0,
            help="Standard (faster) or Pro (higher quality)"
        )

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Input")

        # Prompt input
        prompt = st.text_area(
            "Prompt",
            value="一只可爱的橘猫在阳光下慢慢打哈欠，慢镜头，电影级画质",
            height=100,
            help="Describe the video you want to generate (max 2000 characters)",
        )

        # Image URL for I2V
        image_url = None
        if generation_type == GenerationType.IMAGE_TO_VIDEO:
            image_url = st.text_input(
                "Image URL",
                placeholder="https://example.com/image.jpg",
                help="URL of the first frame image",
            )
            if image_url:
                try:
                    st.image(image_url, caption="Input Image", width=300)
                except:
                    st.warning("Could not load image preview")

    with col2:
        st.subheader("Select Models")

        # Filter compatible models
        compatible_models = filter_models(
            generation_type=generation_type,
            duration_range=duration_range,
            resolution=resolution,
            aspect_ratio=aspect_ratio if available_aspect_ratios else None,
        )

        # Group by provider
        selected_models: List[ModelCapability] = []

        for provider_id, provider_name in PROVIDER_NAMES.items():
            provider_models = [m for m in compatible_models if m.provider == provider_id]
            all_provider_models = get_models_by_provider(provider_id)

            with st.expander(f"{provider_name} ({len(provider_models)}/{len(all_provider_models)} models available)", expanded=True):
                for model in all_provider_models:
                    is_compatible, reason = check_model_compatibility(
                        model,
                        generation_type=generation_type,
                        duration_range=duration_range,
                        resolution=resolution,
                        aspect_ratio=aspect_ratio if available_aspect_ratios else None,
                    )

                    if is_compatible:
                        if st.checkbox(
                            f"{model.display_name}",
                            key=f"model_{provider_id}_{model.model_id}",
                            help=model.description,
                        ):
                            selected_models.append(model)
                    else:
                        st.checkbox(
                            f"~~{model.display_name}~~ ({reason})",
                            key=f"model_{provider_id}_{model.model_id}",
                            disabled=True,
                        )

        st.info(f"Selected: {len(selected_models)} models")

    st.divider()

    # Generate button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn2:
        generate_button = st.button(
            "🚀 Generate Videos",
            type="primary",
            disabled=len(selected_models) == 0 or st.session_state.is_generating,
            use_container_width=True,
        )

    # Generation logic
    if generate_button and selected_models:
        st.session_state.is_generating = True
        st.session_state.results = []

        # Validate inputs
        if generation_type == GenerationType.IMAGE_TO_VIDEO and not image_url:
            st.error("Please provide an image URL for Image-to-Video generation")
            st.session_state.is_generating = False
        else:
            progress_container = st.container()

            with progress_container:
                st.subheader("Generation Progress")

                overall_progress = st.progress(0)
                status_text = st.empty()

                results = []

                for i, model in enumerate(selected_models):
                    status_text.text(f"Generating with {model.display_name} ({i+1}/{len(selected_models)})...")

                    result = generate_video(
                        provider_name=model.provider,
                        model=model,
                        generation_type=generation_type,
                        prompt=prompt,
                        duration_range=duration_range,
                        resolution=resolution,
                        aspect_ratio=aspect_ratio,
                        image_url=image_url,
                        mode=mode,
                    )

                    results.append(result)
                    overall_progress.progress((i + 1) / len(selected_models))

                status_text.text("All generations completed!")
                st.session_state.results = results
                st.session_state.is_generating = False

    # Display results
    if st.session_state.results:
        st.divider()
        st.header("Results")

        # Summary metrics
        successful = [r for r in st.session_state.results if r.success]
        failed = [r for r in st.session_state.results if not r.success]

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Total", len(st.session_state.results))
        with col_m2:
            st.metric("Successful", len(successful))
        with col_m3:
            st.metric("Failed", len(failed))
        with col_m4:
            total_cost = sum(r.estimated_cost for r in successful)
            st.metric("Est. Cost", f"¥{total_cost:.2f}")

        st.divider()

        # Video comparison grid
        if successful:
            st.subheader("Video Comparison")

            # Calculate columns based on number of results
            num_cols = min(len(successful), 3)
            cols = st.columns(num_cols)

            for i, result in enumerate(successful):
                with cols[i % num_cols]:
                    st.markdown(f"**{PROVIDER_NAMES.get(result.provider, result.provider)}**")
                    st.markdown(f"*{result.model_name}*")

                    if result.video_path and os.path.exists(result.video_path):
                        st.video(result.video_path)
                    elif result.video_url:
                        st.video(result.video_url)

                    st.markdown(f"""
                    - **Duration:** {result.duration_used}s
                    - **Gen Time:** {result.generation_time:.1f}s
                    - **Est. Cost:** ¥{result.estimated_cost:.2f}
                    """)

                    if result.video_path:
                        with open(result.video_path, "rb") as f:
                            st.download_button(
                                label="Download",
                                data=f,
                                file_name=os.path.basename(result.video_path),
                                mime="video/mp4",
                                key=f"download_{result.provider}_{result.model_id}",
                            )

        # Failed results
        if failed:
            st.subheader("Failed Generations")
            for result in failed:
                st.error(f"**{result.model_name}** ({result.provider}): {result.error_message}")

        # Download all button
        if successful and len(successful) > 1:
            st.divider()
            st.subheader("Bulk Download")

            # Create a zip file with all videos
            import zipfile
            import io

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for result in successful:
                    if result.video_path and os.path.exists(result.video_path):
                        zf.write(result.video_path, os.path.basename(result.video_path))

            zip_buffer.seek(0)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📦 Download All Videos (ZIP)",
                data=zip_buffer,
                file_name=f"video_comparison_{timestamp}.zip",
                mime="application/zip",
            )

        # Results table
        st.divider()
        st.subheader("Detailed Results")

        import pandas as pd

        df_data = []
        for result in st.session_state.results:
            df_data.append({
                "Provider": PROVIDER_NAMES.get(result.provider, result.provider),
                "Model": result.model_name,
                "Status": "✅ Success" if result.success else "❌ Failed",
                "Duration": f"{result.duration_used}s" if result.duration_used else "-",
                "Gen Time (s)": f"{result.generation_time:.1f}",
                "Est. Cost (¥)": f"{result.estimated_cost:.2f}" if result.success else "-",
                "Error": result.error_message or "-",
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
