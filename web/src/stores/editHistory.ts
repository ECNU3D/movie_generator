import { create } from "zustand";

export interface EditHistoryEntry {
  id: string;
  timestamp: number;
  entityType: "outline" | "character" | "shot" | "prompt";
  entityId?: string;
  field: string;
  oldValue: unknown;
  newValue: unknown;
}

interface EditHistoryState {
  // History stacks
  undoStack: EditHistoryEntry[];
  redoStack: EditHistoryEntry[];

  // Max history size
  maxHistorySize: number;

  // Actions
  pushEdit: (entry: Omit<EditHistoryEntry, "id" | "timestamp">) => void;
  undo: () => EditHistoryEntry | null;
  redo: () => EditHistoryEntry | null;
  canUndo: () => boolean;
  canRedo: () => boolean;
  clearHistory: () => void;
  getHistory: () => EditHistoryEntry[];
}

const generateId = () => Math.random().toString(36).substring(2, 9);

export const useEditHistoryStore = create<EditHistoryState>((set, get) => ({
  undoStack: [],
  redoStack: [],
  maxHistorySize: 50,

  pushEdit: (entry) =>
    set((state) => {
      const newEntry: EditHistoryEntry = {
        ...entry,
        id: generateId(),
        timestamp: Date.now(),
      };

      const newStack = [...state.undoStack, newEntry];

      // Trim stack if it exceeds max size
      if (newStack.length > state.maxHistorySize) {
        newStack.shift();
      }

      return {
        undoStack: newStack,
        redoStack: [], // Clear redo stack on new edit
      };
    }),

  undo: () => {
    const state = get();
    if (state.undoStack.length === 0) return null;

    const entry = state.undoStack[state.undoStack.length - 1];

    set({
      undoStack: state.undoStack.slice(0, -1),
      redoStack: [...state.redoStack, entry],
    });

    return entry;
  },

  redo: () => {
    const state = get();
    if (state.redoStack.length === 0) return null;

    const entry = state.redoStack[state.redoStack.length - 1];

    set({
      redoStack: state.redoStack.slice(0, -1),
      undoStack: [...state.undoStack, entry],
    });

    return entry;
  },

  canUndo: () => get().undoStack.length > 0,

  canRedo: () => get().redoStack.length > 0,

  clearHistory: () =>
    set({
      undoStack: [],
      redoStack: [],
    }),

  getHistory: () => get().undoStack,
}));

// Helper hook for using edit history with workflow store
export function useEditHistoryWithWorkflow() {
  const { pushEdit, undo, redo, canUndo, canRedo } = useEditHistoryStore();

  const recordEdit = (
    entityType: EditHistoryEntry["entityType"],
    field: string,
    oldValue: unknown,
    newValue: unknown,
    entityId?: string
  ) => {
    pushEdit({
      entityType,
      entityId,
      field,
      oldValue,
      newValue,
    });
  };

  return {
    recordEdit,
    undo,
    redo,
    canUndo,
    canRedo,
  };
}
