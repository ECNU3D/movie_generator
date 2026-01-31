"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import {
  Film,
  Clock,
  Camera,
  Edit2,
  Save,
  X,
  Copy,
  Check,
} from "lucide-react";
import type { Shot } from "@/types";

const SHOT_TYPES_ZH = [
  { value: "wide", label: "远景" },
  { value: "medium", label: "中景" },
  { value: "close", label: "特写" },
  { value: "tracking", label: "跟踪" },
  { value: "pov", label: "主观" },
];

const SHOT_TYPES_EN = [
  { value: "wide", label: "Wide" },
  { value: "medium", label: "Medium" },
  { value: "close", label: "Close-up" },
  { value: "tracking", label: "Tracking" },
  { value: "pov", label: "POV" },
];

const CAMERA_MOVEMENTS_ZH = [
  { value: "static", label: "静止" },
  { value: "pan", label: "横摇" },
  { value: "tilt", label: "俯仰" },
  { value: "zoom_in", label: "推进" },
  { value: "zoom_out", label: "拉远" },
  { value: "tracking", label: "跟踪" },
  { value: "crane", label: "升降" },
];

const CAMERA_MOVEMENTS_EN = [
  { value: "static", label: "Static" },
  { value: "pan", label: "Pan" },
  { value: "tilt", label: "Tilt" },
  { value: "zoom_in", label: "Zoom In" },
  { value: "zoom_out", label: "Zoom Out" },
  { value: "tracking", label: "Tracking" },
  { value: "crane", label: "Crane" },
];

interface ShotCardProps {
  shot: Shot;
  index: number;
  isSelected?: boolean;
  onSelect?: () => void;
  onEdit?: (shot: Shot) => void;
  videoPrompt?: string;
  onCopyPrompt?: () => void;
  locale?: "en" | "zh";
}

