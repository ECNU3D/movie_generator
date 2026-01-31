"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DashboardSkeleton, ProjectListSkeleton } from "@/components/ui/skeleton";
import {
  Film,
  Plus,
  FolderOpen,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { api } from "@/lib/api";
import { useTranslation } from "@/i18n/context";
import type { Session } from "@/types";

export default function HomePage() {
  const { t, locale } = useTranslation();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await api.listSessions(undefined, 5);
      setSessions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  const stats = {
    total: sessions.length,
    running: sessions.filter((s) => s.status === "running").length,
    completed: sessions.filter((s) => s.status === "completed").length,
    failed: sessions.filter((s) => s.status === "failed").length,
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
      case "completed":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "failed":
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-zinc-400" />;
    }
  };

  const getStatusVariant = (status: string) => {
    switch (status) {
      case "running":
        return "info";
      case "completed":
        return "success";
      case "failed":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const getStatusLabel = (status: string) => {
    return t(`status.${status}`) || status;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString(locale === "zh" ? "zh-CN" : "en-US");
  };

  if (loading && sessions.length === 0) {
    return (
      <MainLayout>
        <DashboardSkeleton />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-8 page-transition">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-zinc-400" />
              {t("home.title")}
            </h1>
            <p className="text-zinc-500 mt-1">
              {t("home.subtitle")}
            </p>
          </div>
          <Link href="/workflow/new">
            <Button size="lg" className="shadow-md">
              <Plus className="w-5 h-5" />
              {t("home.newProject")}
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-zinc-500">
                {t("stats.total")}
              </CardTitle>
              <FolderOpen className="w-4 h-4 text-zinc-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-zinc-500">
                {t("stats.running")}
              </CardTitle>
              <Loader2 className="w-4 h-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {stats.running}
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-zinc-500">
                {t("stats.completed")}
              </CardTitle>
              <CheckCircle className="w-4 h-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {stats.completed}
              </div>
            </CardContent>
          </Card>

          <Card className="card-hover">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-zinc-500">
                {t("stats.failed")}
              </CardTitle>
              <AlertCircle className="w-4 h-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {stats.failed}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Start */}
        <Card className="overflow-hidden">
          <div className="bg-gradient-to-r from-zinc-900 to-zinc-800 dark:from-zinc-800 dark:to-zinc-900 p-8 text-white">
            <div className="flex items-start justify-between">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Film className="w-8 h-8" />
                  <h2 className="text-2xl font-bold">{t("home.quickStart")}</h2>
                </div>
                <p className="text-zinc-300 max-w-lg">
                  {t("home.quickStartDesc")}
                </p>
                <div className="flex gap-3 pt-2">
                  <Link href="/workflow/new">
                    <Button variant="secondary" size="lg">
                      <Plus className="w-5 h-5" />
                      {t("home.createProject")}
                    </Button>
                  </Link>
                  <Link href="/projects">
                    <Button variant="ghost" size="lg" className="text-white hover:bg-white/10">
                      <FolderOpen className="w-5 h-5" />
                      {t("home.viewAllProjects")}
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="hidden lg:block">
                <div className="w-32 h-32 rounded-2xl bg-white/10 flex items-center justify-center">
                  <Sparkles className="w-16 h-16 text-white/50" />
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Recent Projects */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>{t("home.recentProjects")}</CardTitle>
            <Link href="/projects">
              <Button variant="ghost" size="sm">
                {t("common.viewAll")}
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {loading ? (
              <ProjectListSkeleton />
            ) : error ? (
              <div className="text-center py-8">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/20 mb-4">
                  <AlertCircle className="w-6 h-6 text-red-500" />
                </div>
                <p className="text-red-600 dark:text-red-400 mb-2">{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadSessions}
                >
                  {t("common.retry")}
                </Button>
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-12">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-zinc-100 dark:bg-zinc-800 mb-4">
                  <FolderOpen className="w-8 h-8 text-zinc-400" />
                </div>
                <p className="text-lg font-medium mb-1">{t("home.noProjects")}</p>
                <p className="text-zinc-500 mb-4">{t("home.noProjectsDesc")}</p>
                <Link href="/workflow/new">
                  <Button>
                    <Plus className="w-4 h-4" />
                    {t("home.createFirstProject")}
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-2">
                {sessions.map((session, index) => (
                  <Link
                    key={session.session_id}
                    href={`/workflow/${session.session_id}`}
                    className="block animate-slide-up"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-center justify-between p-4 rounded-lg border border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:border-zinc-700 dark:hover:bg-zinc-800/50 transition-all duration-200">
                      <div className="flex items-center gap-4">
                        {getStatusIcon(session.status)}
                        <div>
                          <p className="font-medium">
                            {session.project_name || session.session_id}
                          </p>
                          <p className="text-xs text-zinc-500">
                            {formatDate(session.created_at)}
                          </p>
                        </div>
                      </div>
                      <Badge variant={getStatusVariant(session.status) as "info" | "success" | "destructive" | "secondary"}>
                        {getStatusLabel(session.status)}
                      </Badge>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
