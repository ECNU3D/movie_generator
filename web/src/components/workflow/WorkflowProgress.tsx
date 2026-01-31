"use client";

import { cn } from "@/lib/utils";
import { Check } from "lucide-react";
import type { WorkflowPhase } from "@/types";

const PHASES: { key: WorkflowPhase; label: string; labelZh: string }[] = [
  { key: "story_outline", label: "Story Outline", labelZh: "故事大纲" },
  { key: "character_design", label: "Characters", labelZh: "角色设计" },
  { key: "episode_writing", label: "Episodes", labelZh: "剧集" },
  { key: "storyboard", label: "Storyboard", labelZh: "分镜" },
  { key: "video_prompts", label: "Prompts", labelZh: "提示词" },
  { key: "video_generation", label: "Videos", labelZh: "视频" },
];

interface WorkflowProgressProps {
  currentPhase: WorkflowPhase;
  locale?: "en" | "zh";
}

export function WorkflowProgress({
  currentPhase,
  locale = "zh",
}: WorkflowProgressProps) {
  const currentIndex = PHASES.findIndex((p) => p.key === currentPhase);
  const isCompleted = currentPhase === "completed";
  const isError = currentPhase === "error";

  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {PHASES.map((phase, index) => {
          const isActive = phase.key === currentPhase;
          const isPast = isCompleted || index < currentIndex;
          const isFuture = !isCompleted && index > currentIndex;

          return (
            <div key={phase.key} className="flex items-center flex-1">
              {/* Step circle */}
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300",
                    isPast &&
                      "bg-green-500 text-white",
                    isActive &&
                      !isError &&
                      "bg-zinc-900 text-white dark:bg-white dark:text-zinc-900 ring-4 ring-zinc-200 dark:ring-zinc-700",
                    isActive &&
                      isError &&
                      "bg-red-500 text-white ring-4 ring-red-200",
                    isFuture &&
                      "bg-zinc-100 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-500"
                  )}
                >
                  {isPast ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    index + 1
                  )}
                </div>
                <span
                  className={cn(
                    "mt-2 text-xs font-medium whitespace-nowrap",
                    isPast && "text-green-600 dark:text-green-400",
                    isActive && !isError && "text-zinc-900 dark:text-white",
                    isActive && isError && "text-red-500",
                    isFuture && "text-zinc-400 dark:text-zinc-500"
                  )}
                >
                  {locale === "zh" ? phase.labelZh : phase.label}
                </span>
              </div>

              {/* Connector line */}
              {index < PHASES.length - 1 && (
                <div
                  className={cn(
                    "flex-1 h-0.5 mx-2 transition-all duration-300",
                    index < currentIndex || isCompleted
                      ? "bg-green-500"
                      : "bg-zinc-200 dark:bg-zinc-700"
                  )}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
