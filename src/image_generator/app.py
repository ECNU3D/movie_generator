"""
Image Generation Test App

Streamlit app for testing image generation features:
1. Text-to-Image generation
2. Frame generation (first/last frame for video)
3. Character design:
   - Front view generation
   - Three-view generation (single image / separate images / turnaround sheet)
4. Image editing (multi-image fusion, style transfer)
5. Scene composition (composite 1-3 characters into scenes)
"""

import os
import sys
import streamlit as st
from pathlib import Path
import requests
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.providers.image import (
    TongyiImageProvider,
    TONGYI_IMAGE_MODELS,
    JiMengImageProvider,
    JIMENG_IMAGE_MODELS,
    CharacterViewMode,
    CharacterRef,
    ImageTaskStatus,
)


def get_provider_name() -> str:
    """Get the currently selected provider name."""
    return st.session_state.get("provider_name", "tongyi")


def init_provider():
    """Initialize the selected image provider."""
    provider_name = get_provider_name()
    cache_key = f"provider_{provider_name}"

    if cache_key not in st.session_state:
        if provider_name == "jimeng":
            provider = JiMengImageProvider()
        else:
            provider = TongyiImageProvider()
        provider.initialize()
        st.session_state[cache_key] = provider

    return st.session_state[cache_key]


def get_current_models() -> dict:
    """Get models dict for the current provider."""
    if get_provider_name() == "jimeng":
        return JIMENG_IMAGE_MODELS
    return TONGYI_IMAGE_MODELS


def is_jimeng() -> bool:
    """Check if JiMeng provider is currently selected."""
    return get_provider_name() == "jimeng"


def download_image(url: str, save_dir: str = "./output/images") -> str:
    """Download image from URL."""
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.png"
    filepath = os.path.join(save_dir, filename)

    response = requests.get(url)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(response.content)

    return filepath


def text_to_image_page():
    """Text-to-Image generation page."""
    st.header("🎨 文生图 Text-to-Image")

    all_models = get_current_models()

    # Model selection - for Tongyi filter t2i only, for JiMeng all models are t2i
    if is_jimeng():
        t2i_models = all_models
    else:
        t2i_models = {k: v for k, v in all_models.items() if v.model_type == "t2i"}

    model = st.selectbox(
        "选择模型",
        options=list(t2i_models.keys()),
        format_func=lambda x: f"{x} - {t2i_models[x].description}",
    )

    # Get supported sizes for selected model
    model_info = all_models[model]
    sizes = model_info.sizes

    col1, col2 = st.columns(2)
    with col1:
        size = st.selectbox("图像尺寸", options=sizes, index=0)
    with col2:
        n = st.slider("生成数量", min_value=1, max_value=4, value=1)

    # Prompt input
    prompt = st.text_area(
        "提示词 (Prompt)",
        placeholder="描述你想生成的图像...",
        height=100,
    )

    # Provider-specific options
    negative_prompt = None
    extra_kwargs = {}

    if is_jimeng():
        col1, col2 = st.columns(2)
        with col1:
            optimize = st.selectbox(
                "提示词优化",
                options=["standard", "fast", "无"],
                format_func=lambda x: {"standard": "标准优化", "fast": "快速优化", "无": "不优化"}.get(x, x),
            )
            if optimize != "无":
                extra_kwargs["optimize_prompt"] = optimize
        with col2:
            watermark = st.checkbox("添加水印", value=False)
    else:
        negative_prompt = st.text_input(
            "反向提示词 (Negative Prompt)",
            placeholder="描述不想出现的内容...",
        )
        col1, col2 = st.columns(2)
        with col1:
            prompt_extend = st.checkbox("智能提示词增强", value=True)
            extra_kwargs["prompt_extend"] = prompt_extend
        with col2:
            watermark = st.checkbox("添加水印", value=False)

    if st.button("🚀 生成图像", type="primary", disabled=not prompt):
        provider = init_provider()

        with st.spinner("正在生成图像..."):
            try:
                task = provider.text_to_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt if negative_prompt else None,
                    size=size,
                    n=n,
                    model=model,
                    watermark=watermark,
                    **extra_kwargs,
                )

                if task.is_successful():
                    st.success(f"✅ 生成成功！共 {len(task.image_urls)} 张图像")

                    cols = st.columns(min(len(task.image_urls), 4))
                    for i, url in enumerate(task.image_urls):
                        with cols[i % 4]:
                            st.image(url, caption=f"图像 {i+1}")
                            if st.button(f"下载图像 {i+1}", key=f"dl_{i}"):
                                filepath = download_image(url)
                                st.success(f"已保存到: {filepath}")

                    st.session_state.last_generated = task.image_urls
                else:
                    st.error(f"❌ 生成失败: {task.error_message}")

            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")


