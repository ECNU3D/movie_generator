"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import {
  RefreshCw,
  Download,
  Play,
  Edit2,
  GitCompare,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  X,
  Save,
} from "lucide-react";
import { VideoPlayer, VideoModal } from "./VideoPlayer";
import type { VideoTask, Shot } from "@/types";

interface VideoManagerProps {
  sessionId: string;
  shots: Shot[];
  videoTasks: Record<string, VideoTask>;
  videoPrompts: Record<string, string>;
  platforms?: string[];
  onRefresh?: () => void;
  onDownload?: (shotId: string) => void;
  onDownloadAll?: () => void;
  onRetry?: (shotId: string, platform?: string) => void;
  onUpdatePrompt?: (shotId: string, prompt: string) => void;
  onCompare?: (shotIds: string[], platforms: string[]) => void;
  locale?: "en" | "zh";
}

export function VideoManager({
  shots,
  videoTasks,
  videoPrompts,
  platforms = ["kling", "hailuo", "jimeng", "tongyi"],
  onRefresh,
  onDownload,
  onDownloadAll,
  onRetry,
  onUpdatePrompt,
  onCompare,
  locale = "zh",
}: VideoManagerProps) {
  const [selectedShot, setSelectedShot] = useState<string | null>(null);
  const [editingPrompt, setEditingPrompt] = useState<string | null>(null);
  const [editedPromptText, setEditedPromptText] = useState("");
  const [selectedPlatform, setSelectedPlatform] = useState(platforms[0]);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState<string[]>([]);
  const [comparePlatforms, setComparePlatforms] = useState<string[]>([]);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const labels = {
    videoManager: locale === "zh" ? "视频管理" : "Video Management",
    refresh: locale === "zh" ? "刷新状态" : "Refresh Status",
    downloadAll: locale === "zh" ? "下载全部" : "Download All",
    compareMode: locale === "zh" ? "多平台对比" : "Compare Platforms",
    exitCompare: locale === "zh" ? "退出对比" : "Exit Compare",
    startCompare: locale === "zh" ? "开始对比" : "Start Compare",
    selectPlatforms: locale === "zh" ? "选择平台" : "Select Platforms",
    shot: locale === "zh" ? "镜头" : "Shot",
    completed: locale === "zh" ? "已完成" : "Completed",
    processing: locale === "zh" ? "生成中" : "Processing",
    failed: locale === "zh" ? "失败" : "Failed",
    pending: locale === "zh" ? "等待中" : "Pending",
    download: locale === "zh" ? "下载" : "Download",
    retry: locale === "zh" ? "重试" : "Retry",
    editPrompt: locale === "zh" ? "编辑提示词" : "Edit Prompt",
    play: locale === "zh" ? "播放" : "Play",
    save: locale === "zh" ? "保存" : "Save",
    cancel: locale === "zh" ? "取消" : "Cancel",
    retryWith: locale === "zh" ? "使用平台重试" : "Retry with platform",
    prompt: locale === "zh" ? "提示词" : "Prompt",
    totalProgress: locale === "zh" ? "总进度" : "Total Progress",
  };

  const PLATFORM_NAMES: Record<string, string> =
    locale === "zh"
      ? {
          kling: "可灵",
          hailuo: "海螺",
          jimeng: "即梦",
          tongyi: "通义万相",
        }
      : {
          kling: "Kling",
          hailuo: "Hailuo",
          jimeng: "Jimeng",
          tongyi: "Tongyi",
        };

  const completedCount = Object.values(videoTasks).filter(
    (t) => t.status === "completed"
  ).length;
  const totalCount = shots.length;

  const handleEditPrompt = (shotId: string) => {
    setEditingPrompt(shotId);
    setEditedPromptText(videoPrompts[shotId] || "");
  };

  const handleSavePrompt = () => {
    if (editingPrompt && onUpdatePrompt) {
      onUpdatePrompt(editingPrompt, editedPromptText);
    }
    setEditingPrompt(null);
    setEditedPromptText("");
  };

  const handleRetryWithPlatform = (shotId: string) => {
    onRetry?.(shotId, selectedPlatform);
  };

  const handleToggleCompare = (shotId: string) => {
    setSelectedForCompare((prev) =>
      prev.includes(shotId)
        ? prev.filter((id) => id !== shotId)
        : [...prev, shotId]
    );
  };

  const handleStartCompare = () => {
    if (selectedForCompare.length > 0 && comparePlatforms.length > 0) {
      onCompare?.(selectedForCompare, comparePlatforms);
      setCompareMode(false);
      setSelectedForCompare([]);
      setComparePlatforms([]);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <Badge variant="success">
            <CheckCircle className="w-3 h-3 mr-1" />
            {labels.completed}
          </Badge>
        );
      case "processing":
        return (
          <Badge variant="info">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            {labels.processing}
          </Badge>
        );
      case "failed":
        return (
          <Badge variant="destructive">
            <XCircle className="w-3 h-3 mr-1" />
            {labels.failed}
          </Badge>
        );
      default:
        return (
          <Badge variant="secondary">
            <Clock className="w-3 h-3 mr-1" />
            {labels.pending}
          </Badge>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with controls */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Play className="w-5 h-5" />
              {labels.videoManager}
            </CardTitle>
            <div className="flex gap-2">
              {onRefresh && (
                <Button variant="outline" size="sm" onClick={onRefresh}>
                  <RefreshCw className="w-4 h-4 mr-1" />
                  {labels.refresh}
                </Button>
              )}
              {onDownloadAll && completedCount > 0 && (
                <Button variant="outline" size="sm" onClick={onDownloadAll}>
                  <Download className="w-4 h-4 mr-1" />
                  {labels.downloadAll}
                </Button>
              )}
              {onCompare && (
                <Button
                  variant={compareMode ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setCompareMode(!compareMode)}
                >
                  <GitCompare className="w-4 h-4 mr-1" />
                  {compareMode ? labels.exitCompare : labels.compareMode}
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Progress bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>
                {labels.totalProgress}: {completedCount}/{totalCount}
              </span>
              <span>
                {totalCount > 0
                  ? Math.round((completedCount / totalCount) * 100)
                  : 0}
                %
              </span>
            </div>
            <div className="h-2 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all duration-300"
                style={{
                  width: `${
                    totalCount > 0 ? (completedCount / totalCount) * 100 : 0
                  }%`,
                }}
              />
            </div>
          </div>

          {/* Compare mode controls */}
          {compareMode && (
            <div className="mt-4 p-4 bg-zinc-50 dark:bg-zinc-900 rounded-lg space-y-3">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <Label className="text-sm">{labels.selectPlatforms}</Label>
                  <div className="flex gap-2 mt-1">
                    {platforms.map((platform) => (
                      <Button
                        key={platform}
                        variant={
                          comparePlatforms.includes(platform)
                            ? "default"
                            : "outline"
                        }
                        size="sm"
                        onClick={() =>
                          setComparePlatforms((prev) =>
                            prev.includes(platform)
                              ? prev.filter((p) => p !== platform)
                              : [...prev, platform]
                          )
                        }
                      >
                        {PLATFORM_NAMES[platform]}
                      </Button>
                    ))}
                  </div>
                </div>
                <Button
                  onClick={handleStartCompare}
                  disabled={
                    selectedForCompare.length === 0 ||
                    comparePlatforms.length === 0
                  }
                >
                  <GitCompare className="w-4 h-4 mr-1" />
                  {labels.startCompare} ({selectedForCompare.length})
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Video grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {shots.map((shot, index) => {
          const task = videoTasks[shot.shot_id];
          const isSelected = selectedForCompare.includes(shot.shot_id);

          return (
            <Card
              key={shot.shot_id}
              className={`relative ${
                compareMode
                  ? "cursor-pointer hover:ring-2 hover:ring-primary"
                  : ""
              } ${isSelected ? "ring-2 ring-primary" : ""}`}
              onClick={
                compareMode
                  ? () => handleToggleCompare(shot.shot_id)
                  : undefined
              }
            >
              {compareMode && isSelected && (
                <div className="absolute top-2 right-2 z-10 bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
                  {selectedForCompare.indexOf(shot.shot_id) + 1}
                </div>
              )}

              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">
                    {labels.shot} {index + 1}
                  </CardTitle>
                  {task && getStatusBadge(task.status)}
                </div>
              </CardHeader>

              <CardContent className="space-y-3">
                {/* Video preview */}
                <div
                  className={`aspect-video rounded-lg flex items-center justify-center ${
                    task?.status === "completed"
                      ? "bg-zinc-900 cursor-pointer hover:bg-zinc-800"
                      : "bg-zinc-100 dark:bg-zinc-800"
                  }`}
                  onClick={
                    task?.status === "completed" && task?.video_url
                      ? (e) => {
                          e.stopPropagation();
                          setPreviewUrl(task.video_url || null);
                        }
                      : undefined
                  }
                >
                  {task?.status === "completed" ? (
                    <Play className="w-12 h-12 text-white opacity-80" />
                  ) : task?.status === "processing" ? (
                    <div className="text-center">
                      <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto" />
                      {task.progress !== undefined && (
                        <span className="text-sm text-zinc-500 mt-1 block">
                          {task.progress}%
                        </span>
                      )}
                    </div>
                  ) : task?.status === "failed" ? (
                    <XCircle className="w-8 h-8 text-red-400" />
                  ) : (
                    <Clock className="w-8 h-8 text-zinc-400" />
                  )}
                </div>

                {/* Error message */}
                {task?.status === "failed" && task.error && (
                  <p className="text-xs text-red-500 line-clamp-2">
                    {task.error}
                  </p>
                )}

                {/* Platform and actions */}
                {!compareMode && (
                  <div className="flex items-center justify-between">
                    {task && (
                      <Badge variant="outline" className="text-xs">
                        {PLATFORM_NAMES[task.platform] || task.platform}
                      </Badge>
                    )}

                    <div className="flex gap-1">
                      {task?.status === "completed" && onDownload && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDownload(shot.shot_id);
                          }}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      )}
                      {(task?.status === "failed" ||
                        task?.status === "completed") &&
                        onRetry && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedShot(shot.shot_id);
                            }}
                          >
                            <RefreshCw className="w-4 h-4" />
                          </Button>
                        )}
                      {onUpdatePrompt && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditPrompt(shot.shot_id);
                          }}
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Retry modal */}
      {selectedShot && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={() => setSelectedShot(null)}
        >
          <Card
            className="w-full max-w-md mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{labels.retryWith}</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedShot(null)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>{labels.selectPlatforms}</Label>
                <Select
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                  options={platforms.map((p) => ({
                    value: p,
                    label: PLATFORM_NAMES[p],
                  }))}
                />
              </div>
              <Button
                className="w-full"
                onClick={() => {
                  handleRetryWithPlatform(selectedShot);
                  setSelectedShot(null);
                }}
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                {labels.retry}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Prompt edit modal */}
      {editingPrompt && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={() => setEditingPrompt(null)}
        >
          <Card
            className="w-full max-w-2xl mx-4"
            onClick={(e) => e.stopPropagation()}
          >
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{labels.editPrompt}</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setEditingPrompt(null)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>{labels.prompt}</Label>
                <Textarea
                  value={editedPromptText}
                  onChange={(e) => setEditedPromptText(e.target.value)}
                  rows={6}
                  className="font-mono text-sm"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <Button
                  variant="outline"
                  onClick={() => setEditingPrompt(null)}
                >
                  {labels.cancel}
                </Button>
                <Button onClick={handleSavePrompt}>
                  <Save className="w-4 h-4 mr-1" />
                  {labels.save}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Video preview modal */}
      {previewUrl && (
        <VideoModal
          isOpen={!!previewUrl}
          onClose={() => setPreviewUrl(null)}
          url={previewUrl}
          locale={locale}
        />
      )}
    </div>
  );
}
