"""
Agent Session Management

Handles session persistence, checkpoints, and recovery.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

from .state import AgentState, WorkflowPhase, InteractionMode, UserRequest


class SessionStatus(Enum):
    """Session status."""
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Checkpoint:
    """A checkpoint in the workflow."""
    id: Optional[int] = None
    session_id: str = ""
    step_name: str = ""
    phase: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "step_name": self.step_name,
            "phase": self.phase,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }


@dataclass
class Session:
    """An agent workflow session."""
    id: Optional[int] = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_request: str = ""
    mode: str = "interactive"
    current_phase: str = "init"
    current_agent: str = ""
    project_id: Optional[int] = None
    state_json: str = "{}"
    status: SessionStatus = SessionStatus.RUNNING
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_request": self.user_request,
            "mode": self.mode,
            "current_phase": self.current_phase,
            "current_agent": self.current_agent,
            "project_id": self.project_id,
            "status": self.status.value if isinstance(self.status, SessionStatus) else self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }


class SessionManager:
    """
    Manages agent workflow sessions with persistence.

    Provides:
    - Session creation and tracking
    - Checkpoint management
    - Session recovery
    - State serialization/deserialization
    """

    def __init__(self, db_path: str = "story_generator.db"):
        self.db_path = db_path
        self._init_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Initialize session tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Agent sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_request TEXT,
                mode TEXT DEFAULT 'interactive',
                current_phase TEXT DEFAULT 'init',
                current_agent TEXT,
                project_id INTEGER,
                state_json TEXT,
                status TEXT DEFAULT 'running',
                error_message TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
            )
        """)

        # Agent checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                step_name TEXT NOT NULL,
                phase TEXT,
                input_json TEXT,
                output_json TEXT,
                created_at TEXT,
                FOREIGN KEY (session_id) REFERENCES agent_sessions(session_id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    # ==================== Session Operations ====================

    def create_session(
        self,
        user_request: str,
        mode: InteractionMode = InteractionMode.INTERACTIVE,
    ) -> Session:
        """Create a new workflow session."""
        session = Session(
            user_request=user_request,
            mode=mode.value if isinstance(mode, InteractionMode) else mode,
        )

        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO agent_sessions
            (session_id, user_request, mode, current_phase, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.user_request,
            session.mode,
            session.current_phase,
            session.status.value,
            now,
            now,
        ))

        session.id = cursor.lastrowid
        conn.commit()
        conn.close()

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM agent_sessions WHERE session_id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_session(row)

    def update_session(self, session: Session):
        """Update a session."""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE agent_sessions SET
                current_phase = ?,
                current_agent = ?,
                project_id = ?,
                state_json = ?,
                status = ?,
                error_message = ?,
                updated_at = ?
            WHERE session_id = ?
        """, (
            session.current_phase,
            session.current_agent,
            session.project_id,
            session.state_json,
            session.status.value if isinstance(session.status, SessionStatus) else session.status,
            session.error_message,
            now,
            session.session_id,
        ))

        conn.commit()
        conn.close()

    def list_sessions(
        self,
        status: Optional[SessionStatus] = None,
        limit: int = 20
    ) -> List[Session]:
        """List sessions, optionally filtered by status."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                "SELECT * FROM agent_sessions WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                (status.value, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM agent_sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            )

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_session(row) for row in rows]

    def delete_session(self, session_id: str):
        """Delete a session and its checkpoints."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM agent_checkpoints WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM agent_sessions WHERE session_id = ?", (session_id,))

        conn.commit()
        conn.close()

    def update_session_status(
        self,
        session_id: str,
        status: SessionStatus,
        error_message: Optional[str] = None
    ):
        """Update session status and optionally error message."""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE agent_sessions SET
                status = ?,
                error_message = ?,
                updated_at = ?
            WHERE session_id = ?
        """, (
            status.value,
            error_message,
            now,
            session_id,
        ))

        conn.commit()
        conn.close()

    # ==================== Checkpoint Operations ====================

    def create_checkpoint(
        self,
        session_id: str,
        step_name: str,
        phase: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
    ) -> Checkpoint:
        """Create a checkpoint for the session."""
        checkpoint = Checkpoint(
            session_id=session_id,
            step_name=step_name,
            phase=phase,
            input_data=input_data,
            output_data=output_data,
        )

        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO agent_checkpoints
            (session_id, step_name, phase, input_json, output_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            step_name,
            phase,
            json.dumps(input_data, ensure_ascii=False, default=str),
            json.dumps(output_data, ensure_ascii=False, default=str),
            now,
        ))

        checkpoint.id = cursor.lastrowid
        conn.commit()
        conn.close()

        return checkpoint

    def get_checkpoints(self, session_id: str) -> List[Checkpoint]:
        """Get all checkpoints for a session."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM agent_checkpoints WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_checkpoint(row) for row in rows]

    def get_last_checkpoint(self, session_id: str) -> Optional[Checkpoint]:
        """Get the last checkpoint for a session."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM agent_checkpoints WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_checkpoint(row)

    # ==================== State Serialization ====================

    def save_state(self, session_id: str, state: AgentState):
        """Save agent state to session."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        # Serialize state
        state_dict = self._serialize_state(state)
        session.state_json = json.dumps(state_dict, ensure_ascii=False, default=str)
        session.current_phase = state.phase.value if isinstance(state.phase, WorkflowPhase) else state.phase
        session.current_agent = state.current_agent
        session.project_id = state.project_id

        if state.error:
            session.status = SessionStatus.FAILED
            session.error_message = state.error
        elif state.phase == WorkflowPhase.COMPLETED:
            session.status = SessionStatus.COMPLETED
        elif state.pending_approval:
            session.status = SessionStatus.PAUSED
        else:
            session.status = SessionStatus.RUNNING

        self.update_session(session)

    def load_state(self, session_id: str) -> Optional[AgentState]:
        """Load agent state from session."""
        session = self.get_session(session_id)
        if not session or not session.state_json:
            return None

        state_dict = json.loads(session.state_json)
        return self._deserialize_state(state_dict)

    def _serialize_state(self, state: AgentState) -> Dict[str, Any]:
        """Serialize AgentState to dict."""
        return {
            "request": {
                "idea": state.request.idea,
                "genre": state.request.genre,
                "style": state.request.style,
                "num_episodes": state.request.num_episodes,
                "episode_duration": state.request.episode_duration,
                "num_characters": state.request.num_characters,
                "target_audience": state.request.target_audience,
                "target_platform": state.request.target_platform,
            } if state.request else None,
            "phase": state.phase.value if isinstance(state.phase, WorkflowPhase) else state.phase,
            "mode": state.mode.value if isinstance(state.mode, InteractionMode) else state.mode,
            "current_agent": state.current_agent,
            "next_agent": state.next_agent,
            "project_id": state.project_id,
            "project_name": state.project_name,
            "story_outline": state.story_outline,
            "characters": state.characters,
            "episodes": state.episodes,
            "current_episode_index": state.current_episode_index,
            "storyboard": state.storyboard,
            "current_shot_index": state.current_shot_index,
            "video_prompts": state.video_prompts,
            "video_tasks": state.video_tasks,
            "error": state.error,
            "retry_count": state.retry_count,
            "pending_approval": state.pending_approval,
            "approval_type": state.approval_type,
            "approval_data": state.approval_data,
        }

    def _deserialize_state(self, data: Dict[str, Any]) -> AgentState:
        """Deserialize dict to AgentState."""
        request = None
        if data.get("request"):
            req_data = data["request"]
            request = UserRequest(
                idea=req_data.get("idea", ""),
                genre=req_data.get("genre", "drama"),
                style=req_data.get("style", ""),
                num_episodes=req_data.get("num_episodes", 1),
                episode_duration=req_data.get("episode_duration", 60),
                num_characters=req_data.get("num_characters", 3),
                target_audience=req_data.get("target_audience", ""),
                target_platform=req_data.get("target_platform", "kling"),
            )

        phase_str = data.get("phase", "init")
        phase = WorkflowPhase(phase_str) if phase_str else WorkflowPhase.INIT

        mode_str = data.get("mode", "interactive")
        mode = InteractionMode(mode_str) if mode_str else InteractionMode.INTERACTIVE

        state = AgentState(
            request=request,
            phase=phase,
            mode=mode,
            current_agent=data.get("current_agent", ""),
            next_agent=data.get("next_agent", ""),
            project_id=data.get("project_id"),
            project_name=data.get("project_name", ""),
            story_outline=data.get("story_outline"),
            characters=data.get("characters", []),
            episodes=data.get("episodes", []),
            current_episode_index=data.get("current_episode_index", 0),
            storyboard=data.get("storyboard", []),
            current_shot_index=data.get("current_shot_index", 0),
            video_prompts=data.get("video_prompts", {}),
            video_tasks=data.get("video_tasks", {}),
            error=data.get("error"),
            retry_count=data.get("retry_count", 0),
            pending_approval=data.get("pending_approval", False),
            approval_type=data.get("approval_type", ""),
            approval_data=data.get("approval_data"),
        )

        return state

    # ==================== Helper Methods ====================

    def _row_to_session(self, row: sqlite3.Row) -> Session:
        """Convert database row to Session object."""
        status_str = row["status"]
        try:
            status = SessionStatus(status_str)
        except ValueError:
            status = SessionStatus.RUNNING

        return Session(
            id=row["id"],
            session_id=row["session_id"],
            user_request=row["user_request"] or "",
            mode=row["mode"] or "interactive",
            current_phase=row["current_phase"] or "init",
            current_agent=row["current_agent"] or "",
            project_id=row["project_id"],
            state_json=row["state_json"] or "{}",
            status=status,
            error_message=row["error_message"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_checkpoint(self, row: sqlite3.Row) -> Checkpoint:
        """Convert database row to Checkpoint object."""
        input_data = {}
        output_data = {}

        if row["input_json"]:
            try:
                input_data = json.loads(row["input_json"])
            except json.JSONDecodeError:
                pass

        if row["output_json"]:
            try:
                output_data = json.loads(row["output_json"])
            except json.JSONDecodeError:
                pass

        return Checkpoint(
            id=row["id"],
            session_id=row["session_id"],
            step_name=row["step_name"],
            phase=row["phase"] or "",
            input_data=input_data,
            output_data=output_data,
            created_at=row["created_at"],
        )