def frame_generation_page():
    """Frame generation page for video first/last frames."""
    st.header("🎬 视频帧生成 Frame Generation")

    st.markdown("""
    生成视频的首帧或尾帧图像，可用于图生视频。
    - **纯文本模式**: 根据场景描述生成帧
    - **角色参考模式**: 基于角色设定图生成保持一致性的帧
    """)

    # Mode selection
    mode = st.radio(
        "生成模式",
        options=["纯文本", "角色参考"],
        horizontal=True,
    )

    # Size selection
    sizes = ["1664*928", "1280*720", "1920*1080", "928*1664"]
    size_labels = {
        "1664*928": "1664x928 (16:9 通义)",
        "1280*720": "1280x720 (16:9 标准)",
        "1920*1080": "1920x1080 (16:9 全高清)",
        "928*1664": "928x1664 (9:16 竖屏)",
    }
    size = st.selectbox(
        "帧尺寸",
        options=sizes,
        format_func=lambda x: size_labels.get(x, x),
    )

    # Scene prompt
    prompt = st.text_area(
        "场景描述",
        placeholder="描述这一帧的场景内容...\n例如: 一个年轻女子站在樱花树下，微风吹过，花瓣飘落",
        height=100,
    )

    # Style
    style = st.selectbox(
        "视觉风格",
        options=["cinematic", "realistic", "anime", "artistic", "dramatic"],
        format_func=lambda x: {
            "cinematic": "电影风格",
            "realistic": "写实风格",
            "anime": "动漫风格",
            "artistic": "艺术风格",
            "dramatic": "戏剧风格",
        }.get(x, x),
    )

    # Character reference (if mode is character reference)
    character_ref = None
    if mode == "角色参考":
        st.subheader("角色参考图")
        ref_source = st.radio(
            "参考图来源",
            options=["上传图片", "输入URL", "使用上次生成"],
            horizontal=True,
        )

        if ref_source == "上传图片":
            uploaded = st.file_uploader("上传角色图片", type=["png", "jpg", "jpeg"])
            if uploaded:
                # Save temporarily
                temp_path = f"./output/temp_{uploaded.name}"
                os.makedirs("./output", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded.getvalue())
                character_ref = temp_path
                st.image(uploaded, width=200)

        elif ref_source == "输入URL":
            character_ref = st.text_input("角色图片URL")
            if character_ref:
                st.image(character_ref, width=200)

        elif ref_source == "使用上次生成":
            if "last_generated" in st.session_state and st.session_state.last_generated:
                character_ref = st.selectbox(
                    "选择图片",
                    options=st.session_state.last_generated,
                )
                if character_ref:
                    st.image(character_ref, width=200)
            else:
                st.warning("没有上次生成的图片")

    if st.button("🎬 生成帧", type="primary", disabled=not prompt):
        provider = init_provider()

        with st.spinner("正在生成帧图像..."):
            try:
                if character_ref:
                    task = provider.generate_frame_with_character(
                        prompt=prompt,
                        character_reference=character_ref,
                        size=size,
                        style=style,
                    )
                else:
                    task = provider.generate_frame(
                        prompt=prompt,
                        size=size,
                        style=style,
                    )

                if task.is_successful():
                    st.success("✅ 帧生成成功！")
                    st.image(task.image_url, caption="生成的帧")

                    if st.button("💾 下载帧"):
                        filepath = download_image(task.image_url, "./output/frames")
                        st.success(f"已保存到: {filepath}")

                    st.session_state.last_frame = task.image_url
                else:
                    st.error(f"❌ 生成失败: {task.error_message}")

            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")


