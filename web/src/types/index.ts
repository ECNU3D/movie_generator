export type WorkflowPhase =
  | "init"
  | "story_outline"
  | "character_design"
  | "episode_writing"
  | "storyboard"
  | "video_prompts"
  | "video_generation"
  | "review"
  | "completed"
  | "error";

export type SessionStatus = "running" | "paused" | "completed" | "failed";

export type VideoTaskStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed";

export interface Character {
  name: string;
  age?: string;
  personality: string;
  appearance: string;
  visual_description: string;
  major_events?: string[];
}

export interface Shot {
  shot_id: string;
  visual_description: string;
  dialogue?: string;
  camera_movement?: string;
  duration: number;
  shot_type?: string;
}

export interface Episode {
  episode_number: number;
  title: string;
  outline: string;
  shots: Shot[];
}

export interface StoryOutline {
  title: string;
  genre: string;
  theme: string;
  synopsis: string;
  setting: string;
}

export interface VideoTask {
  task_id?: string | null;
  shot_id: string;
  status: VideoTaskStatus | "submitted";
  video_url?: string;
  error?: string;
  platform: string;
  progress?: number;
  prompt?: string;
}

export interface Session {
  session_id: string;
  status: SessionStatus;
  phase: WorkflowPhase;
  project_name: string;
  created_at: string;
  updated_at: string;
  error?: string;
}

export interface SessionDetail extends Session {
  story_outline?: StoryOutline;
  characters: Character[];
  episodes: Episode[];
  storyboard: Shot[];
  video_prompts: Record<string, string>;
  video_tasks: Record<string, VideoTask>;
  pending_approval: boolean;
  approval_type: string;
}

export interface CreateSessionRequest {
  idea: string;
  genre: string;
  style?: string;
  num_episodes: number;
  episode_duration: number;
  num_characters: number;
  target_platform: string;
  mode: "interactive" | "autonomous";
}

export interface ApproveRequest {
  approved: boolean;
  feedback?: string;
  edits?: Record<string, unknown>;
}

export interface WebSocketMessage {
  type: string;
  sessionId?: string;
  phase?: string;
  data?: unknown;
  message?: string;
  progress?: number;
  shotId?: string;
  status?: string;
  url?: string;
  approvalType?: string;
  projectName?: string;
  summary?: unknown;
}
