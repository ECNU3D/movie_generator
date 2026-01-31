"use client";

import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Play,
  Download,
  RefreshCw,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  Film,
} from "lucide-react";
import type { VideoTask } from "@/types";

interface VideoCardProps {
  task: VideoTask;
  shotIndex: number;
  onDownload?: () => void;
  onRegenerate?: () => void;
  onGenerate?: () => void;
  onPlay?: () => void;
  locale?: "en" | "zh";
}

export function VideoCard({
  task,
  shotIndex,
  onDownload,
  onRegenerate,
  onGenerate,
  onPlay,
  locale = "zh",
}: VideoCardProps) {
  const getStatusIcon = () => {
    switch (task.status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "processing":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-zinc-400" />;
    }
  };

  const getStatusLabel = () => {
    switch (task.status) {
      case "completed":
        return locale === "zh" ? "已完成" : "Completed";
      case "failed":
        return locale === "zh" ? "失败" : "Failed";
      case "processing":
        return locale === "zh" ? "生成中" : "Processing";
      default:
        return locale === "zh" ? "等待中" : "Pending";
    }
  };

  const getStatusVariant = () => {
    switch (task.status) {
      case "completed":
        return "success";
      case "failed":
        return "destructive";
      case "processing":
        return "info";
      default:
        return "secondary";
    }
  };

  const shotLabel = locale === "zh" ? "镜头" : "Shot";

  return (
    <Card
      className={cn(
        "transition-all duration-200",
        task.status === "completed" && "border-green-200 dark:border-green-800",
        task.status === "failed" && "border-red-200 dark:border-red-800"
      )}
    >
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <Film className="w-4 h-4" />
            {shotLabel} {shotIndex + 1}
          </CardTitle>
          <Badge variant={getStatusVariant() as "success" | "destructive" | "info" | "secondary"}>
            {getStatusIcon()}
            <span className="ml-1">{getStatusLabel()}</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Video preview area */}
        <div
          className={cn(
            "aspect-video rounded-lg flex items-center justify-center",
            task.status === "completed"
              ? "bg-zinc-900 cursor-pointer hover:bg-zinc-800"
              : "bg-zinc-100 dark:bg-zinc-800"
          )}
          onClick={task.status === "completed" ? onPlay : undefined}
        >
          {task.status === "completed" ? (
            <Play className="w-12 h-12 text-white opacity-80" />
          ) : task.status === "processing" ? (
            <div className="text-center">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto" />
              {task.progress !== undefined && (
                <span className="text-sm text-zinc-500 mt-2 block">
                  {task.progress}%
                </span>
              )}
            </div>
          ) : task.status === "failed" ? (
            <XCircle className="w-8 h-8 text-red-400" />
          ) : (
            <Clock className="w-8 h-8 text-zinc-400" />
          )}
        </div>

        {/* Progress bar for processing */}
        {task.status === "processing" && task.progress !== undefined && (
          <Progress value={task.progress} />
        )}

        {/* Error message */}
        {task.status === "failed" && task.error && (
          <p className="text-xs text-red-500 line-clamp-2">{task.error}</p>
        )}

        {/* Platform badge */}
        <div className="flex items-center justify-between">
          <Badge variant="outline" className="text-xs">
            {task.platform}
          </Badge>

          {/* Action buttons */}
          <div className="flex gap-1">
            {/* Generate button for pending tasks */}
            {(task.status === "pending" || !task.task_id) && onGenerate && (
              <Button variant="default" size="sm" onClick={onGenerate}>
                <Play className="w-4 h-4 mr-1" />
                {locale === "zh" ? "生成" : "Generate"}
              </Button>
            )}
            {task.status === "completed" && onDownload && (
              <Button variant="ghost" size="sm" onClick={onDownload}>
                <Download className="w-4 h-4" />
              </Button>
            )}
            {(task.status === "failed" || task.status === "completed") &&
              onRegenerate && (
                <Button variant="ghost" size="sm" onClick={onRegenerate}>
                  <RefreshCw className="w-4 h-4" />
                </Button>
              )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface VideoGridProps {
  tasks: Record<string, VideoTask>;
  shotIds: string[];
  prompts?: Record<string, string>;
  onRefresh?: () => void;
  onDownload?: (shotId: string) => void;
  onRegenerate?: (shotId: string) => void;
  onGenerate?: (shotId: string, prompt: string) => void;
  onDownloadAll?: () => void;
  locale?: "en" | "zh";
}

export function VideoGrid({
  tasks,
  shotIds,
  prompts,
  onRefresh,
  onDownload,
  onRegenerate,
  onGenerate,
  onDownloadAll,
  locale = "zh",
}: VideoGridProps) {
  const completedCount = Object.values(tasks).filter(
    (t) => t.status === "completed"
  ).length;
  const totalCount = shotIds.length;
  const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  // Localized labels
  const totalProgressLabel = locale === "zh" ? "总进度" : "Total Progress";
  const completedLabel = locale === "zh" ? "完成" : "completed";
  const refreshLabel = locale === "zh" ? "刷新状态" : "Refresh Status";
  const downloadAllLabel = locale === "zh" ? "下载全部" : "Download All";

  return (
    <div className="space-y-6">
      {/* Overall progress */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              {totalProgressLabel}: {completedCount}/{totalCount} {completedLabel}
            </span>
            <span className="text-sm text-zinc-500">{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} />

          <div className="flex gap-2 mt-4">
            {onRefresh && (
              <Button variant="outline" size="sm" onClick={onRefresh}>
                <RefreshCw className="w-4 h-4 mr-1" />
                {refreshLabel}
              </Button>
            )}
            {onDownloadAll && completedCount > 0 && (
              <Button variant="outline" size="sm" onClick={onDownloadAll}>
                <Download className="w-4 h-4 mr-1" />
                {downloadAllLabel}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Video grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {shotIds.map((shotId, index) => {
          const task = tasks[shotId];
          if (!task) return null;

          return (
            <VideoCard
              key={shotId}
              task={task}
              shotIndex={index}
              onDownload={onDownload ? () => onDownload(shotId) : undefined}
              onRegenerate={
                onRegenerate ? () => onRegenerate(shotId) : undefined
              }
              onGenerate={
                onGenerate && prompts?.[shotId]
                  ? () => onGenerate(shotId, prompts[shotId])
                  : undefined
              }
              locale={locale}
            />
          );
        })}
      </div>
    </div>
  );
}
