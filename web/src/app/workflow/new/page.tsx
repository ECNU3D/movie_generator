"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Film, Rocket } from "lucide-react";
import { api } from "@/lib/api";
import { useTranslation } from "@/i18n/context";
import type { CreateSessionRequest } from "@/types";

export default function NewWorkflowPage() {
  const router = useRouter();
  const { t, locale } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<CreateSessionRequest>({
    idea: "",
    genre: "drama",
    style: "",
    num_episodes: 1,
    episode_duration: 60,
    num_characters: 3,
    target_platform: "kling",
    mode: "interactive",
  });

  // Memoized options based on locale
  const GENRES = useMemo(
    () => [
      { value: "drama", label: t("genres.drama") },
      { value: "comedy", label: t("genres.comedy") },
      { value: "action", label: t("genres.action") },
      { value: "sci-fi", label: t("genres.sci-fi") },
      { value: "fantasy", label: t("genres.fantasy") },
      { value: "romance", label: t("genres.romance") },
      { value: "horror", label: t("genres.horror") },
      { value: "thriller", label: t("genres.thriller") },
    ],
    [t]
  );

  const PLATFORMS = useMemo(
    () => [
      { value: "kling", label: t("platforms.kling") },
      { value: "hailuo", label: t("platforms.hailuo") },
      { value: "jimeng", label: t("platforms.jimeng") },
      { value: "tongyi", label: t("platforms.tongyi") },
    ],
    [t]
  );

  const EPISODES = useMemo(
    () => [
      { value: "1", label: `1 ${t("units.episode")}` },
      { value: "2", label: `2 ${t("units.episode")}` },
      { value: "3", label: `3 ${t("units.episode")}` },
      { value: "5", label: `5 ${t("units.episode")}` },
    ],
    [t]
  );

  const DURATIONS = useMemo(
    () => [
      { value: "30", label: `30 ${t("units.second")}` },
      { value: "60", label: `60 ${t("units.second")}` },
      { value: "90", label: `90 ${t("units.second")}` },
      { value: "120", label: `120 ${t("units.second")}` },
    ],
    [t]
  );

  const CHARACTERS = useMemo(
    () => [
      { value: "2", label: locale === "zh" ? "2 个" : "2" },
      { value: "3", label: locale === "zh" ? "3 个" : "3" },
      { value: "4", label: locale === "zh" ? "4 个" : "4" },
      { value: "5", label: locale === "zh" ? "5 个" : "5" },
    ],
    [locale]
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.idea.trim()) {
      setError(t("workflow.ideaRequired"));
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const session = await api.createSession(formData);
      router.push(`/workflow/${session.session_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("workflow.createFailed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Film className="w-6 h-6" />
              {t("workflow.title")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Story Idea */}
              <div className="space-y-2">
                <Label htmlFor="idea">
                  {t("workflow.idea")} <span className="text-red-500">*</span>
                </Label>
                <Textarea
                  id="idea"
                  value={formData.idea}
                  onChange={(e) =>
                    setFormData({ ...formData, idea: e.target.value })
                  }
                  placeholder={t("workflow.ideaPlaceholder")}
                  rows={4}
                  className="resize-none"
                />
              </div>

              {/* Genre, Episodes, Duration */}
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="genre">{t("workflow.genre")}</Label>
                  <Select
                    id="genre"
                    value={formData.genre}
                    onChange={(e) =>
                      setFormData({ ...formData, genre: e.target.value })
                    }
                    options={GENRES}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="episodes">{t("workflow.episodes")}</Label>
                  <Select
                    id="episodes"
                    value={formData.num_episodes.toString()}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        num_episodes: parseInt(e.target.value),
                      })
                    }
                    options={EPISODES}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="duration">{t("workflow.duration")}</Label>
                  <Select
                    id="duration"
                    value={formData.episode_duration.toString()}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        episode_duration: parseInt(e.target.value),
                      })
                    }
                    options={DURATIONS}
                  />
                </div>
              </div>

              {/* Characters, Platform */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="characters">{t("workflow.characters")}</Label>
                  <Select
                    id="characters"
                    value={formData.num_characters.toString()}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        num_characters: parseInt(e.target.value),
                      })
                    }
                    options={CHARACTERS}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="platform">{t("workflow.platform")}</Label>
                  <Select
                    id="platform"
                    value={formData.target_platform}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        target_platform: e.target.value,
                      })
                    }
                    options={PLATFORMS}
                  />
                </div>
              </div>

              {/* Style */}
              <div className="space-y-2">
                <Label htmlFor="style">{t("workflow.style")}</Label>
                <Input
                  id="style"
                  value={formData.style}
                  onChange={(e) =>
                    setFormData({ ...formData, style: e.target.value })
                  }
                  placeholder={t("workflow.stylePlaceholder")}
                />
              </div>

              {/* Mode */}
              <div className="space-y-3">
                <Label>{t("workflow.workMode")}</Label>
                <div className="space-y-2">
                  <label className="flex items-center gap-3 p-3 rounded-lg border border-zinc-200 cursor-pointer hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-800/50">
                    <input
                      type="radio"
                      name="mode"
                      value="interactive"
                      checked={formData.mode === "interactive"}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          mode: e.target.value as "interactive" | "autonomous",
                        })
                      }
                      className="w-4 h-4"
                    />
                    <div>
                      <p className="font-medium">{t("workflow.interactiveMode")}</p>
                      <p className="text-sm text-zinc-500">
                        {t("workflow.interactiveModeDesc")}
                      </p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 p-3 rounded-lg border border-zinc-200 cursor-pointer hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-800/50">
                    <input
                      type="radio"
                      name="mode"
                      value="autonomous"
                      checked={formData.mode === "autonomous"}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          mode: e.target.value as "interactive" | "autonomous",
                        })
                      }
                      className="w-4 h-4"
                    />
                    <div>
                      <p className="font-medium">{t("workflow.autonomousMode")}</p>
                      <p className="text-sm text-zinc-500">
                        {t("workflow.autonomousModeDesc")}
                      </p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="p-3 rounded-lg bg-red-50 text-red-600 text-sm dark:bg-red-900/20 dark:text-red-400">
                  {error}
                </div>
              )}

              {/* Submit */}
              <Button
                type="submit"
                size="lg"
                className="w-full"
                loading={loading}
                disabled={loading}
              >
                <Rocket className="w-5 h-5 mr-2" />
                {t("workflow.start")}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
