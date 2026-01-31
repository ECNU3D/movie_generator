"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Undo2, Redo2, History, Trash2 } from "lucide-react";
import { useEditHistoryStore, type EditHistoryEntry } from "@/stores/editHistory";

interface EditHistoryPanelProps {
  onUndo?: (entry: EditHistoryEntry) => void;
  onRedo?: (entry: EditHistoryEntry) => void;
  locale?: "en" | "zh";
}

export function EditHistoryPanel({
  onUndo,
  onRedo,
  locale = "zh",
}: EditHistoryPanelProps) {
  const { undoStack, redoStack, undo, redo, canUndo, canRedo, clearHistory } =
    useEditHistoryStore();

  const labels = {
    editHistory: locale === "zh" ? "编辑历史" : "Edit History",
    undo: locale === "zh" ? "撤销" : "Undo",
    redo: locale === "zh" ? "重做" : "Redo",
    clear: locale === "zh" ? "清空" : "Clear",
    noHistory: locale === "zh" ? "暂无编辑历史" : "No edit history",
    outline: locale === "zh" ? "大纲" : "Outline",
    character: locale === "zh" ? "角色" : "Character",
    shot: locale === "zh" ? "镜头" : "Shot",
    prompt: locale === "zh" ? "提示词" : "Prompt",
    edited: locale === "zh" ? "已编辑" : "edited",
  };

  const getEntityLabel = (type: string) => {
    switch (type) {
      case "outline":
        return labels.outline;
      case "character":
        return labels.character;
      case "shot":
        return labels.shot;
      case "prompt":
        return labels.prompt;
      default:
        return type;
    }
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString(locale === "zh" ? "zh-CN" : "en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleUndo = () => {
    const entry = undo();
    if (entry && onUndo) {
      onUndo(entry);
    }
  };

  const handleRedo = () => {
    const entry = redo();
    if (entry && onRedo) {
      onRedo(entry);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <History className="w-4 h-4" />
            {labels.editHistory}
          </CardTitle>
          <div className="flex gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleUndo}
              disabled={!canUndo()}
              title={labels.undo}
            >
              <Undo2 className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRedo}
              disabled={!canRedo()}
              title={labels.redo}
            >
              <Redo2 className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearHistory}
              disabled={undoStack.length === 0 && redoStack.length === 0}
              title={labels.clear}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {undoStack.length === 0 ? (
          <p className="text-sm text-zinc-400 text-center py-4">
            {labels.noHistory}
          </p>
        ) : (
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {[...undoStack].reverse().map((entry, index) => (
              <div
                key={entry.id}
                className={`flex items-center justify-between p-2 rounded text-sm ${
                  index === 0
                    ? "bg-zinc-100 dark:bg-zinc-800"
                    : "text-zinc-500"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    {getEntityLabel(entry.entityType)}
                  </Badge>
                  <span>
                    {entry.field} {labels.edited}
                  </span>
                </div>
                <span className="text-xs text-zinc-400">
                  {formatTime(entry.timestamp)}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Floating toolbar for quick undo/redo access
interface UndoRedoToolbarProps {
  onUndo?: (entry: EditHistoryEntry) => void;
  onRedo?: (entry: EditHistoryEntry) => void;
  locale?: "en" | "zh";
}

export function UndoRedoToolbar({
  onUndo,
  onRedo,
  locale = "zh",
}: UndoRedoToolbarProps) {
  const { undo, redo, canUndo, canRedo } = useEditHistoryStore();

  const handleUndo = () => {
    const entry = undo();
    if (entry && onUndo) {
      onUndo(entry);
    }
  };

  const handleRedo = () => {
    const entry = redo();
    if (entry && onRedo) {
      onRedo(entry);
    }
  };

  // Don't show if no history
  if (!canUndo() && !canRedo()) {
    return null;
  }

  return (
    <div className="fixed bottom-6 right-6 flex gap-2 bg-white dark:bg-zinc-900 shadow-lg rounded-full px-3 py-2 border border-zinc-200 dark:border-zinc-700">
      <Button
        variant="ghost"
        size="sm"
        onClick={handleUndo}
        disabled={!canUndo()}
        className="rounded-full"
      >
        <Undo2 className="w-4 h-4" />
        <span className="ml-1 text-xs">
          {locale === "zh" ? "撤销" : "Undo"}
        </span>
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleRedo}
        disabled={!canRedo()}
        className="rounded-full"
      >
        <Redo2 className="w-4 h-4" />
        <span className="ml-1 text-xs">
          {locale === "zh" ? "重做" : "Redo"}
        </span>
      </Button>
    </div>
  );
}
