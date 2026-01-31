"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import {
  Plus,
  FolderOpen,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Trash2,
  Play,
  RefreshCw,
} from "lucide-react";
import { api } from "@/lib/api";
import { useTranslation } from "@/i18n/context";
import type { Session } from "@/types";

export default function ProjectsPage() {
  const { t, locale } = useTranslation();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [deleting, setDeleting] = useState<string | null>(null);

  const STATUS_OPTIONS = useMemo(
    () => [
      { value: "", label: locale === "zh" ? "全部状态" : "All Status" },
      { value: "running", label: t("status.running") },
      { value: "paused", label: t("status.paused") },
      { value: "completed", label: t("status.completed") },
      { value: "failed", label: t("status.failed") },
    ],
    [t, locale]
  );

  useEffect(() => {
    loadSessions();
  }, [statusFilter]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await api.listSessions(statusFilter || undefined, 50);
      setSessions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sessionId: string) => {
    const confirmMsg = locale === "zh" ? "确定要删除这个项目吗？" : "Are you sure you want to delete this project?";
    if (!confirm(confirmMsg)) return;

    try {
      setDeleting(sessionId);
      await api.deleteSession(sessionId);
      setSessions(sessions.filter((s) => s.session_id !== sessionId));
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setDeleting(null);
    }
  };

  const handleResume = async (sessionId: string) => {
    try {
      await api.resumeSession(sessionId);
      await loadSessions();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "failed":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case "paused":
        return <Clock className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-zinc-400" />;
    }
  };

  const getStatusLabel = (status: string) => {
    return t(`status.${status}`) || status;
  };

  const getStatusVariant = (status: string) => {
    switch (status) {
      case "running":
        return "info";
      case "completed":
        return "success";
      case "failed":
        return "destructive";
      case "paused":
        return "warning";
      default:
        return "secondary";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString(locale === "zh" ? "zh-CN" : "en-US");
  };

  const projectListTitle = locale === "zh" ? "项目列表" : "Project List";
  const projectListDesc = locale === "zh" ? "管理你的所有 AI 视频项目" : "Manage all your AI video projects";
  const statusFilterLabel = locale === "zh" ? "状态筛选:" : "Status Filter:";
  const refreshLabel = locale === "zh" ? "刷新" : "Refresh";
  const projectsLabel = locale === "zh" ? "项目" : "Projects";
  const createdAtLabel = locale === "zh" ? "创建于" : "Created at";

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">{projectListTitle}</h1>
            <p className="text-zinc-500 mt-1">
              {projectListDesc}
            </p>
          </div>
          <Link href="/workflow/new">
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              {t("nav.newProject")}
            </Button>
          </Link>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-zinc-500">{statusFilterLabel}</span>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={STATUS_OPTIONS}
                  className="w-32"
                />
              </div>
              <Button variant="outline" size="sm" onClick={loadSessions}>
                <RefreshCw className="w-4 h-4 mr-1" />
                {refreshLabel}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Error */}
        {error && (
          <Card className="border-red-200 dark:border-red-800">
            <CardContent className="flex items-center gap-2 py-4 text-red-600 dark:text-red-400">
              <AlertCircle className="w-5 h-5" />
              {error}
            </CardContent>
          </Card>
        )}

        {/* Sessions List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FolderOpen className="w-5 h-5" />
              {projectsLabel} ({sessions.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-zinc-400" />
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-12 text-zinc-500">
                <FolderOpen className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg mb-2">{t("home.noProjects")}</p>
                <p className="text-sm mb-4">{t("home.noProjectsDesc")}</p>
                <Link href="/workflow/new">
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    {t("home.createProject")}
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className="flex items-center justify-between p-4 rounded-lg border border-zinc-200 hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700 transition-colors"
                  >
                    <Link
                      href={`/workflow/${session.session_id}`}
                      className="flex items-center gap-4 flex-1"
                    >
                      {getStatusIcon(session.status)}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">
                          {session.project_name || session.session_id}
                        </p>
                        <div className="flex items-center gap-2 text-xs text-zinc-500">
                          <span>
                            {createdAtLabel}{" "}
                            {formatDate(session.created_at)}
                          </span>
                          {session.error && (
                            <span className="text-red-500 truncate max-w-xs">
                              {session.error}
                            </span>
                          )}
                        </div>
                      </div>
                    </Link>

                    <div className="flex items-center gap-2">
                      <Badge variant={getStatusVariant(session.status) as "info" | "success" | "destructive" | "warning" | "secondary"}>
                        {getStatusLabel(session.status)}
                      </Badge>

                      {(session.status === "failed" ||
                        session.status === "paused") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleResume(session.session_id)}
                        >
                          <Play className="w-4 h-4" />
                        </Button>
                      )}

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(session.session_id)}
                        disabled={deleting === session.session_id}
                        className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                      >
                        {deleting === session.session_id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