def character_design_page():
    """Character design page."""
    st.header("👤 角色设计 Character Design")

    tabs = st.tabs(["1. 正面图生成", "2. 三视图生成"])

    with tabs[0]:
        st.subheader("生成角色正面图")

        # Character description
        char_desc = st.text_area(
            "角色描述",
            placeholder="详细描述角色的外貌特征...\n例如: 一位20岁左右的亚洲女性，长黑发，穿着白色连衣裙，温柔的眼神",
            height=150,
        )

        col1, col2 = st.columns(2)
        with col1:
            style = st.selectbox(
                "艺术风格",
                options=["realistic", "anime", "cartoon", "3d", "watercolor"],
                format_func=lambda x: {
                    "realistic": "写实风格",
                    "anime": "动漫风格",
                    "cartoon": "卡通风格",
                    "3d": "3D渲染",
                    "watercolor": "水彩风格",
                }.get(x, x),
            )
        with col2:
            size = st.selectbox(
                "图像尺寸",
                options=["1328*1328", "1024*1024", "1104*1472"],
                format_func=lambda x: {
                    "1328*1328": "1328x1328 (1:1 方形)",
                    "1024*1024": "1024x1024 (1:1 方形)",
                    "1104*1472": "1104x1472 (3:4 竖版)",
                }.get(x, x),
            )

        if st.button("🎨 生成正面图", type="primary", disabled=not char_desc):
            provider = init_provider()

            with st.spinner("正在生成角色正面图..."):
                try:
                    task = provider.generate_character_front_view(
                        character_description=char_desc,
                        style=style,
                        size=size,
                    )

                    if task.is_successful():
                        st.success("✅ 角色正面图生成成功！")
                        st.image(task.image_url, caption="角色正面图")

                        # Store for three-view generation
                        st.session_state.character_front = task.image_url
                        st.session_state.character_desc = char_desc
                        st.session_state.character_style = style

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 下载图片"):
                                filepath = download_image(task.image_url, "./output/characters")
                                st.success(f"已保存到: {filepath}")
                        with col2:
                            st.info("✅ 可以继续生成三视图")

                    else:
                        st.error(f"❌ 生成失败: {task.error_message}")

                except Exception as e:
                    st.error(f"❌ 错误: {str(e)}")

    with tabs[1]:
        st.subheader("生成角色三视图")

        # Check if we have a front view
        if "character_front" not in st.session_state:
            st.warning("请先生成角色正面图，或上传/输入正面图URL")

            ref_source = st.radio(
                "正面图来源",
                options=["上传图片", "输入URL"],
                horizontal=True,
            )

            if ref_source == "上传图片":
                uploaded = st.file_uploader("上传角色正面图", type=["png", "jpg", "jpeg"])
                if uploaded:
                    temp_path = f"./output/temp_front_{uploaded.name}"
                    os.makedirs("./output", exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded.getvalue())
                    st.session_state.character_front = temp_path
                    st.image(uploaded, width=300)
            else:
                url = st.text_input("正面图URL")
                if url:
                    st.session_state.character_front = url
                    st.image(url, width=300)

            char_desc = st.text_area(
                "角色描述 (用于保持一致性)",
                placeholder="描述角色特征...",
                height=100,
            )
            if char_desc:
                st.session_state.character_desc = char_desc
        else:
            st.image(st.session_state.character_front, width=300, caption="当前角色正面图")

        # View mode selection
        st.markdown("### 三视图模式")
        view_mode = st.radio(
            "选择生成模式",
            options=[
                CharacterViewMode.SINGLE_IMAGE_THREE_VIEWS,
                CharacterViewMode.THREE_SEPARATE_IMAGES,
                CharacterViewMode.TURNAROUND_SHEET,
            ],
            format_func=lambda x: {
                CharacterViewMode.SINGLE_IMAGE_THREE_VIEWS: "🖼️ 单张三视图 - 一张图包含正面/侧面/背面",
                CharacterViewMode.THREE_SEPARATE_IMAGES: "📸 三张独立图 - 分别生成正面、侧面、背面",
                CharacterViewMode.TURNAROUND_SHEET: "📐 角色转面图 - 专业游戏/动画设定图",
            }.get(x, str(x)),
            horizontal=False,
        )

        # Size for output
        if view_mode == CharacterViewMode.SINGLE_IMAGE_THREE_VIEWS:
            size_options = ["1664*928", "1920*1080"]
        elif view_mode == CharacterViewMode.TURNAROUND_SHEET:
            size_options = ["1664*928", "1920*1080", "2048*1024"]
        else:
            size_options = ["1024*1024", "1328*1328"]

        output_size = st.selectbox("输出尺寸", options=size_options)

        if st.button(
            "🎭 生成三视图",
            type="primary",
            disabled="character_front" not in st.session_state,
        ):
            provider = init_provider()

            with st.spinner("正在生成角色三视图..."):
                try:
                    task = provider.generate_character_views(
                        front_image_url=st.session_state.character_front,
                        character_description=st.session_state.get("character_desc", ""),
                        mode=view_mode,
                        style=st.session_state.get("character_style", "realistic"),
                        size=output_size,
                    )

                    if task.is_successful():
                        st.success(f"✅ 三视图生成成功！共 {len(task.image_urls)} 张图像")

                        if view_mode == CharacterViewMode.THREE_SEPARATE_IMAGES:
                            cols = st.columns(3)
                            labels = ["侧面", "正面", "背面"]
                            for i, url in enumerate(task.image_urls):
                                with cols[i % 3]:
                                    st.image(url, caption=labels[i] if i < 3 else f"图{i+1}")
                        else:
                            st.image(task.image_url, caption="角色设定图")

                        st.session_state.character_views = task.image_urls

                        if st.button("💾 下载全部"):
                            for i, url in enumerate(task.image_urls):
                                filepath = download_image(url, "./output/characters")
                                st.success(f"已保存: {filepath}")

                    else:
                        st.error(f"❌ 生成失败: {task.error_message}")

                except Exception as e:
                    st.error(f"❌ 错误: {str(e)}")


