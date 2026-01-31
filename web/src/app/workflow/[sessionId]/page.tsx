"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { WorkflowProgress } from "@/components/workflow/WorkflowProgress";
import { ApprovalPanel } from "@/components/workflow/ApprovalPanel";
import { StoryOutlineView } from "@/components/workflow/StoryOutlineView";
import { CharacterList } from "@/components/workflow/CharacterList";
import { StoryboardGrid } from "@/components/workflow/StoryboardGrid";
import { VideoGrid } from "@/components/video/VideoGrid";
import {
  ArrowLeft,
  Loader2,
  AlertCircle,
  RefreshCw,
  Play,
  Film,
} from "lucide-react";
import { api } from "@/lib/api";
import { workflowWS } from "@/lib/websocket";
import {
  requestNotificationPermission,
  notifyApprovalRequired,
  notifyVideoComplete,
  notifyAllVideosComplete,
} from "@/lib/notifications";
import { useWorkflowStore } from "@/stores/workflow";
import { useTranslation } from "@/i18n/context";
import type { SessionDetail, Character, Shot } from "@/types";

export default function WorkflowDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;
  const { t, locale } = useTranslation();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [approving, setApproving] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);

  const {
    status,
    phase,
    projectName,
    storyOutline,
    characters,
    episodes,
    storyboard,
    videoPrompts,
    videoTasks,
    pendingApproval,
    approvalType,
    loadFromSession,
    updateCharacter,
    updateShot,
    setVideoTasks,
  } = useWorkflowStore();

  // Request notification permission on mount
  useEffect(() => {
    requestNotificationPermission().then(setNotificationsEnabled);
  }, []);

  const loadSession = useCallback(async () => {
    try {
      setLoading(true);
      const data: SessionDetail = await api.getSession(sessionId);
      loadFromSession(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  }, [sessionId, loadFromSession, t]);

  useEffect(() => {
    loadSession();

    // Connect WebSocket
    workflowWS.connect();
    workflowWS.subscribe(sessionId);

    // Listen for updates
    const unsubPhase = workflowWS.on("phase_changed", () => {
      loadSession();
    });

    const unsubApproval = workflowWS.on("approval_required", (data) => {
      loadSession();
      // Show browser notification
      if (notificationsEnabled && data.projectName && data.approvalType) {
        notifyApprovalRequired(data.projectName, data.approvalType, sessionId);
      }
    });

    const unsubVideo = workflowWS.on("video_status", (data) => {
      if (data.shotId && data.status) {
        loadSession();
        // Show notification when video completes
        if (notificationsEnabled && data.status === "completed") {
          notifyVideoComplete(data.shotId);
        }
      }
    });

    const unsubComplete = workflowWS.on("completed", (data) => {
      loadSession();
      // Show notification when all videos complete
      if (notificationsEnabled && data.projectName) {
        notifyAllVideosComplete(data.projectName);
      }
    });

    return () => {
      workflowWS.unsubscribe();
      unsubPhase();
      unsubApproval();
      unsubVideo();
      unsubComplete();
    };
  }, [sessionId, loadSession, notificationsEnabled]);

  const handleApprove = async () => {
    try {
      setApproving(true);
      await api.approveSession(sessionId, { approved: true });
      await loadSession();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setApproving(false);
    }
  };

  const handleReject = async (feedback: string) => {
    try {
      setApproving(true);
      await api.approveSession(sessionId, { approved: false, feedback });
      await loadSession();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setApproving(false);
    }
  };

  const handleResume = async () => {
    try {
      setLoading(true);
      await api.resumeSession(sessionId);
      await loadSession();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshVideos = async () => {
    try {
      const tasks = await api.refreshVideos(sessionId);
      setVideoTasks(tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  };

  const handleGenerateSingleVideo = async (shotId: string, prompt: string) => {
    try {
      const result = await api.generateSingleVideo(sessionId, shotId, prompt);
      // Update the task in the store
      setVideoTasks({
        ...videoTasks,
        [shotId]: {
          shot_id: shotId,
          task_id: result.task_id,
          platform: result.platform,
          status: result.status,
          prompt: prompt,
        },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  };

  const handleRetryVideo = async (shotId: string) => {
    try {
      const result = await api.retryVideo(sessionId, shotId);
      setVideoTasks({
        ...videoTasks,
        [shotId]: {
          ...videoTasks[shotId],
          task_id: result.task_id,
          status: result.status,
        },
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  };

  const handleDownloadVideo = (shotId: string) => {
    api.downloadVideo(sessionId, shotId);
  };

  const handleDownloadAll = async () => {
    try {
      const result = await api.downloadVideos(sessionId);
      // Open each video URL in a new tab
      for (const video of result.videos) {
        window.open(video.video_url, "_blank");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  };

  const handleCharacterUpdate = async (index: number, character: Character) => {
    try {
      await api.updateCharacter(sessionId, index, character);
      updateCharacter(index, character);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  };

  const handleShotUpdate = async (index: number, shot: Shot) => {
    try {
      await api.updateShot(sessionId, index, shot);
      updateShot(index, shot);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case "running":
        return (
          <Badge variant="info">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            {t("status.running")}
          </Badge>
        );
      case "completed":
        return <Badge variant="success">{t("status.completed")}</Badge>;
      case "failed":
        return <Badge variant="destructive">{t("status.failed")}</Badge>;
      case "paused":
        return <Badge variant="warning">{t("status.paused")}</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  // Get shot IDs for video grid - generate from episode_number and shot_number
  const shotIds = storyboard.map((shot, index) => {
    // Try shot_id first, then generate from episode/shot numbers
    if (shot.shot_id) return shot.shot_id;
    const epNum = (shot as Record<string, unknown>).episode_number || 1;
    const shotNum = (shot as Record<string, unknown>).shot_number || index + 1;
    return `ep${epNum}_shot${shotNum}`;
  });

  // Labels
  const refreshLabel = locale === "zh" ? "刷新" : "Refresh";
  const resumeLabel = locale === "zh" ? "恢复" : "Resume";
  const workflowLabel = locale === "zh" ? "工作流" : "Workflow";
  const characterDesignLabel = locale === "zh" ? "角色设计" : "Character Design";
  const episodeOutlineLabel = locale === "zh" ? "剧集大纲" : "Episode Outline";
  const episodeLabel = locale === "zh" ? "第" : "Episode";
  const shotLabel = locale === "zh" ? "个镜头" : "shots";
  const storyboardLabel = locale === "zh" ? "分镜脚本" : "Storyboard";

  if (loading && !storyOutline) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="w-8 h-8 animate-spin text-zinc-400" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/projects">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Film className="w-6 h-6" />
                {projectName || storyOutline?.title || workflowLabel}
              </h1>
              <p className="text-sm text-zinc-500">ID: {sessionId}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {getStatusBadge()}
            <Button variant="outline" size="sm" onClick={loadSession}>
              <RefreshCw className="w-4 h-4 mr-1" />
              {refreshLabel}
            </Button>
            {status === "failed" && (
              <Button size="sm" onClick={handleResume}>
                <Play className="w-4 h-4 mr-1" />
                {resumeLabel}
              </Button>
            )}
          </div>
        </div>

        {/* Error */}
        {error && (
          <Card className="border-red-200 dark:border-red-800">
            <CardContent className="flex items-center gap-2 py-4 text-red-600 dark:text-red-400">
              <AlertCircle className="w-5 h-5" />
              {error}
            </CardContent>
          </Card>
        )}

        {/* Progress */}
        <Card>
          <CardContent className="py-6">
            <WorkflowProgress currentPhase={phase} locale={locale} />
          </CardContent>
        </Card>

        {/* Approval Panel */}
        {pendingApproval && (
          <ApprovalPanel
            approvalType={approvalType}
            data={{}}
            onApprove={handleApprove}
            onReject={handleReject}
            loading={approving}
            locale={locale}
          />
        )}

        {/* Content based on phase */}
        <div className="space-y-6">
          {/* Story Outline */}
          {storyOutline && (
            <StoryOutlineView outline={storyOutline} locale={locale} />
          )}

          {/* Characters */}
          {characters.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>{characterDesignLabel}</CardTitle>
              </CardHeader>
              <CardContent>
                <CharacterList
                  characters={characters}
                  onUpdate={
                    pendingApproval && approvalType === "character_design"
                      ? handleCharacterUpdate
                      : undefined
                  }
                  locale={locale}
                />
              </CardContent>
            </Card>
          )}

          {/* Episodes */}
          {episodes.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>{episodeOutlineLabel}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {episodes.map((episode, index) => (
                    <div
                      key={index}
                      className="p-4 rounded-lg border border-zinc-200 dark:border-zinc-800"
                    >
                      <h4 className="font-medium mb-2">
                        {locale === "zh"
                          ? `第 ${episode.episode_number} 集: ${episode.title}`
                          : `Episode ${episode.episode_number}: ${episode.title}`}
                      </h4>
                      <p className="text-sm text-zinc-600 dark:text-zinc-400">
                        {episode.outline}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Storyboard */}
          {storyboard.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>
                  {storyboardLabel} ({storyboard.length} {shotLabel})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <StoryboardGrid
                  shots={storyboard}
                  onEdit={
                    pendingApproval && approvalType === "storyboard"
                      ? handleShotUpdate
                      : undefined
                  }
                  videoPrompts={videoPrompts}
                  locale={locale}
                />
              </CardContent>
            </Card>
          )}

          {/* Videos */}
          {Object.keys(videoTasks).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>{t("video.videoGeneration")}</CardTitle>
              </CardHeader>
              <CardContent>
                <VideoGrid
                  tasks={videoTasks}
                  shotIds={shotIds}
                  prompts={videoPrompts}
                  onRefresh={handleRefreshVideos}
                  onGenerate={handleGenerateSingleVideo}
                  onRegenerate={handleRetryVideo}
                  onDownload={handleDownloadVideo}
                  onDownloadAll={handleDownloadAll}
                  locale={locale}
                />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
