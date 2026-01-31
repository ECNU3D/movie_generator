"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { StoryOutline } from "@/types";

interface StoryOutlineViewProps {
  outline: StoryOutline;
  onEdit?: () => void;
  locale?: "en" | "zh";
}

export function StoryOutlineView({
  outline,
  onEdit,
  locale = "zh",
}: StoryOutlineViewProps) {
  const themeLabel = locale === "zh" ? "主题" : "Theme";
  const synopsisLabel = locale === "zh" ? "故事梗概" : "Synopsis";
  const settingLabel = locale === "zh" ? "背景设定" : "Setting";
  const editLabel = locale === "zh" ? "编辑大纲" : "Edit Outline";

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-xl">{outline.title}</CardTitle>
        <Badge variant="secondary">{outline.genre}</Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-zinc-500 mb-1">{themeLabel}</h4>
          <p className="text-sm">{outline.theme}</p>
        </div>

        <div>
          <h4 className="text-sm font-medium text-zinc-500 mb-1">{synopsisLabel}</h4>
          <p className="text-sm whitespace-pre-wrap">{outline.synopsis}</p>
        </div>

        <div>
          <h4 className="text-sm font-medium text-zinc-500 mb-1">{settingLabel}</h4>
          <p className="text-sm">{outline.setting}</p>
        </div>

        {onEdit && (
          <button
            onClick={onEdit}
            className="text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 underline"
          >
            {editLabel}
          </button>
        )}
      </CardContent>
    </Card>
  );
}