def image_editing_page():
    """Image editing page."""
    st.header("✏️ 图像编辑 Image Editing")

    st.markdown("""
    使用AI编辑图像：
    - 修改图像内容
    - 多图融合
    - 风格迁移
    """)

    # Image input - JiMeng supports up to 14, Tongyi up to 3
    max_images = 14 if is_jimeng() else 3
    st.subheader(f"输入图像 (最多{max_images}张)")

    images = []
    num_slots = min(max_images, 6)  # Show up to 6 slots in UI
    slot_cols = st.columns(min(num_slots, 3))

    for i in range(num_slots):
        with slot_cols[i % 3]:
            st.markdown(f"**图像 {i+1}**")
            source = st.radio(
                f"来源",
                options=["无", "上传", "URL"],
                key=f"img_source_{i}",
                horizontal=True,
            )

            if source == "上传":
                uploaded = st.file_uploader(f"上传图{i+1}", type=["png", "jpg", "jpeg"], key=f"upload_{i}")
                if uploaded:
                    temp_path = f"./output/temp_edit_{i}_{uploaded.name}"
                    os.makedirs("./output", exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded.getvalue())
                    images.append(temp_path)
                    st.image(uploaded, width=150)

            elif source == "URL":
                url = st.text_input(f"URL", key=f"url_{i}")
                if url:
                    images.append(url)
                    st.image(url, width=150)

    # Edit model - for JiMeng all models support editing, for Tongyi filter edit type
    all_models = get_current_models()
    if is_jimeng():
        edit_models = all_models
    else:
        edit_models = {k: v for k, v in all_models.items() if v.model_type == "edit"}
    model = st.selectbox(
        "编辑模型",
        options=list(edit_models.keys()),
        format_func=lambda x: f"{x} - {edit_models[x].description}",
    )

    # Edit prompt
    prompt = st.text_area(
        "编辑指令",
        placeholder="描述如何编辑图像...\n例如: 把图1中的女生的衣服换成图2中的款式",
        height=100,
    )

    col1, col2 = st.columns(2)
    with col1:
        n = st.slider("输出数量", min_value=1, max_value=4, value=1)
    with col2:
        size = st.text_input("输出尺寸 (可选)", placeholder="如: 1024*1024")

    if st.button("✨ 编辑图像", type="primary", disabled=not images or not prompt):
        provider = init_provider()

        with st.spinner("正在编辑图像..."):
            try:
                task = provider.edit_image(
                    images=images,
                    prompt=prompt,
                    size=size if size else None,
                    n=n,
                    model=model,
                )

                if task.is_successful():
                    st.success(f"✅ 编辑成功！共 {len(task.image_urls)} 张图像")

                    cols = st.columns(min(len(task.image_urls), 4))
                    for i, url in enumerate(task.image_urls):
                        with cols[i % 4]:
                            st.image(url, caption=f"结果 {i+1}")

                    st.session_state.last_generated = task.image_urls
                else:
                    st.error(f"❌ 编辑失败: {task.error_message}")

            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")


