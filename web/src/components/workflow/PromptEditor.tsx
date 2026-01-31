"use client";

import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Edit2,
  Save,
  X,
  Wand2,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from "lucide-react";
import type { Shot } from "@/types";

interface PromptEditorProps {
  shot: Shot;
  prompt: string;
  onSave?: (prompt: string) => void;
  onAiSuggest?: (shot: Shot) => Promise<string>;
  characterNames?: string[];
  locale?: "en" | "zh";
}

export function PromptEditor({
  shot,
  prompt,
  onSave,
  onAiSuggest,
  characterNames = [],
  locale = "zh",
}: PromptEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedPrompt, setEditedPrompt] = useState(prompt);
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  // Localized labels
  const labels = {
    videoPrompt: locale === "zh" ? "视频提示词" : "Video Prompt",
    edit: locale === "zh" ? "编辑" : "Edit",
    save: locale === "zh" ? "保存" : "Save",
    cancel: locale === "zh" ? "取消" : "Cancel",
    aiSuggest: locale === "zh" ? "AI 优化" : "AI Suggest",
    copy: locale === "zh" ? "复制" : "Copy",
    copied: locale === "zh" ? "已复制" : "Copied",
    expand: locale === "zh" ? "展开" : "Expand",
    collapse: locale === "zh" ? "收起" : "Collapse",
    noPrompt: locale === "zh" ? "暂无提示词" : "No prompt yet",
    generating: locale === "zh" ? "生成中..." : "Generating...",
    characters: locale === "zh" ? "角色" : "Characters",
    shotInfo: locale === "zh" ? "镜头信息" : "Shot Info",
  };

  const handleSave = () => {
    onSave?.(editedPrompt);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedPrompt(prompt);
    setIsEditing(false);
  };

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(prompt || editedPrompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [prompt, editedPrompt]);

  const handleAiSuggest = async () => {
    if (!onAiSuggest) return;

    setIsGenerating(true);
    try {
      const suggested = await onAiSuggest(shot);
      setEditedPrompt(suggested);
    } catch (error) {
      console.error("AI suggestion failed:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Highlight character names in prompt
  const highlightCharacters = (text: string) => {
    if (!characterNames.length) return text;

    let result = text;
    characterNames.forEach((name) => {
      const regex = new RegExp(`(${name})`, "gi");
      result = result.replace(regex, `**$1**`);
    });
    return result;
  };

  const displayPrompt = prompt || editedPrompt;
  const shouldTruncate = displayPrompt.length > 200;

  if (isEditing) {
    return (
      <Card className="border-2 border-primary">
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Wand2 className="w-4 h-4" />
            {labels.videoPrompt}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Shot context */}
          <div className="p-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg space-y-2">
            <div className="text-xs font-medium text-zinc-500">
              {labels.shotInfo}
            </div>
            <p className="text-sm">{shot.visual_description}</p>
            {shot.dialogue && (
              <p className="text-xs italic text-zinc-500">
                &ldquo;{shot.dialogue}&rdquo;
              </p>
            )}
          </div>

          {/* Character badges */}
          {characterNames.length > 0 && (
            <div className="flex flex-wrap gap-1">
              <span className="text-xs text-zinc-500">{labels.characters}:</span>
              {characterNames.map((name) => (
                <Badge
                  key={name}
                  variant="secondary"
                  className="text-xs cursor-pointer hover:bg-primary hover:text-primary-foreground"
                  onClick={() => {
                    setEditedPrompt((prev) =>
                      prev.includes(name) ? prev : `${prev} ${name}`
                    );
                  }}
                >
                  {name}
                </Badge>
              ))}
            </div>
          )}

          {/* Prompt textarea */}
          <Textarea
            value={editedPrompt}
            onChange={(e) => setEditedPrompt(e.target.value)}
            rows={6}
            className="font-mono text-sm"
            placeholder={
              locale === "zh"
                ? "输入视频生成提示词..."
                : "Enter video generation prompt..."
            }
          />

          {/* Actions */}
          <div className="flex gap-2">
            <Button onClick={handleSave} size="sm">
              <Save className="w-4 h-4 mr-1" />
              {labels.save}
            </Button>
            <Button variant="outline" onClick={handleCancel} size="sm">
              <X className="w-4 h-4 mr-1" />
              {labels.cancel}
            </Button>
            {onAiSuggest && (
              <Button
                variant="secondary"
                onClick={handleAiSuggest}
                size="sm"
                disabled={isGenerating}
              >
                <Sparkles className="w-4 h-4 mr-1" />
                {isGenerating ? labels.generating : labels.aiSuggest}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Wand2 className="w-4 h-4" />
            {labels.videoPrompt}
          </CardTitle>
          <div className="flex gap-1">
            {displayPrompt && (
              <Button variant="ghost" size="sm" onClick={handleCopy}>
                {copied ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </Button>
            )}
            {onSave && (
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
      <CardContent>
        {displayPrompt ? (
          <div className="space-y-2">
            <p
              className={`text-sm font-mono whitespace-pre-wrap ${
                shouldTruncate && !isExpanded ? "line-clamp-4" : ""
              }`}
            >
              {highlightCharacters(displayPrompt)}
            </p>
            {shouldTruncate && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-xs"
              >
                {isExpanded ? (
                  <>
                    <ChevronUp className="w-3 h-3 mr-1" />
                    {labels.collapse}
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3 mr-1" />
                    {labels.expand}
                  </>
                )}
              </Button>
            )}
          </div>
        ) : (
          <p className="text-sm text-zinc-400 italic">{labels.noPrompt}</p>
        )}
      </CardContent>
    </Card>
  );
}

interface PromptListProps {
  shots: Shot[];
  prompts: Record<string, string>;
  onSave?: (shotId: string, prompt: string) => void;
  onAiSuggest?: (shot: Shot) => Promise<string>;
  characterNames?: string[];
  locale?: "en" | "zh";
}

export function PromptList({
  shots,
  prompts,
  onSave,
  onAiSuggest,
  characterNames = [],
  locale = "zh",
}: PromptListProps) {
  const promptListLabel = locale === "zh" ? "视频提示词列表" : "Video Prompts";
  const totalLabel = locale === "zh" ? "个镜头" : "shots";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium">
          {promptListLabel} ({shots.length} {totalLabel})
        </h3>
      </div>
      <div className="space-y-4">
        {shots.map((shot, index) => (
          <div key={shot.shot_id || index} className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-zinc-500">
              <Badge variant="outline">
                {locale === "zh" ? "镜头" : "Shot"} {index + 1}
              </Badge>
              <span className="line-clamp-1">{shot.visual_description}</span>
            </div>
            <PromptEditor
              shot={shot}
              prompt={prompts[shot.shot_id] || ""}
              onSave={onSave ? (p) => onSave(shot.shot_id, p) : undefined}
              onAiSuggest={onAiSuggest}
              characterNames={characterNames}
              locale={locale}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
