"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Edit2, Save, X, BookOpen, Sparkles } from "lucide-react";
import type { StoryOutline } from "@/types";

interface StoryOutlineEditorProps {
  outline: StoryOutline;
  onSave?: (outline: StoryOutline) => void;
  onAiEnhance?: (outline: StoryOutline) => Promise<StoryOutline>;
  editable?: boolean;
  locale?: "en" | "zh";
}

export function StoryOutlineEditor({
  outline,
  onSave,
  onAiEnhance,
  editable = true,
  locale = "zh",
}: StoryOutlineEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<StoryOutline>(outline);
  const [isEnhancing, setIsEnhancing] = useState(false);

  // Localized labels
  const labels = {
    storyOutline: locale === "zh" ? "故事大纲" : "Story Outline",
    title: locale === "zh" ? "标题" : "Title",
    genre: locale === "zh" ? "类型" : "Genre",
    theme: locale === "zh" ? "主题" : "Theme",
    synopsis: locale === "zh" ? "故事简介" : "Synopsis",
    setting: locale === "zh" ? "背景设定" : "Setting",
    edit: locale === "zh" ? "编辑" : "Edit",
    save: locale === "zh" ? "保存" : "Save",
    cancel: locale === "zh" ? "取消" : "Cancel",
    aiEnhance: locale === "zh" ? "AI 优化" : "AI Enhance",
    enhancing: locale === "zh" ? "优化中..." : "Enhancing...",
    titlePlaceholder: locale === "zh" ? "输入故事标题" : "Enter story title",
    themePlaceholder: locale === "zh" ? "输入故事主题" : "Enter story theme",
    synopsisPlaceholder:
      locale === "zh" ? "描述故事的主要情节..." : "Describe the main plot...",
    settingPlaceholder:
      locale === "zh"
        ? "描述故事发生的时间、地点和环境..."
        : "Describe time, place and environment...",
  };

  const handleSave = () => {
    onSave?.(editData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData(outline);
    setIsEditing(false);
  };

  const handleAiEnhance = async () => {
    if (!onAiEnhance) return;

    setIsEnhancing(true);
    try {
      const enhanced = await onAiEnhance(editData);
      setEditData(enhanced);
    } catch (error) {
      console.error("AI enhancement failed:", error);
    } finally {
      setIsEnhancing(false);
    }
  };

  if (isEditing) {
    return (
      <Card className="border-2 border-primary">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            {labels.storyOutline}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>{labels.title}</Label>
              <Input
                value={editData.title}
                onChange={(e) =>
                  setEditData({ ...editData, title: e.target.value })
                }
                placeholder={labels.titlePlaceholder}
              />
            </div>
            <div className="space-y-2">
              <Label>{labels.genre}</Label>
              <Input
                value={editData.genre}
                onChange={(e) =>
                  setEditData({ ...editData, genre: e.target.value })
                }
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>{labels.theme}</Label>
            <Input
              value={editData.theme}
              onChange={(e) =>
                setEditData({ ...editData, theme: e.target.value })
              }
              placeholder={labels.themePlaceholder}
            />
          </div>

          <div className="space-y-2">
            <Label>{labels.synopsis}</Label>
            <Textarea
              value={editData.synopsis}
              onChange={(e) =>
                setEditData({ ...editData, synopsis: e.target.value })
              }
              rows={4}
              placeholder={labels.synopsisPlaceholder}
            />
          </div>

          <div className="space-y-2">
            <Label>{labels.setting}</Label>
            <Textarea
              value={editData.setting}
              onChange={(e) =>
                setEditData({ ...editData, setting: e.target.value })
              }
              rows={3}
              placeholder={labels.settingPlaceholder}
            />
          </div>

          <div className="flex gap-2">
            <Button onClick={handleSave}>
              <Save className="w-4 h-4 mr-1" />
              {labels.save}
            </Button>
            <Button variant="outline" onClick={handleCancel}>
              <X className="w-4 h-4 mr-1" />
              {labels.cancel}
            </Button>
            {onAiEnhance && (
              <Button
                variant="secondary"
                onClick={handleAiEnhance}
                disabled={isEnhancing}
              >
                <Sparkles className="w-4 h-4 mr-1" />
                {isEnhancing ? labels.enhancing : labels.aiEnhance}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5" />
            {outline.title}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">{outline.genre}</Badge>
            {editable && onSave && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsEditing(true)}
              >
                <Edit2 className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {outline.theme && (
          <div>
            <h4 className="text-sm font-medium text-zinc-500 mb-1">
              {labels.theme}
            </h4>
            <p className="text-sm">{outline.theme}</p>
          </div>
        )}

        <div>
          <h4 className="text-sm font-medium text-zinc-500 mb-1">
            {labels.synopsis}
          </h4>
          <p className="text-sm whitespace-pre-wrap">{outline.synopsis}</p>
        </div>

        {outline.setting && (
          <div>
            <h4 className="text-sm font-medium text-zinc-500 mb-1">
              {labels.setting}
            </h4>
            <p className="text-sm whitespace-pre-wrap">{outline.setting}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
