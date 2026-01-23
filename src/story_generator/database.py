"""
Story Generator Database

SQLite数据库管理，用于持久化存储故事项目
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .models import Project, Character, Episode, Shot, MajorEvent, EditHistory


class Database:
    """SQLite数据库管理类"""

    def __init__(self, db_path: str = "data/story_generator.db"):
        self.db_path = db_path
        self._persistent_conn = None  # 用于内存数据库的持久连接
        # 确保数据目录存在（跳过内存数据库）
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        else:
            # 内存数据库需要保持连接，否则每次连接都是新数据库
            self._persistent_conn = sqlite3.connect(":memory:")
            self._persistent_conn.row_factory = sqlite3.Row
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._persistent_conn is not None:
            return self._persistent_conn
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _close_connection(self, conn: sqlite3.Connection):
        """关闭连接（内存数据库不关闭）"""
        if self._persistent_conn is None:
            conn.close()

    def _init_database(self):
        """初始化数据库表结构"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 项目表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                genre TEXT DEFAULT 'drama',
                style TEXT,
                target_audience TEXT,
                num_episodes INTEGER DEFAULT 1,
                episode_duration INTEGER DEFAULT 60,
                max_video_duration INTEGER DEFAULT 10,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # 尝试添加 max_video_duration 列（兼容旧数据库）
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN max_video_duration INTEGER DEFAULT 10")
        except sqlite3.OperationalError:
            pass  # 列已存在

        # 人物表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                age TEXT,
                appearance TEXT,
                personality TEXT,
                background TEXT,
                relationships TEXT,
                visual_description TEXT,
                major_events TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # 剧集表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                episode_number INTEGER NOT NULL,
                title TEXT,
                outline TEXT,
                duration INTEGER DEFAULT 60,
                status TEXT DEFAULT 'outline',
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # 镜头表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_id INTEGER NOT NULL,
                scene_number INTEGER DEFAULT 1,
                shot_number INTEGER DEFAULT 1,
                shot_type TEXT DEFAULT 'medium',
                duration INTEGER DEFAULT 5,
                visual_description TEXT,
                dialogue TEXT,
                sound_music TEXT,
                camera_movement TEXT DEFAULT 'static',
                notes TEXT,
                generated_prompts TEXT,
                FOREIGN KEY (episode_id) REFERENCES episodes(id) ON DELETE CASCADE
            )
        """)

        # 编辑历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                edit_type TEXT NOT NULL,
                target_id INTEGER,
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                edit_instruction TEXT,
                is_ai_edit INTEGER DEFAULT 0,
                related_changes TEXT,
                is_undone INTEGER DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        self._close_connection(conn)

    # ==================== Project CRUD ====================

    def create_project(self, project: Project) -> int:
        """创建项目"""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO projects (name, description, genre, style, target_audience,
                                  num_episodes, episode_duration, max_video_duration,
                                  created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (project.name, project.description, project.genre, project.style,
              project.target_audience, project.num_episodes, project.episode_duration,
              project.max_video_duration, now, now))

        project_id = cursor.lastrowid
        conn.commit()
        self._close_connection(conn)

        project.id = project_id
        project.created_at = datetime.fromisoformat(now)
        project.updated_at = datetime.fromisoformat(now)

        return project_id

    def get_project(self, project_id: int) -> Optional[Project]:
        """获取项目（包含人物和剧集）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()

        if not row:
            self._close_connection(conn)
            return None

        # 安全获取 max_video_duration（兼容旧数据库）
        max_video_duration = 10
        try:
            max_video_duration = row["max_video_duration"] or 10
        except (IndexError, KeyError):
            pass

        project = Project(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            genre=row["genre"] or "drama",
            style=row["style"] or "",
            target_audience=row["target_audience"] or "",
            num_episodes=row["num_episodes"] or 1,
            episode_duration=row["episode_duration"] or 60,
            max_video_duration=max_video_duration,
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now(),
        )

        # 加载人物
        project.characters = self.get_characters_by_project(project_id)

        # 加载剧集
        project.episodes = self.get_episodes_by_project(project_id)

        self._close_connection(conn)
        return project

    def update_project(self, project: Project):
        """更新项目"""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE projects SET name=?, description=?, genre=?, style=?,
                               target_audience=?, num_episodes=?, episode_duration=?,
                               max_video_duration=?, updated_at=?
            WHERE id=?
        """, (project.name, project.description, project.genre, project.style,
              project.target_audience, project.num_episodes, project.episode_duration,
              project.max_video_duration, now, project.id))

        conn.commit()
        self._close_connection(conn)
        project.updated_at = datetime.fromisoformat(now)

    def delete_project(self, project_id: int):
        """删除项目（级联删除人物、剧集、镜头）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 手动级联删除（SQLite的外键级联需要启用）
        cursor.execute("DELETE FROM shots WHERE episode_id IN (SELECT id FROM episodes WHERE project_id=?)", (project_id,))
        cursor.execute("DELETE FROM episodes WHERE project_id=?", (project_id,))
        cursor.execute("DELETE FROM characters WHERE project_id=?", (project_id,))
        cursor.execute("DELETE FROM projects WHERE id=?", (project_id,))

        conn.commit()
        self._close_connection(conn)

    def list_projects(self) -> List[Project]:
        """列出所有项目（不包含详细数据）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
        rows = cursor.fetchall()

        projects = []
        for row in rows:
            # 安全获取 max_video_duration（兼容旧数据库）
            max_video_duration = 10
            try:
                max_video_duration = row["max_video_duration"] or 10
            except (IndexError, KeyError):
                pass

            project = Project(
                id=row["id"],
                name=row["name"],
                description=row["description"] or "",
                genre=row["genre"] or "drama",
                style=row["style"] or "",
                target_audience=row["target_audience"] or "",
                num_episodes=row["num_episodes"] or 1,
                episode_duration=row["episode_duration"] or 60,
                max_video_duration=max_video_duration,
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now(),
            )
            projects.append(project)

        self._close_connection(conn)
        return projects

    # ==================== Character CRUD ====================

    def create_character(self, character: Character) -> int:
        """创建人物"""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        major_events_json = json.dumps([e.to_dict() for e in character.major_events], ensure_ascii=False)

        cursor.execute("""
            INSERT INTO characters (project_id, name, age, appearance, personality,
                                    background, relationships, visual_description,
                                    major_events, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (character.project_id, character.name, character.age, character.appearance,
              character.personality, character.background, character.relationships,
              character.visual_description, major_events_json, now, now))

        character_id = cursor.lastrowid
        conn.commit()
        self._close_connection(conn)

        character.id = character_id
        return character_id

    def get_character(self, character_id: int) -> Optional[Character]:
        """获取人物"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
        row = cursor.fetchone()

        if not row:
            self._close_connection(conn)
            return None

        major_events = []
        if row["major_events"]:
            events_data = json.loads(row["major_events"])
            major_events = [MajorEvent.from_dict(e) for e in events_data]

        character = Character(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            age=row["age"] or "",
            appearance=row["appearance"] or "",
            personality=row["personality"] or "",
            background=row["background"] or "",
            relationships=row["relationships"] or "",
            visual_description=row["visual_description"] or "",
            major_events=major_events,
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now(),
        )

        self._close_connection(conn)
        return character

    def update_character(self, character: Character):
        """更新人物"""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        major_events_json = json.dumps([e.to_dict() for e in character.major_events], ensure_ascii=False)

        cursor.execute("""
            UPDATE characters SET name=?, age=?, appearance=?, personality=?,
                                  background=?, relationships=?, visual_description=?,
                                  major_events=?, updated_at=?
            WHERE id=?
        """, (character.name, character.age, character.appearance, character.personality,
              character.background, character.relationships, character.visual_description,
              major_events_json, now, character.id))

        conn.commit()
        self._close_connection(conn)
        character.updated_at = datetime.fromisoformat(now)

    def delete_character(self, character_id: int):
        """删除人物"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM characters WHERE id=?", (character_id,))
        conn.commit()
        self._close_connection(conn)

    def get_characters_by_project(self, project_id: int) -> List[Character]:
        """获取项目的所有人物"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM characters WHERE project_id = ? ORDER BY id", (project_id,))
        rows = cursor.fetchall()

        characters = []
        for row in rows:
            major_events = []
            if row["major_events"]:
                events_data = json.loads(row["major_events"])
                major_events = [MajorEvent.from_dict(e) for e in events_data]

            character = Character(
                id=row["id"],
                project_id=row["project_id"],
                name=row["name"],
                age=row["age"] or "",
                appearance=row["appearance"] or "",
                personality=row["personality"] or "",
                background=row["background"] or "",
                relationships=row["relationships"] or "",
                visual_description=row["visual_description"] or "",
                major_events=major_events,
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now(),
            )
            characters.append(character)

        self._close_connection(conn)
        return characters

    # ==================== Episode CRUD ====================

    def create_episode(self, episode: Episode) -> int:
        """创建剧集"""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO episodes (project_id, episode_number, title, outline,
                                  duration, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (episode.project_id, episode.episode_number, episode.title, episode.outline,
              episode.duration, episode.status, now, now))

        episode_id = cursor.lastrowid
        conn.commit()
        self._close_connection(conn)

        episode.id = episode_id
        return episode_id

    def get_episode(self, episode_id: int) -> Optional[Episode]:
        """获取剧集（包含镜头）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
        row = cursor.fetchone()

        if not row:
            self._close_connection(conn)
            return None

        episode = Episode(
            id=row["id"],
            project_id=row["project_id"],
            episode_number=row["episode_number"],
            title=row["title"] or "",
            outline=row["outline"] or "",
            duration=row["duration"] or 60,
            status=row["status"] or "outline",
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now(),
        )

        # 加载镜头
        episode.shots = self.get_shots_by_episode(episode_id)

        self._close_connection(conn)
        return episode

    def update_episode(self, episode: Episode):
        """更新剧集"""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE episodes SET episode_number=?, title=?, outline=?,
                               duration=?, status=?, updated_at=?
            WHERE id=?
        """, (episode.episode_number, episode.title, episode.outline,
              episode.duration, episode.status, now, episode.id))

        conn.commit()
        self._close_connection(conn)
        episode.updated_at = datetime.fromisoformat(now)

    def delete_episode(self, episode_id: int):
        """删除剧集（级联删除镜头）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shots WHERE episode_id=?", (episode_id,))
        cursor.execute("DELETE FROM episodes WHERE id=?", (episode_id,))
        conn.commit()
        self._close_connection(conn)

    def get_episodes_by_project(self, project_id: int) -> List[Episode]:
        """获取项目的所有剧集"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM episodes WHERE project_id = ? ORDER BY episode_number", (project_id,))
        rows = cursor.fetchall()

        episodes = []
        for row in rows:
            episode = Episode(
                id=row["id"],
                project_id=row["project_id"],
                episode_number=row["episode_number"],
                title=row["title"] or "",
                outline=row["outline"] or "",
                duration=row["duration"] or 60,
                status=row["status"] or "outline",
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
                updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.now(),
            )
            # 加载镜头
            episode.shots = self.get_shots_by_episode(episode.id)
            episodes.append(episode)

        self._close_connection(conn)
        return episodes

    # ==================== Shot CRUD ====================

    def create_shot(self, shot: Shot) -> int:
        """创建镜头"""
        conn = self._get_connection()
        cursor = conn.cursor()

        prompts_json = json.dumps(shot.generated_prompts, ensure_ascii=False)
        cursor.execute("""
            INSERT INTO shots (episode_id, scene_number, shot_number, shot_type,
                               duration, visual_description, dialogue, sound_music,
                               camera_movement, notes, generated_prompts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (shot.episode_id, shot.scene_number, shot.shot_number, shot.shot_type,
              shot.duration, shot.visual_description, shot.dialogue, shot.sound_music,
              shot.camera_movement, shot.notes, prompts_json))

        shot_id = cursor.lastrowid
        conn.commit()
        self._close_connection(conn)

        shot.id = shot_id
        return shot_id

    def get_shot(self, shot_id: int) -> Optional[Shot]:
        """获取镜头"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM shots WHERE id = ?", (shot_id,))
        row = cursor.fetchone()

        if not row:
            self._close_connection(conn)
            return None

        prompts = {}
        if row["generated_prompts"]:
            prompts = json.loads(row["generated_prompts"])

        shot = Shot(
            id=row["id"],
            episode_id=row["episode_id"],
            scene_number=row["scene_number"],
            shot_number=row["shot_number"],
            shot_type=row["shot_type"] or "medium",
            duration=row["duration"] or 5,
            visual_description=row["visual_description"] or "",
            dialogue=row["dialogue"] or "",
            sound_music=row["sound_music"] or "",
            camera_movement=row["camera_movement"] or "static",
            notes=row["notes"] or "",
            generated_prompts=prompts,
        )

        self._close_connection(conn)
        return shot

    def update_shot(self, shot: Shot):
        """更新镜头"""
        conn = self._get_connection()
        cursor = conn.cursor()

        prompts_json = json.dumps(shot.generated_prompts, ensure_ascii=False)
        cursor.execute("""
            UPDATE shots SET scene_number=?, shot_number=?, shot_type=?,
                            duration=?, visual_description=?, dialogue=?, sound_music=?,
                            camera_movement=?, notes=?, generated_prompts=?
            WHERE id=?
        """, (shot.scene_number, shot.shot_number, shot.shot_type, shot.duration,
              shot.visual_description, shot.dialogue, shot.sound_music,
              shot.camera_movement, shot.notes, prompts_json, shot.id))

        conn.commit()
        self._close_connection(conn)

    def delete_shot(self, shot_id: int):
        """删除镜头"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shots WHERE id=?", (shot_id,))
        conn.commit()
        self._close_connection(conn)

    def get_shots_by_episode(self, episode_id: int) -> List[Shot]:
        """获取剧集的所有镜头"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM shots WHERE episode_id = ? ORDER BY scene_number, shot_number", (episode_id,))
        rows = cursor.fetchall()

        shots = []
        for row in rows:
            prompts = {}
            if row["generated_prompts"]:
                prompts = json.loads(row["generated_prompts"])

            shot = Shot(
                id=row["id"],
                episode_id=row["episode_id"],
                scene_number=row["scene_number"],
                shot_number=row["shot_number"],
                shot_type=row["shot_type"] or "medium",
                duration=row["duration"] or 5,
                visual_description=row["visual_description"] or "",
                dialogue=row["dialogue"] or "",
                sound_music=row["sound_music"] or "",
                camera_movement=row["camera_movement"] or "static",
                notes=row["notes"] or "",
                generated_prompts=prompts,
            )
            shots.append(shot)

        self._close_connection(conn)
        return shots

    def delete_shots_by_episode(self, episode_id: int):
        """删除剧集的所有镜头"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shots WHERE episode_id=?", (episode_id,))
        conn.commit()
        self._close_connection(conn)

    def batch_create_shots(self, shots: List[Shot]) -> List[int]:
        """批量创建镜头"""
        conn = self._get_connection()
        cursor = conn.cursor()

        shot_ids = []
        for shot in shots:
            prompts_json = json.dumps(shot.generated_prompts, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO shots (episode_id, scene_number, shot_number, shot_type,
                                   duration, visual_description, dialogue, sound_music,
                                   camera_movement, notes, generated_prompts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (shot.episode_id, shot.scene_number, shot.shot_number, shot.shot_type,
                  shot.duration, shot.visual_description, shot.dialogue, shot.sound_music,
                  shot.camera_movement, shot.notes, prompts_json))
            shot.id = cursor.lastrowid
            shot_ids.append(shot.id)

        conn.commit()
        self._close_connection(conn)
        return shot_ids

    # ==================== EditHistory CRUD ====================

    def create_edit_history(self, history: EditHistory) -> int:
        """创建编辑历史记录"""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO edit_history (project_id, edit_type, target_id, field_name,
                                      old_value, new_value, edit_instruction, is_ai_edit,
                                      related_changes, is_undone, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (history.project_id, history.edit_type, history.target_id, history.field_name,
              history.old_value, history.new_value, history.edit_instruction,
              1 if history.is_ai_edit else 0, history.related_changes,
              1 if history.is_undone else 0, now))

        history_id = cursor.lastrowid
        conn.commit()
        self._close_connection(conn)

        history.id = history_id
        history.created_at = datetime.fromisoformat(now)
        return history_id

    def get_edit_history(self, history_id: int) -> Optional[EditHistory]:
        """获取编辑历史记录"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM edit_history WHERE id = ?", (history_id,))
        row = cursor.fetchone()

        if not row:
            self._close_connection(conn)
            return None

        history = EditHistory(
            id=row["id"],
            project_id=row["project_id"],
            edit_type=row["edit_type"] or "",
            target_id=row["target_id"],
            field_name=row["field_name"] or "",
            old_value=row["old_value"] or "",
            new_value=row["new_value"] or "",
            edit_instruction=row["edit_instruction"] or "",
            is_ai_edit=bool(row["is_ai_edit"]),
            related_changes=row["related_changes"] or "",
            is_undone=bool(row["is_undone"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
        )

        self._close_connection(conn)
        return history

    def get_edit_history_by_project(self, project_id: int, include_undone: bool = False) -> List[EditHistory]:
        """获取项目的编辑历史（按时间倒序）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if include_undone:
            cursor.execute(
                "SELECT * FROM edit_history WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,)
            )
        else:
            cursor.execute(
                "SELECT * FROM edit_history WHERE project_id = ? AND is_undone = 0 ORDER BY created_at DESC",
                (project_id,)
            )

        rows = cursor.fetchall()
        histories = []

        for row in rows:
            history = EditHistory(
                id=row["id"],
                project_id=row["project_id"],
                edit_type=row["edit_type"] or "",
                target_id=row["target_id"],
                field_name=row["field_name"] or "",
                old_value=row["old_value"] or "",
                new_value=row["new_value"] or "",
                edit_instruction=row["edit_instruction"] or "",
                is_ai_edit=bool(row["is_ai_edit"]),
                related_changes=row["related_changes"] or "",
                is_undone=bool(row["is_undone"]),
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
            )
            histories.append(history)

        self._close_connection(conn)
        return histories

    def mark_edit_undone(self, history_id: int):
        """标记编辑为已撤销"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE edit_history SET is_undone = 1 WHERE id = ?", (history_id,))
        conn.commit()
        self._close_connection(conn)

    def mark_edit_redone(self, history_id: int):
        """标记编辑为已重做（取消撤销）"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE edit_history SET is_undone = 0 WHERE id = ?", (history_id,))
        conn.commit()
        self._close_connection(conn)

    def get_latest_undoable_edit(self, project_id: int) -> Optional[EditHistory]:
        """获取最新的可撤销编辑"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM edit_history
            WHERE project_id = ? AND is_undone = 0
            ORDER BY created_at DESC LIMIT 1
        """, (project_id,))
        row = cursor.fetchone()

        if not row:
            self._close_connection(conn)
            return None

        history = EditHistory(
            id=row["id"],
            project_id=row["project_id"],
            edit_type=row["edit_type"] or "",
            target_id=row["target_id"],
            field_name=row["field_name"] or "",
            old_value=row["old_value"] or "",
            new_value=row["new_value"] or "",
            edit_instruction=row["edit_instruction"] or "",
            is_ai_edit=bool(row["is_ai_edit"]),
            related_changes=row["related_changes"] or "",
            is_undone=bool(row["is_undone"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
        )

        self._close_connection(conn)
        return history

    def get_latest_redoable_edit(self, project_id: int) -> Optional[EditHistory]:
        """获取最新的可重做编辑（已撤销的）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM edit_history
            WHERE project_id = ? AND is_undone = 1
            ORDER BY created_at DESC LIMIT 1
        """, (project_id,))
        row = cursor.fetchone()

        if not row:
            self._close_connection(conn)
            return None

        history = EditHistory(
            id=row["id"],
            project_id=row["project_id"],
            edit_type=row["edit_type"] or "",
            target_id=row["target_id"],
            field_name=row["field_name"] or "",
            old_value=row["old_value"] or "",
            new_value=row["new_value"] or "",
            edit_instruction=row["edit_instruction"] or "",
            is_ai_edit=bool(row["is_ai_edit"]),
            related_changes=row["related_changes"] or "",
            is_undone=bool(row["is_undone"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
        )

        self._close_connection(conn)
        return history

    def delete_edit_history_by_project(self, project_id: int):
        """删除项目的所有编辑历史"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM edit_history WHERE project_id = ?", (project_id,))
        conn.commit()
        self._close_connection(conn)