def scene_composition_page():
    """Scene composition page - composite characters into scenes."""
    st.header("🎭 场景合成 Scene Composition")

    max_chars = 14 if is_jimeng() else 3
    st.markdown(f"""
    将角色合成到指定场景中，保持角色外貌一致性。
    - 每个角色需要一张**正面参考图**
    - 当前 Provider 最多支持 **{max_chars}** 个角色
    - 角色数较少时可额外添加背景参考图
    """)

    # Number of characters
    char_options = list(range(1, min(max_chars, 6) + 1))
    num_chars = st.radio(
        "角色数量",
        options=char_options,
        horizontal=True,
    )

    # Character slots
    st.subheader("角色设定")
    characters_data = []

    for i in range(num_chars):
        with st.expander(f"角色 {i+1}", expanded=True):
            col_name, col_pos = st.columns(2)
            with col_name:
                name = st.text_input(
                    "角色名称",
                    value=f"角色{i+1}",
                    key=f"sc_name_{i}",
                )
            with col_pos:
                position = st.selectbox(
                    "位置",
                    options=["", "左侧", "中间", "右侧", "画面中央"],
                    key=f"sc_pos_{i}",
                )

            action = st.text_input(
                "动作描述",
                placeholder="例如：微笑着看向镜头、正在递给对方一本书...",
                key=f"sc_action_{i}",
            )

            # Image source
            ref_source = st.radio(
                "参考图来源",
                options=["上传图片", "输入URL", "使用之前的角色设计"],
                horizontal=True,
                key=f"sc_source_{i}",
            )

            image_url = None
            if ref_source == "上传图片":
                uploaded = st.file_uploader(
                    "上传正面参考图",
                    type=["png", "jpg", "jpeg"],
                    key=f"sc_upload_{i}",
                )
                if uploaded:
                    temp_path = f"./output/temp_scene_char_{i}_{uploaded.name}"
                    os.makedirs("./output", exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded.getvalue())
                    image_url = temp_path
                    st.image(uploaded, width=150)

            elif ref_source == "输入URL":
                image_url = st.text_input(
                    "角色正面图URL",
                    key=f"sc_url_{i}",
                )
                if image_url:
                    st.image(image_url, width=150)

            elif ref_source == "使用之前的角色设计":
                prev_images = []
                if "character_front" in st.session_state:
                    prev_images.append(st.session_state.character_front)
                if "last_generated" in st.session_state:
                    prev_images.extend(st.session_state.last_generated)
                if prev_images:
                    image_url = st.selectbox(
                        "选择图片",
                        options=prev_images,
                        key=f"sc_prev_{i}",
                    )
                    if image_url:
                        st.image(image_url, width=150)
                else:
                    st.warning("没有可用的之前生成的图片")

            characters_data.append({
                "name": name,
                "image_url": image_url,
                "action": action,
                "position": position,
            })

    # Scene description
    st.subheader("场景设定")
    scene_description = st.text_area(
        "场景描述",
        placeholder="描述场景的环境、氛围、光线等...\n例如：安静的图书馆内，背景是整齐的书架，温暖的灯光",
        height=100,
    )

    # Background image (only when characters <= 2)
    background_image = None
    if num_chars <= 2:
        use_bg = st.checkbox("添加背景参考图")
        if use_bg:
            bg_source = st.radio(
                "背景图来源",
                options=["上传", "URL"],
                horizontal=True,
                key="sc_bg_source",
            )
            if bg_source == "上传":
                bg_uploaded = st.file_uploader(
                    "上传背景图",
                    type=["png", "jpg", "jpeg"],
                    key="sc_bg_upload",
                )
                if bg_uploaded:
                    bg_path = f"./output/temp_scene_bg_{bg_uploaded.name}"
                    os.makedirs("./output", exist_ok=True)
                    with open(bg_path, "wb") as f:
                        f.write(bg_uploaded.getvalue())
                    background_image = bg_path
                    st.image(bg_uploaded, width=200)
            else:
                background_image = st.text_input("背景图URL", key="sc_bg_url")
                if background_image:
                    st.image(background_image, width=200)

    # Generation settings
    st.subheader("生成设置")
    col1, col2, col3 = st.columns(3)

    with col1:
        all_models = get_current_models()
        if is_jimeng():
            sc_models = all_models
        else:
            sc_models = {k: v for k, v in all_models.items() if v.model_type == "edit"}
        sc_model_keys = list(sc_models.keys())
        default_idx = 0
        if "qwen-image-edit-max" in sc_models:
            default_idx = sc_model_keys.index("qwen-image-edit-max")
        model = st.selectbox(
            "模型",
            options=sc_model_keys,
            index=default_idx,
            format_func=lambda x: f"{x}",
            key="sc_model",
        )
    with col2:
        if is_jimeng():
            sc_sizes = all_models[model].sizes
        else:
            sc_sizes = ["1664*928", "1280*720", "1024*1024", "928*1664"]
        size = st.selectbox(
            "输出尺寸",
            options=sc_sizes,
            format_func=lambda x: {
                "1664*928": "1664x928 (16:9)",
                "1280*720": "1280x720 (16:9)",
                "1024*1024": "1024x1024 (1:1)",
                "928*1664": "928x1664 (9:16)",
            }.get(x, x),
            key="sc_size",
        )
    with col3:
        n = st.slider("生成数量", min_value=1, max_value=4, value=2, key="sc_n")

    style = st.selectbox(
        "视觉风格",
        options=["cinematic", "realistic", "anime", "artistic", "dramatic"],
        format_func=lambda x: {
            "cinematic": "电影风格",
            "realistic": "写实风格",
            "anime": "动漫风格",
            "artistic": "艺术风格",
            "dramatic": "戏剧风格",
        }.get(x, x),
        key="sc_style",
    )

    # Validate and generate
    all_chars_ready = all(d["image_url"] for d in characters_data)
    can_generate = all_chars_ready and scene_description

    if not all_chars_ready:
        st.warning("请为每个角色提供参考图片")

    if st.button("🎭 合成场景", type="primary", disabled=not can_generate):
        provider = init_provider()

        # Build CharacterRef list
        characters = []
        for d in characters_data:
            characters.append(CharacterRef(
                name=d["name"],
                image_url=d["image_url"],
                action=d["action"],
                position=d["position"],
            ))

        with st.spinner("正在合成场景...（可能需要较长时间）"):
            try:
                task = provider.composite_character_scene(
                    characters=characters,
                    scene_description=scene_description,
                    style=style,
                    size=size,
                    background_image=background_image,
                    n=n,
                    model=model,
                )

                if task.is_successful():
                    st.success(f"✅ 场景合成成功！共 {len(task.image_urls)} 张图像")

                    cols = st.columns(min(len(task.image_urls), 4))
                    for i, url in enumerate(task.image_urls):
                        with cols[i % 4]:
                            st.image(url, caption=f"场景 {i+1}")

                    st.session_state.last_generated = task.image_urls

                    # Download all
                    if st.button("💾 下载全部场景图", key="sc_download"):
                        for i, url in enumerate(task.image_urls):
                            filepath = download_image(url, "./output/scenes")
                            st.success(f"已保存: {filepath}")
                else:
                    st.error(f"❌ 合成失败: {task.error_message}")

            except ValueError as e:
                st.error(f"❌ 参数错误: {str(e)}")
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")


