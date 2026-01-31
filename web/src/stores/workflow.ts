import { create } from "zustand";
import type {
  SessionStatus,
  WorkflowPhase,
  StoryOutline,
  Character,
  Episode,
  Shot,
  VideoTask,
} from "@/types";

interface WorkflowState {
  // Session info
  sessionId: string | null;
  status: SessionStatus | "idle";
  phase: WorkflowPhase;
  projectName: string;

  // Workflow data
  storyOutline: StoryOutline | null;
  characters: Character[];
  episodes: Episode[];
  storyboard: Shot[];
  videoPrompts: Record<string, string>;
  videoTasks: Record<string, VideoTask>;

  // Approval state
  pendingApproval: boolean;
  approvalType: string;

  // Progress
  progress: number;
  progressMessage: string;

  // Error
  error: string | null;

  // Actions
  setSession: (sessionId: string, projectName?: string) => void;
  setStatus: (status: SessionStatus | "idle") => void;
  updatePhase: (phase: WorkflowPhase) => void;
  setStoryOutline: (outline: StoryOutline) => void;
  setCharacters: (characters: Character[]) => void;
  updateCharacter: (index: number, character: Character) => void;
  addCharacter: (character: Character) => void;
  removeCharacter: (index: number) => void;
  setEpisodes: (episodes: Episode[]) => void;
  updateEpisode: (index: number, episode: Episode) => void;
  setStoryboard: (shots: Shot[]) => void;
  updateShot: (index: number, shot: Shot) => void;
  setVideoPrompts: (prompts: Record<string, string>) => void;
  updateVideoPrompt: (shotId: string, prompt: string) => void;
  setVideoTasks: (tasks: Record<string, VideoTask>) => void;
  updateVideoTask: (shotId: string, task: VideoTask) => void;
  setApproval: (pending: boolean, type: string) => void;
  setProgress: (progress: number, message?: string) => void;
  setError: (error: string | null) => void;
  reset: () => void;
  loadFromSession: (data: {
    session_id: string;
    status: SessionStatus;
    phase: WorkflowPhase;
    project_name: string;
    story_outline?: StoryOutline;
    characters: Character[];
    episodes: Episode[];
    storyboard: Shot[];
    video_prompts: Record<string, string>;
    video_tasks: Record<string, VideoTask>;
    pending_approval: boolean;
    approval_type: string;
  }) => void;
}

const initialState = {
  sessionId: null,
  status: "idle" as const,
  phase: "init" as WorkflowPhase,
  projectName: "",
  storyOutline: null,
  characters: [],
  episodes: [],
  storyboard: [],
  videoPrompts: {},
  videoTasks: {},
  pendingApproval: false,
  approvalType: "",
  progress: 0,
  progressMessage: "",
  error: null,
};

export const useWorkflowStore = create<WorkflowState>((set) => ({
  ...initialState,

  setSession: (sessionId, projectName = "") =>
    set({ sessionId, projectName }),

  setStatus: (status) => set({ status }),

  updatePhase: (phase) => set({ phase }),

  setStoryOutline: (outline) => set({ storyOutline: outline }),

  setCharacters: (characters) => set({ characters }),

  updateCharacter: (index, character) =>
    set((state) => ({
      characters: state.characters.map((c, i) =>
        i === index ? character : c
      ),
    })),

  addCharacter: (character) =>
    set((state) => ({
      characters: [...state.characters, character],
    })),

  removeCharacter: (index) =>
    set((state) => ({
      characters: state.characters.filter((_, i) => i !== index),
    })),

  setEpisodes: (episodes) => set({ episodes }),

  updateEpisode: (index, episode) =>
    set((state) => ({
      episodes: state.episodes.map((e, i) => (i === index ? episode : e)),
    })),

  setStoryboard: (shots) => set({ storyboard: shots }),

  updateShot: (index, shot) =>
    set((state) => ({
      storyboard: state.storyboard.map((s, i) => (i === index ? shot : s)),
    })),

  setVideoPrompts: (prompts) => set({ videoPrompts: prompts }),

  updateVideoPrompt: (shotId, prompt) =>
    set((state) => ({
      videoPrompts: { ...state.videoPrompts, [shotId]: prompt },
    })),

  setVideoTasks: (tasks) => set({ videoTasks: tasks }),

  updateVideoTask: (shotId, task) =>
    set((state) => ({
      videoTasks: { ...state.videoTasks, [shotId]: task },
    })),

  setApproval: (pending, type) =>
    set({ pendingApproval: pending, approvalType: type }),

  setProgress: (progress, message = "") =>
    set({ progress, progressMessage: message }),

  setError: (error) => set({ error }),

  reset: () => set(initialState),

  loadFromSession: (data) =>
    set({
      sessionId: data.session_id,
      status: data.status,
      phase: data.phase,
      projectName: data.project_name,
      storyOutline: data.story_outline || null,
      characters: data.characters,
      episodes: data.episodes,
      storyboard: data.storyboard,
      videoPrompts: data.video_prompts,
      videoTasks: data.video_tasks,
      pendingApproval: data.pending_approval,
      approvalType: data.approval_type,
    }),
}));
