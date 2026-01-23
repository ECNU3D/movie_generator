"""
Story Generator - Streamlit App

AI驱动的故事剧本生成器UI
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

import streamlit as st

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from story_generator.models import (
    Project, Character, Episode, Shot, MajorEvent, EditHistory,
    SHOT_TYPE_NAMES, CAMERA_MOVEMENT_NAMES, GENRE_NAMES
)
from story_generator.database import Database
from story_generator.gemini_client import GeminiClient, GeminiConfig
import json


# ==================== 初始化 ====================

def init_database() -> Database:
    """初始化数据库"""
    db_path = Path(__file__).parent.parent.parent / "data" / "story_generator.db"
    return Database(str(db_path))


def init_gemini_client() -> Optional[GeminiClient]:
    """初始化Gemini客户端"""
    # 从文件或环境变量获取API key
    api_key = None

    # 尝试从文件读取
    key_file = Path(__file__).parent.parent.parent / "gemini_api_key"
    if key_file.exists():
        api_key = key_file.read_text().strip()

    # 尝试从环境变量
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return None

    config = GeminiConfig(api_key=api_key)
    return GeminiClient(config)


# ==================== Session State ====================

def init_session_state():
    """初始化session state"""
    if "db" not in st.session_state:
        st.session_state.db = init_database()

    if "gemini" not in st.session_state:
        st.session_state.gemini = init_gemini_client()

    if "current_project_id" not in st.session_state:
        st.session_state.current_project_id = None

    if "current_episode_id" not in st.session_state:
        st.session_state.current_episode_id = None

    if "page" not in st.session_state:
        st.session_state.page = "projects"


def get_db() -> Database:
    return st.session_state.db


def get_gemini() -> Optional[GeminiClient]:
    return st.session_state.gemini


# ==================== 页面: 项目列表 ====================

def page_projects():
    """项目列表页面"""
    st.header("📁 我的项目")

    # 检查Gemini连接
    gemini = get_gemini()
    if not gemini:
        st.error("⚠️ 未配置Gemini API Key。请在项目根目录创建 `gemini_api_key` 文件或设置 `GEMINI_API_KEY` 环境变量。")
        return

    db = get_db()
    projects = db.list_projects()

    # 创建新项目按钮
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ 新建项目", type="primary", use_container_width=True):
            st.session_state.page = "new_project"
            st.rerun()

    if not projects:
        st.info("暂无项目，点击上方按钮创建新项目")
        return

    # 项目列表
    for project in projects:
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                st.markdown(f"### {project.name}")
                st.caption(f"{GENRE_NAMES.get(project.genre, project.genre)} | {project.num_episodes}集 | 每集{project.episode_duration}秒")
                if project.description:
                    st.text(project.description[:100] + "..." if len(project.description) > 100 else project.description)

            with col2:
                if st.button("打开", key=f"open_{project.id}", use_container_width=True):
                    st.session_state.current_project_id = project.id
                    st.session_state.page = "project_detail"
                    st.rerun()

            with col3:
                if st.button("🗑️", key=f"delete_{project.id}", use_container_width=True):
                    db.delete_project(project.id)
                    st.rerun()

            st.divider()


# ==================== 页面: 新建项目 ====================

def page_new_project():
    """新建项目页面"""
    st.header("✨ 创建新故事")

    gemini = get_gemini()
    db = get_db()

    # 返回按钮
    if st.button("← 返回项目列表"):
        st.session_state.page = "projects"
        st.rerun()

    st.divider()

    # 输入方式选择
    input_mode = st.radio(
        "选择创作方式",
        ["💡 输入故事创意", "🎲 随机生成"],
        horizontal=True
    )

    # 基本设置
    col1, col2 = st.columns(2)

    with col1:
        genre = st.selectbox(
            "故事类型",
            options=list(GENRE_NAMES.keys()),
            format_func=lambda x: GENRE_NAMES[x],
            index=5  # 默认剧情
        )

        num_episodes = st.number_input("集数", min_value=1, max_value=50, value=3)

    with col2:
        style = st.text_input("风格描述", placeholder="如: 温馨治愈、紧张刺激、幽默搞笑...")
        episode_duration = st.number_input("每集时长(秒)", min_value=10, max_value=300, value=60)

    col3, col4 = st.columns(2)
    with col3:
        target_audience = st.text_input("目标受众", placeholder="如: 年轻人、儿童、职场白领...")
    with col4:
        max_video_duration = st.selectbox(
            "最大视频时长(秒)",
            options=[5, 6, 10, 15],
            index=2,  # 默认10秒
            help="单个视频片段的最大时长，用于计算分镜数量"
        )

    # 故事创意输入
    if input_mode == "💡 输入故事创意":
        idea = st.text_area(
            "故事创意",
            height=150,
            placeholder="描述你的故事想法...\n例如: 一个内向的程序员意外获得了读心术，却发现同事们的内心想法和表面完全不同..."
        )
    else:
        # 随机生成
        if st.button("🎲 生成随机创意"):
            with st.spinner("正在生成创意..."):
                idea = gemini.generate_random_story_idea(genre, style)
                st.session_state.random_idea = idea

        idea = st.text_area(
            "故事创意",
            value=st.session_state.get("random_idea", ""),
            height=150,
            placeholder="点击上方按钮生成随机创意，或直接输入..."
        )

    st.divider()

    # 生成按钮
    if st.button("🚀 生成故事大纲", type="primary", disabled=not idea):
        with st.spinner("AI正在创作故事大纲..."):
            try:
                result = gemini.generate_story_outline(
                    idea=idea,
                    genre=genre,
                    style=style,
                    num_episodes=num_episodes,
                    episode_duration=episode_duration,
                    target_audience=target_audience
                )

                # 创建项目
                project = Project(
                    name=result.get("title", "未命名项目"),
                    description=result.get("synopsis", idea),
                    genre=genre,
                    style=style,
                    target_audience=target_audience,
                    num_episodes=num_episodes,
                    episode_duration=episode_duration,
                    max_video_duration=max_video_duration
                )
                project_id = db.create_project(project)

                # 创建人物
                for char_data in result.get("characters", []):
                    character = Character(
                        project_id=project_id,
                        name=char_data.get("name", ""),
                        age=char_data.get("age", ""),
                        appearance=char_data.get("appearance", ""),
                        personality=char_data.get("personality", ""),
                        background=char_data.get("background", ""),
                        relationships=char_data.get("relationships", ""),
                        visual_description=char_data.get("visual_description", "")
                    )
                    db.create_character(character)

                # 创建剧集
                for ep_data in result.get("episodes", []):
                    episode = Episode(
                        project_id=project_id,
                        episode_number=ep_data.get("episode_number", 1),
                        title=ep_data.get("title", ""),
                        outline=ep_data.get("outline", ""),
                        duration=episode_duration
                    )
                    db.create_episode(episode)

                st.success(f"故事「{project.name}」创建成功！")
                st.session_state.current_project_id = project_id
                st.session_state.page = "project_detail"
                st.rerun()

            except Exception as e:
                st.error(f"生成失败: {e}")


# ==================== 页面: 项目详情 ====================

def page_project_detail():
    """项目详情页面"""
    db = get_db()
    gemini = get_gemini()
    project_id = st.session_state.current_project_id

    if not project_id:
        st.session_state.page = "projects"
        st.rerun()
        return

    project = db.get_project(project_id)
    if not project:
        st.error("项目不存在")
        st.session_state.page = "projects"
        return

    # 顶部导航
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header(f"📖 {project.name}")
    with col2:
        if st.button("← 返回列表"):
            st.session_state.current_project_id = None
            st.session_state.page = "projects"
            st.rerun()

    st.caption(f"{GENRE_NAMES.get(project.genre, project.genre)} | {project.style}")
    st.text(project.description)

    # 选项卡
    tab1, tab2, tab3 = st.tabs(["📺 剧集", "👥 人物", "⚙️ 设置"])

    # ===== 剧集选项卡 =====
    with tab1:
        st.subheader("剧集列表")

        # 待处理的一致性问题提示
        if "pending_issues" in st.session_state and st.session_state.pending_issues:
            issues = st.session_state.pending_issues
            issue_count = len(issues)
            with st.expander(f"⚠️ 有 {issue_count} 个待处理的一致性问题", expanded=False):
                for i, issue in enumerate(issues):
                    severity_icon = "🔴" if issue.get("severity") == "error" else "🟡"
                    issue_type = issue.get("type", "")
                    type_label = "剧集" if issue_type == "episode" else "角色" if issue_type == "character" else issue_type
                    st.markdown(f"{severity_icon} **{type_label}: {issue.get('name')}**")
                    st.markdown(f"  问题: {issue.get('issue')}")
                    st.markdown(f"  建议: {issue.get('suggested_fix')}")

                    # 操作按钮
                    btn_col1, btn_col2 = st.columns(2)

                    with btn_col1:
                        # 自动修复按钮
                        can_auto_fix = issue.get("auto_fixable", False)
                        is_implemented = issue_type == "episode"
                        if can_auto_fix and is_implemented:
                            if st.button(f"🔧 自动修复", key=f"fix_pending_{i}", use_container_width=True):
                                _apply_consistency_fix(gemini, db, project, issue)
                                st.session_state.pending_issues.pop(i)
                                st.rerun()

                    with btn_col2:
                        # 手工已修复按钮
                        if st.button(f"✅ 已手工修复", key=f"manual_fix_{i}", use_container_width=True):
                            st.session_state.pending_issues.pop(i)
                            st.toast(f"已标记「{issue.get('name')}」为已修复")
                            st.rerun()

                    st.divider()

                if st.button("🗑️ 清除所有提示", key="clear_issues"):
                    st.session_state.pending_issues = []
                    st.rerun()

        # 撤销/重做按钮（带详细说明）
        latest_undo = db.get_latest_undoable_edit(project_id)
        latest_redo = db.get_latest_redoable_edit(project_id)

        undo_col, redo_col, history_col = st.columns([2, 2, 2])
        with undo_col:
            undo_label = "↶ 撤销"
            undo_help = "没有可撤销的操作"
            if latest_undo:
                undo_desc = _get_edit_description(latest_undo)
                undo_help = f"撤销: {undo_desc}"
            if st.button(undo_label, disabled=not latest_undo, help=undo_help, use_container_width=True):
                if latest_undo:
                    _perform_undo(db, latest_undo)
                    st.toast(f"已撤销: {_get_edit_description(latest_undo)}")
                    st.rerun()

        with redo_col:
            redo_label = "↷ 重做"
            redo_help = "没有可重做的操作"
            if latest_redo:
                redo_desc = _get_edit_description(latest_redo)
                redo_help = f"重做: {redo_desc}"
            if st.button(redo_label, disabled=not latest_redo, help=redo_help, use_container_width=True):
                if latest_redo:
                    _perform_redo(db, latest_redo)
                    st.toast(f"已重做: {_get_edit_description(latest_redo)}")
                    st.rerun()

        with history_col:
            if st.button("📜 编辑历史", use_container_width=True):
                st.session_state.show_edit_history = not st.session_state.get("show_edit_history", False)
                st.rerun()

        # 显示编辑历史
        if st.session_state.get("show_edit_history", False):
            _show_edit_history(db, project_id)

        st.divider()

        if not project.episodes:
            st.info("暂无剧集")
        else:
            for episode in project.episodes:
                with st.expander(f"第{episode.episode_number}集: {episode.title}", expanded=False):
                    st.markdown(f"**大纲:** {episode.outline}")
                    st.caption(f"目标时长: {episode.duration}秒 | 状态: {episode.status}")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ 编辑大纲", key=f"edit_outline_{episode.id}"):
                            st.session_state.current_episode_id = episode.id
                            st.session_state.page = "edit_episode"
                            st.rerun()

                    with col2:
                        if st.button("📝 编辑分镜", key=f"edit_ep_{episode.id}"):
                            st.session_state.current_episode_id = episode.id
                            st.session_state.page = "storyboard"
                            st.rerun()

                    with col3:
                        if st.button("🎬 生成分镜", key=f"gen_ep_{episode.id}"):
                            st.session_state.current_episode_id = episode.id
                            st.session_state.page = "generate_storyboard"
                            st.rerun()

    # ===== 人物选项卡 =====
    with tab2:
        st.subheader("人物设定")

        if not project.characters:
            st.info("暂无人物设定")
        else:
            for character in project.characters:
                with st.expander(f"👤 {character.name}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**年龄:** {character.age}")
                        st.markdown(f"**性格:** {character.personality}")
                        st.markdown(f"**外貌:** {character.appearance}")
                    with col2:
                        st.markdown(f"**背景:** {character.background}")
                        st.markdown(f"**关系:** {character.relationships}")

                    st.markdown(f"**视觉描述:** {character.visual_description}")

                    if character.major_events:
                        st.markdown("**重大经历:**")
                        for event in character.major_events:
                            st.markdown(f"- 第{event.episode_number}集: {event.description}")

                    if st.button("编辑", key=f"edit_char_{character.id}"):
                        st.session_state.editing_character_id = character.id
                        st.session_state.page = "edit_character"
                        st.rerun()

    # ===== 设置选项卡 =====
    with tab3:
        st.subheader("项目设置")

        with st.form("project_settings"):
            name = st.text_input("项目名称", value=project.name)
            description = st.text_area("故事简介", value=project.description)
            style = st.text_input("风格", value=project.style)

            if st.form_submit_button("保存设置"):
                project.name = name
                project.description = description
                project.style = style
                db.update_project(project)
                st.success("设置已保存")
                st.rerun()


# ==================== 页面: 生成分镜 ====================

def page_generate_storyboard():
    """生成分镜脚本页面"""
    db = get_db()
    gemini = get_gemini()

    episode_id = st.session_state.current_episode_id
    project_id = st.session_state.current_project_id

    if not episode_id or not project_id:
        st.session_state.page = "project_detail"
        st.rerun()
        return

    project = db.get_project(project_id)
    episode = db.get_episode(episode_id)

    if not project or not episode:
        st.error("数据不存在")
        return

    # 返回按钮
    if st.button("← 返回项目"):
        st.session_state.page = "project_detail"
        st.rerun()

    st.header(f"🎬 生成分镜 - 第{episode.episode_number}集")
    st.markdown(f"**{episode.title}**")
    st.text(episode.outline)

    st.divider()

    # 警告如果已有分镜
    if episode.shots:
        st.warning(f"⚠️ 本集已有 {len(episode.shots)} 个镜头。重新生成将覆盖现有分镜。")

    # 分镜密度选择
    import math
    min_shots = math.ceil(episode.duration / project.max_video_duration)

    st.subheader("分镜设置")
    col1, col2 = st.columns(2)

    with col1:
        density_options = {
            "low": f"少 ({min_shots}个镜头)",
            "medium": f"中 ({int(min_shots * 1.5)}个镜头)",
            "high": f"多 ({min_shots * 2}个镜头)",
            "custom": "自定义"
        }
        shot_density = st.selectbox(
            "分镜密度",
            options=list(density_options.keys()),
            format_func=lambda x: density_options[x],
            index=1,  # 默认中等
            help=f"最少需要{min_shots}个镜头（每集{episode.duration}秒 ÷ 每镜头最长{project.max_video_duration}秒）"
        )

    with col2:
        custom_shot_count = None
        if shot_density == "custom":
            custom_shot_count = st.number_input(
                "自定义镜头数",
                min_value=min_shots,
                max_value=min_shots * 5,
                value=min_shots * 2
            )
        else:
            st.info(f"每镜头平均 {episode.duration / (min_shots if shot_density == 'low' else int(min_shots * 1.5) if shot_density == 'medium' else min_shots * 2):.1f} 秒")

    # 人物上下文
    character_context = project.get_all_characters_context(up_to_episode=episode.episode_number - 1)

    with st.expander("查看人物知识库", expanded=False):
        st.text(character_context if character_context else "暂无人物设定")

    if st.button("🚀 生成分镜脚本", type="primary"):
        with st.spinner("AI正在生成分镜脚本..."):
            try:
                shots_data = gemini.generate_storyboard(
                    episode=episode,
                    project=project,
                    character_context=character_context,
                    shot_density=shot_density,
                    custom_shot_count=custom_shot_count
                )

                # 删除旧镜头
                db.delete_shots_by_episode(episode_id)

                # 创建新镜头
                for shot_data in shots_data:
                    shot = Shot(
                        episode_id=episode_id,
                        scene_number=shot_data.get("scene_number", 1),
                        shot_number=shot_data.get("shot_number", 1),
                        shot_type=shot_data.get("shot_type", "medium"),
                        duration=shot_data.get("duration", 5),
                        visual_description=shot_data.get("visual_description", ""),
                        dialogue=shot_data.get("dialogue", ""),
                        sound_music=shot_data.get("sound_music", ""),
                        camera_movement=shot_data.get("camera_movement", "static"),
                        notes=shot_data.get("notes", "")
                    )
                    db.create_shot(shot)

                # 更新剧集状态
                episode.status = "in_progress"
                db.update_episode(episode)

                st.success(f"成功生成 {len(shots_data)} 个镜头！")
                st.session_state.page = "storyboard"
                st.rerun()

            except Exception as e:
                st.error(f"生成失败: {e}")


# ==================== 页面: 分镜编辑 ====================

def page_storyboard():
    """分镜脚本编辑页面"""
    db = get_db()
    gemini = get_gemini()

    episode_id = st.session_state.current_episode_id
    project_id = st.session_state.current_project_id

    if not episode_id or not project_id:
        st.session_state.page = "project_detail"
        st.rerun()
        return

    project = db.get_project(project_id)
    episode = db.get_episode(episode_id)

    if not project or not episode:
        st.error("数据不存在")
        return

    # 顶部导航
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.header(f"📝 第{episode.episode_number}集: {episode.title}")
    with col2:
        if st.button("← 返回项目"):
            st.session_state.page = "project_detail"
            st.rerun()
    with col3:
        total_duration = episode.get_total_duration()
        st.metric("总时长", f"{total_duration}秒", f"目标: {episode.duration}秒")

    st.divider()

    if not episode.shots:
        st.info("暂无分镜，请先生成分镜脚本")
        if st.button("生成分镜"):
            st.session_state.page = "generate_storyboard"
            st.rerun()
        return

    # 分镜列表
    for i, shot in enumerate(episode.shots):
        with st.expander(
            f"场景{shot.scene_number} - 镜头{shot.shot_number} | {SHOT_TYPE_NAMES.get(shot.shot_type, shot.shot_type)} | {shot.duration}秒",
            expanded=False
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                # 编辑画面描述
                new_description = st.text_area(
                    "画面描述",
                    value=shot.visual_description,
                    key=f"desc_{shot.id}",
                    height=100
                )

                new_dialogue = st.text_input(
                    "对白",
                    value=shot.dialogue,
                    key=f"dialogue_{shot.id}"
                )

            with col2:
                new_shot_type = st.selectbox(
                    "镜头类型",
                    options=list(SHOT_TYPE_NAMES.keys()),
                    format_func=lambda x: SHOT_TYPE_NAMES[x],
                    index=list(SHOT_TYPE_NAMES.keys()).index(shot.shot_type) if shot.shot_type in SHOT_TYPE_NAMES else 3,
                    key=f"type_{shot.id}"
                )

                new_camera = st.selectbox(
                    "镜头运动",
                    options=list(CAMERA_MOVEMENT_NAMES.keys()),
                    format_func=lambda x: CAMERA_MOVEMENT_NAMES[x],
                    index=list(CAMERA_MOVEMENT_NAMES.keys()).index(shot.camera_movement) if shot.camera_movement in CAMERA_MOVEMENT_NAMES else 0,
                    key=f"camera_{shot.id}"
                )

                new_duration = st.number_input(
                    "时长(秒)",
                    min_value=1,
                    max_value=60,
                    value=shot.duration,
                    key=f"duration_{shot.id}"
                )

            new_sound = st.text_input(
                "音效/配乐",
                value=shot.sound_music,
                key=f"sound_{shot.id}"
            )

            # 保存和操作按钮
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("💾 保存", key=f"save_{shot.id}"):
                    shot.visual_description = new_description
                    shot.dialogue = new_dialogue
                    shot.shot_type = new_shot_type
                    shot.camera_movement = new_camera
                    shot.duration = new_duration
                    shot.sound_music = new_sound
                    db.update_shot(shot)
                    st.success("已保存")

            with col2:
                if st.button("✨ AI优化", key=f"enhance_{shot.id}"):
                    with st.spinner("优化中..."):
                        character_context = project.get_all_characters_context()
                        enhanced = gemini.expand_shot_description(
                            shot, episode, character_context, project.style
                        )
                        shot.visual_description = enhanced
                        db.update_shot(shot)
                        st.rerun()

            with col3:
                if st.button("🎬 生成提示词", key=f"prompt_{shot.id}"):
                    st.session_state.current_shot_id = shot.id
                    st.session_state.page = "generate_prompts"
                    st.rerun()

            with col4:
                if st.button("🗑️ 删除", key=f"delete_{shot.id}"):
                    db.delete_shot(shot.id)
                    st.rerun()

            # 显示已生成的提示词
            if shot.generated_prompts:
                st.markdown("---")
                st.markdown("**已生成的提示词:**")
                for key, prompt in shot.generated_prompts.items():
                    platform, ptype = key.rsplit("_", 1) if "_" in key else (key, "t2v")
                    with st.expander(f"{platform.upper()} - {ptype}"):
                        st.code(prompt, language=None)
                        st.button("📋 复制", key=f"copy_{shot.id}_{key}")


# ==================== 页面: 生成提示词 ====================

def page_generate_prompts():
    """生成视频提示词页面"""
    db = get_db()
    gemini = get_gemini()

    shot_id = st.session_state.get("current_shot_id")
    project_id = st.session_state.current_project_id

    if not shot_id or not project_id:
        st.session_state.page = "storyboard"
        st.rerun()
        return

    project = db.get_project(project_id)
    shot = db.get_shot(shot_id)

    if not project or not shot:
        st.error("数据不存在")
        return

    # 返回按钮
    if st.button("← 返回分镜"):
        st.session_state.page = "storyboard"
        st.rerun()

    st.header("🎬 生成视频提示词")

    # 显示镜头信息
    st.markdown(f"**场景{shot.scene_number} - 镜头{shot.shot_number}**")
    st.text(shot.visual_description)

    st.divider()

    # 平台选择
    st.subheader("选择目标平台")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        use_kling = st.checkbox("可灵 (Kling)", value=True)
    with col2:
        use_tongyi = st.checkbox("通义万相", value=True)
    with col3:
        use_jimeng = st.checkbox("即梦", value=True)
    with col4:
        use_hailuo = st.checkbox("海螺", value=True)

    platforms = []
    if use_kling: platforms.append("kling")
    if use_tongyi: platforms.append("tongyi")
    if use_jimeng: platforms.append("jimeng")
    if use_hailuo: platforms.append("hailuo")

    # 提示词类型选择
    st.subheader("选择提示词类型")
    col1, col2, col3 = st.columns(3)
    with col1:
        use_t2v = st.checkbox("文生视频", value=True)
    with col2:
        use_i2v_first = st.checkbox("首帧图片", value=False)
    with col3:
        use_i2v_last = st.checkbox("尾帧图片", value=False)

    prompt_types = []
    if use_t2v: prompt_types.append("t2v")
    if use_i2v_first: prompt_types.append("i2v_first")
    if use_i2v_last: prompt_types.append("i2v_last")

    st.divider()

    if st.button("🚀 生成提示词", type="primary", disabled=not platforms or not prompt_types):
        character_context = project.get_all_characters_context()

        progress = st.progress(0)
        total = len(platforms) * len(prompt_types)
        current = 0

        results = {}

        for platform in platforms:
            for ptype in prompt_types:
                with st.spinner(f"生成 {platform} {ptype} 提示词..."):
                    key = f"{platform}_{ptype}"
                    prompt = gemini.generate_video_prompt(
                        shot=shot,
                        platform=platform,
                        character_context=character_context,
                        style=project.style,
                        prompt_type=ptype
                    )
                    results[key] = prompt
                    current += 1
                    progress.progress(current / total)

        # 保存到镜头
        shot.generated_prompts.update(results)
        db.update_shot(shot)

        st.success("提示词生成完成！")

    # 显示结果
    if shot.generated_prompts:
        st.subheader("生成的提示词")

        for key, prompt in shot.generated_prompts.items():
            parts = key.rsplit("_", 1)
            platform = parts[0]
            ptype = parts[1] if len(parts) > 1 else "t2v"

            platform_names = {
                "kling": "可灵",
                "tongyi": "通义万相",
                "jimeng": "即梦",
                "hailuo": "海螺"
            }
            type_names = {
                "t2v": "文生视频",
                "i2v_first": "首帧图片",
                "i2v_last": "尾帧图片"
            }

            with st.expander(f"{platform_names.get(platform, platform)} - {type_names.get(ptype, ptype)}", expanded=True):
                st.code(prompt, language=None)

                # 复制按钮（使用clipboard功能）
                st.text_input(
                    "复制提示词",
                    value=prompt,
                    key=f"copy_input_{key}",
                    label_visibility="collapsed"
                )


# ==================== 撤销/重做辅助函数 ====================

def _perform_undo(db: Database, history: EditHistory):
    """执行撤销操作"""
    if history.edit_type == "episode_outline":
        episode = db.get_episode(history.target_id)
        if episode:
            # 恢复旧值
            old_data = json.loads(history.old_value)
            if history.field_name == "outline":
                episode.outline = old_data.get("outline", episode.outline)
            elif history.field_name == "title":
                episode.title = old_data.get("title", episode.title)
            elif history.field_name == "full":
                episode.outline = old_data.get("outline", episode.outline)
                episode.title = old_data.get("title", episode.title)
            db.update_episode(episode)

    elif history.edit_type == "character":
        character = db.get_character(history.target_id)
        if character:
            old_data = json.loads(history.old_value)
            for key, value in old_data.items():
                if hasattr(character, key):
                    setattr(character, key, value)
            db.update_character(character)

    # 标记为已撤销
    db.mark_edit_undone(history.id)


def _perform_redo(db: Database, history: EditHistory):
    """执行重做操作"""
    if history.edit_type == "episode_outline":
        episode = db.get_episode(history.target_id)
        if episode:
            # 应用新值
            new_data = json.loads(history.new_value)
            if history.field_name == "outline":
                episode.outline = new_data.get("outline", episode.outline)
            elif history.field_name == "title":
                episode.title = new_data.get("title", episode.title)
            elif history.field_name == "full":
                episode.outline = new_data.get("outline", episode.outline)
                episode.title = new_data.get("title", episode.title)
            db.update_episode(episode)

    elif history.edit_type == "character":
        character = db.get_character(history.target_id)
        if character:
            new_data = json.loads(history.new_value)
            for key, value in new_data.items():
                if hasattr(character, key):
                    setattr(character, key, value)
            db.update_character(character)

    # 标记为未撤销
    db.mark_edit_redone(history.id)


def _save_edit_history(db: Database, project_id: int, edit_type: str, target_id: int,
                       field_name: str, old_value: dict, new_value: dict,
                       edit_instruction: str = "", is_ai_edit: bool = False):
    """保存编辑历史"""
    history = EditHistory(
        project_id=project_id,
        edit_type=edit_type,
        target_id=target_id,
        field_name=field_name,
        old_value=json.dumps(old_value, ensure_ascii=False),
        new_value=json.dumps(new_value, ensure_ascii=False),
        edit_instruction=edit_instruction,
        is_ai_edit=is_ai_edit
    )
    db.create_edit_history(history)


def _get_edit_description(history: EditHistory) -> str:
    """获取编辑操作的简短描述"""
    db = get_db()

    if history.edit_type == "episode_outline":
        episode = db.get_episode(history.target_id)
        ep_name = f"第{episode.episode_number}集" if episode else f"剧集#{history.target_id}"

        if history.is_ai_edit:
            instruction = history.edit_instruction[:20] + "..." if len(history.edit_instruction) > 20 else history.edit_instruction
            return f"AI编辑{ep_name} ({instruction})"
        else:
            return f"手动编辑{ep_name}大纲"

    elif history.edit_type == "character":
        character = db.get_character(history.target_id)
        char_name = character.name if character else f"角色#{history.target_id}"
        return f"编辑角色「{char_name}」"

    else:
        return f"编辑{history.edit_type}"


def _show_edit_history(db: Database, project_id: int):
    """显示编辑历史列表"""
    histories = db.get_edit_history_by_project(project_id, include_undone=True)

    if not histories:
        st.info("暂无编辑历史")
        return

    st.markdown("**编辑历史**（最近10条）")

    for history in histories[:10]:
        desc = _get_edit_description(history)
        time_str = history.created_at.strftime("%m-%d %H:%M")

        if history.is_undone:
            st.markdown(f"~~{time_str} - {desc}~~ *(已撤销)*")
        else:
            icon = "🤖" if history.is_ai_edit else "✏️"
            st.markdown(f"{icon} {time_str} - {desc}")


# ==================== 页面: 编辑剧集大纲 ====================

def page_edit_episode():
    """编辑剧集大纲页面"""
    db = get_db()
    gemini = get_gemini()

    episode_id = st.session_state.current_episode_id
    project_id = st.session_state.current_project_id

    if not episode_id or not project_id:
        st.session_state.page = "project_detail"
        st.rerun()
        return

    project = db.get_project(project_id)
    episode = db.get_episode(episode_id)

    if not project or not episode:
        st.error("数据不存在")
        return

    # 返回按钮
    if st.button("← 返回项目"):
        st.session_state.page = "project_detail"
        st.rerun()

    st.header(f"✏️ 编辑大纲 - 第{episode.episode_number}集")

    # 保存原始值用于历史记录
    original_title = episode.title
    original_outline = episode.outline

    # 编辑模式选择
    edit_mode = st.radio(
        "编辑方式",
        ["📝 直接编辑", "🤖 AI辅助编辑"],
        horizontal=True
    )

    if edit_mode == "📝 直接编辑":
        # 直接编辑模式
        with st.form("edit_episode_form"):
            new_title = st.text_input("标题", value=episode.title)
            new_outline = st.text_area("大纲", value=episode.outline, height=200)

            if st.form_submit_button("💾 保存修改", type="primary"):
                if new_title != original_title or new_outline != original_outline:
                    # 保存历史
                    _save_edit_history(
                        db, project_id, "episode_outline", episode.id, "full",
                        {"title": original_title, "outline": original_outline},
                        {"title": new_title, "outline": new_outline},
                        is_ai_edit=False
                    )

                    # 更新剧集
                    episode.title = new_title
                    episode.outline = new_outline
                    db.update_episode(episode)

                    st.success("保存成功！")

                    # 检查一致性
                    _check_and_show_consistency_issues(
                        gemini, db, project, episode, original_outline, new_outline
                    )
                else:
                    st.info("没有检测到修改")

    else:
        # AI辅助编辑模式
        st.subheader("当前大纲")
        st.info(f"**{episode.title}**\n\n{episode.outline}")

        instruction = st.text_area(
            "修改指令",
            placeholder="告诉AI你想如何修改...\n例如: 让主角在这一集发现真相，但先保持悬念",
            height=100
        )

        character_context = project.get_all_characters_context(up_to_episode=episode.episode_number - 1)

        if st.button("🤖 AI生成修改", type="primary", disabled=not instruction):
            with st.spinner("AI正在分析并生成修改..."):
                try:
                    result = gemini.edit_episode_with_instruction(
                        episode=episode,
                        project=project,
                        instruction=instruction,
                        character_context=character_context
                    )

                    st.session_state.ai_edit_result = result
                    st.session_state.ai_edit_instruction = instruction

                except Exception as e:
                    st.error(f"生成失败: {e}")

        # 显示AI生成的结果
        if "ai_edit_result" in st.session_state:
            result = st.session_state.ai_edit_result

            st.subheader("AI生成的修改")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**原标题:**")
                st.text(original_title)
            with col2:
                st.markdown("**新标题:**")
                st.text(result.get("new_title", original_title))

            st.markdown("**修改说明:**")
            st.info(result.get("changes_summary", ""))

            st.markdown("**新大纲:**")
            st.text_area("预览", value=result.get("new_outline", ""), height=200, disabled=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 应用修改", type="primary"):
                    new_title = result.get("new_title", original_title)
                    new_outline = result.get("new_outline", original_outline)

                    # 保存历史
                    _save_edit_history(
                        db, project_id, "episode_outline", episode.id, "full",
                        {"title": original_title, "outline": original_outline},
                        {"title": new_title, "outline": new_outline},
                        edit_instruction=st.session_state.get("ai_edit_instruction", ""),
                        is_ai_edit=True
                    )

                    # 更新剧集
                    episode.title = new_title
                    episode.outline = new_outline
                    db.update_episode(episode)

                    # 清理session state
                    del st.session_state.ai_edit_result
                    if "ai_edit_instruction" in st.session_state:
                        del st.session_state.ai_edit_instruction

                    st.success("修改已应用！")

                    # 检查一致性
                    _check_and_show_consistency_issues(
                        gemini, db, project, episode, original_outline, new_outline
                    )

            with col2:
                if st.button("❌ 放弃修改"):
                    del st.session_state.ai_edit_result
                    if "ai_edit_instruction" in st.session_state:
                        del st.session_state.ai_edit_instruction
                    st.rerun()


def _check_and_show_consistency_issues(gemini, db, project, episode, original_outline, new_outline):
    """检查并显示一致性问题"""
    with st.spinner("正在检查一致性..."):
        try:
            issues = gemini.analyze_edit_impact(
                edited_episode=episode,
                original_outline=original_outline,
                new_outline=new_outline,
                project=project,
                all_episodes=project.episodes,
                characters=project.characters
            )

            if issues:
                # 保存到session state以便在项目页面显示
                st.session_state.pending_issues = issues

                st.warning(f"⚠️ 发现 {len(issues)} 个潜在一致性问题（已保存，可在项目页面查看）")

                for i, issue in enumerate(issues):
                    severity_icon = "🔴" if issue.get("severity") == "error" else "🟡"
                    issue_type = issue.get("type", "")
                    type_label = "剧集" if issue_type == "episode" else "角色" if issue_type == "character" else issue_type

                    with st.expander(f"{severity_icon} {type_label}: {issue.get('name')}", expanded=True):
                        st.markdown(f"**问题:** {issue.get('issue')}")
                        st.markdown(f"**建议修复:** {issue.get('suggested_fix')}")

                        # 判断是否可以自动修复
                        can_auto_fix = issue.get("auto_fixable", False)
                        is_implemented = issue_type == "episode"  # 目前只实现了剧集修复
                        fix_reason = issue.get("auto_fix_reason", "")

                        if can_auto_fix and is_implemented:
                            if st.button(f"🔧 自动修复", key=f"fix_issue_{i}"):
                                _apply_consistency_fix(gemini, db, project, issue)
                                # 从pending列表中移除
                                if "pending_issues" in st.session_state:
                                    st.session_state.pending_issues = [
                                        iss for iss in st.session_state.pending_issues
                                        if iss.get("name") != issue.get("name")
                                    ]
                                st.rerun()
                            if fix_reason:
                                st.caption(f"💡 {fix_reason}")
                        elif can_auto_fix and not is_implemented:
                            st.caption(f"💡 此问题可自动修复，但角色修复功能开发中。原因: {fix_reason}")
                        elif not can_auto_fix:
                            reason_text = fix_reason if fix_reason else "此问题涉及叙事结构或核心设定"
                            st.caption(f"💡 建议人工审核: {reason_text}")
            else:
                # 清空pending issues
                st.session_state.pending_issues = []
                st.success("✅ 未发现一致性问题")

        except Exception as e:
            st.warning(f"一致性检查失败: {e}")


def _apply_consistency_fix(gemini, db, project, issue):
    """应用一致性修复"""
    try:
        if issue.get("type") == "episode":
            # 修复剧集
            target_episode = None
            for ep in project.episodes:
                if ep.episode_number == issue.get("id"):
                    target_episode = ep
                    break

            if target_episode:
                character_context = project.get_all_characters_context()
                fix_result = gemini.generate_consistency_fix(
                    issue_type="剧集",
                    target_name=f"第{target_episode.episode_number}集 - {target_episode.title}",
                    issue_description=issue.get("issue"),
                    original_content=target_episode.outline,
                    project=project,
                    character_context=character_context
                )

                # 保存历史
                _save_edit_history(
                    db, project.id, "episode_outline", target_episode.id, "outline",
                    {"outline": target_episode.outline},
                    {"outline": fix_result.get("fixed_content", target_episode.outline)},
                    edit_instruction=f"一致性修复: {issue.get('issue')}",
                    is_ai_edit=True
                )

                target_episode.outline = fix_result.get("fixed_content", target_episode.outline)
                db.update_episode(target_episode)
                st.success(f"已修复: {fix_result.get('explanation', '修复完成')}")

        elif issue.get("type") == "character":
            # 修复角色（待实现）
            st.info("角色修复功能开发中...")

    except Exception as e:
        st.error(f"修复失败: {e}")


# ==================== 主应用 ====================

def main():
    st.set_page_config(
        page_title="AI故事生成器",
        page_icon="📖",
        layout="wide",
    )

    # 初始化
    init_session_state()

    # 侧边栏
    with st.sidebar:
        st.title("📖 AI故事生成器")
        st.caption("基于Gemini的智能剧本创作工具")

        st.divider()

        # 导航
        if st.button("🏠 项目列表", use_container_width=True):
            st.session_state.page = "projects"
            st.session_state.current_project_id = None
            st.session_state.current_episode_id = None
            st.rerun()

        # 当前项目信息
        if st.session_state.current_project_id:
            db = get_db()
            project = db.get_project(st.session_state.current_project_id)
            if project:
                st.divider()
                st.markdown(f"**当前项目:** {project.name}")

        st.divider()

        # Gemini状态
        gemini = get_gemini()
        if gemini:
            st.success("✅ Gemini已连接")
        else:
            st.error("❌ Gemini未连接")

    # 页面路由
    page = st.session_state.page

    if page == "projects":
        page_projects()
    elif page == "new_project":
        page_new_project()
    elif page == "project_detail":
        page_project_detail()
    elif page == "generate_storyboard":
        page_generate_storyboard()
    elif page == "storyboard":
        page_storyboard()
    elif page == "generate_prompts":
        page_generate_prompts()
    elif page == "edit_episode":
        page_edit_episode()
    else:
        page_projects()


if __name__ == "__main__":
    main()