def main():
    st.set_page_config(
        page_title="AI 图像生成测试",
        page_icon="🎨",
        layout="wide",
    )

    st.title("🎨 AI 图像生成测试")
    st.markdown("测试图像生成 Provider 的各项功能")

    # Sidebar - provider selection and settings
    with st.sidebar:
        st.header("⚙️ 设置")

        # Provider selector
        provider_name = st.selectbox(
            "图像 Provider",
            options=["tongyi", "jimeng"],
            format_func=lambda x: {
                "tongyi": "通义 (Tongyi)",
                "jimeng": "即梦 Seedream (JiMeng)",
            }.get(x, x),
            key="provider_name",
        )

        if st.button("🔌 测试连接"):
            provider = init_provider()
            result = provider.test_connection()
            if result["success"]:
                st.success("✅ 连接成功")
            else:
                st.error(f"❌ {result.get('error', '连接失败')}")

        st.divider()
        st.markdown("### 可用模型")
        current_models = get_current_models()
        for name, info in current_models.items():
            with st.expander(name):
                st.markdown(f"**{info.description}**")
                st.markdown(f"- 类型: {info.model_type}")
                if hasattr(info, "sync_supported"):
                    st.markdown(f"- 同步: {'✅' if info.sync_supported else '❌'}")
                if hasattr(info, "max_input_images"):
                    st.markdown(f"- 最大输入图片: {info.max_input_images}")

    # Main content - tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎨 文生图",
        "🎬 帧生成",
        "👤 角色设计",
        "✏️ 图像编辑",
        "🎭 场景合成",
    ])

    with tab1:
        text_to_image_page()

    with tab2:
        frame_generation_page()

    with tab3:
        character_design_page()

    with tab4:
        image_editing_page()

    with tab5:
        scene_composition_page()


if __name__ == "__main__":
    main()