export function ShotCard({
  shot,
  index,
  isSelected,
  onSelect,
  onEdit,
  videoPrompt,
  onCopyPrompt,
  locale = "zh",
}: ShotCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState(shot);
  const [copied, setCopied] = useState(false);

  const SHOT_TYPES = locale === "zh" ? SHOT_TYPES_ZH : SHOT_TYPES_EN;
  const CAMERA_MOVEMENTS = locale === "zh" ? CAMERA_MOVEMENTS_ZH : CAMERA_MOVEMENTS_EN;

  // Localized labels
  const editShotLabel = locale === "zh" ? "编辑镜头" : "Edit Shot";
  const durationLabel = locale === "zh" ? "时长 (秒)" : "Duration (s)";
  const shotTypeLabel = locale === "zh" ? "镜头类型" : "Shot Type";
  const cameraMovementLabel = locale === "zh" ? "镜头运动" : "Camera Movement";
  const visualDescLabel = locale === "zh" ? "画面描述" : "Visual Description";
  const dialogueLabel = locale === "zh" ? "对白" : "Dialogue";
  const dialoguePlaceholder = locale === "zh" ? "角色对白（可选）" : "Character dialogue (optional)";
  const saveLabel = locale === "zh" ? "保存" : "Save";
  const cancelLabel = locale === "zh" ? "取消" : "Cancel";
  const editLabel = locale === "zh" ? "编辑" : "Edit";
  const copiedLabel = locale === "zh" ? "已复制" : "Copied";
  const copyPromptLabel = locale === "zh" ? "复制提示词" : "Copy Prompt";
  const shotLabel = locale === "zh" ? "镜头" : "Shot";
  const secondLabel = locale === "zh" ? "秒" : "s";

  const handleSave = () => {
    onEdit?.(editData);
    setIsEditing(false);
  };

  const handleCopy = () => {
    if (videoPrompt) {
      navigator.clipboard.writeText(videoPrompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      onCopyPrompt?.();
    }
  };

  if (isEditing) {
    return (
      <Card className="border-2 border-zinc-900 dark:border-zinc-100">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">{editShotLabel} {index + 1}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>{durationLabel}</Label>
              <Input
                type="number"
                value={editData.duration}
                onChange={(e) =>
                  setEditData({
                    ...editData,
                    duration: parseInt(e.target.value) || 5,
                  })
                }
                min={1}
                max={30}
              />
            </div>
            <div className="space-y-2">
              <Label>{shotTypeLabel}</Label>
              <Select
                value={editData.shot_type || "medium"}
                onChange={(e) =>
                  setEditData({ ...editData, shot_type: e.target.value })
                }
                options={SHOT_TYPES}
              />
            </div>
            <div className="space-y-2">
              <Label>{cameraMovementLabel}</Label>
              <Select
                value={editData.camera_movement || "static"}
                onChange={(e) =>
                  setEditData({ ...editData, camera_movement: e.target.value })
                }
                options={CAMERA_MOVEMENTS}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>{visualDescLabel}</Label>
            <Textarea
              value={editData.visual_description}
              onChange={(e) =>
                setEditData({
                  ...editData,
                  visual_description: e.target.value,
                })
              }
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label>{dialogueLabel}</Label>
            <Textarea
              value={editData.dialogue || ""}
              onChange={(e) =>
                setEditData({ ...editData, dialogue: e.target.value })
              }
              rows={2}
              placeholder={dialoguePlaceholder}
            />
          </div>

          <div className="flex gap-2">
            <Button onClick={handleSave} size="sm">
              <Save className="w-4 h-4 mr-1" />
              {saveLabel}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setEditData(shot);
                setIsEditing(false);
              }}
              size="sm"
            >
              <X className="w-4 h-4 mr-1" />
              {cancelLabel}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        "cursor-pointer transition-all duration-200 hover:shadow-md",
        isSelected && "ring-2 ring-zinc-900 dark:ring-zinc-100"
      )}
      onClick={onSelect}
    >
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <Film className="w-4 h-4" />
            {shotLabel} {index + 1}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs">
              <Clock className="w-3 h-3 mr-1" />
              {shot.duration}{secondLabel}
            </Badge>
            {shot.shot_type && (
              <Badge variant="outline" className="text-xs">
                {SHOT_TYPES.find((t) => t.value === shot.shot_type)?.label ||
                  shot.shot_type}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-sm text-zinc-600 dark:text-zinc-400 line-clamp-2">
          {shot.visual_description}
        </p>

        {shot.camera_movement && (
          <div className="flex items-center gap-1 text-xs text-zinc-500">
            <Camera className="w-3 h-3" />
            {CAMERA_MOVEMENTS.find((m) => m.value === shot.camera_movement)
              ?.label || shot.camera_movement}
          </div>
        )}

        {shot.dialogue && (
          <p className="text-xs text-zinc-500 italic line-clamp-1">
            &ldquo;{shot.dialogue}&rdquo;
          </p>
        )}

        <div className="flex gap-2 pt-2" onClick={(e) => e.stopPropagation()}>
          {onEdit && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsEditing(true)}
            >
              <Edit2 className="w-3 h-3 mr-1" />
              {editLabel}
            </Button>
          )}
          {videoPrompt && (
            <Button variant="ghost" size="sm" onClick={handleCopy}>
              {copied ? (
                <Check className="w-3 h-3 mr-1" />
              ) : (
                <Copy className="w-3 h-3 mr-1" />
              )}
              {copied ? copiedLabel : copyPromptLabel}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

interface StoryboardGridProps {
  shots: Shot[];
  selectedIndex?: number;
  onSelect?: (index: number) => void;
  onEdit?: (index: number, shot: Shot) => void;
  videoPrompts?: Record<string, string>;
  locale?: "en" | "zh";
}

export function StoryboardGrid({
  shots,
  selectedIndex,
  onSelect,
  onEdit,
  videoPrompts = {},
  locale = "zh",
}: StoryboardGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {shots.map((shot, index) => (
        <ShotCard
          key={shot.shot_id || index}
          shot={shot}
          index={index}
          isSelected={selectedIndex === index}
          onSelect={() => onSelect?.(index)}
          onEdit={onEdit ? (s) => onEdit(index, s) : undefined}
          videoPrompt={videoPrompts[shot.shot_id]}
          locale={locale}
        />
      ))}
    </div>
  );
}
