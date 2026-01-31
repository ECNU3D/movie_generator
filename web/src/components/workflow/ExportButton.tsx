"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Download,
  FileText,
  FileJson,
  ChevronDown,
} from "lucide-react";
import {
  exportAndDownloadMarkdown,
  exportAndDownloadJSON,
} from "@/lib/export";
import type {
  StoryOutline,
  Character,
  Episode,
  Shot,
} from "@/types";

interface ExportButtonProps {
  projectName: string;
  storyOutline?: StoryOutline | null;
  characters: Character[];
  episodes: Episode[];
  storyboard: Shot[];
  videoPrompts: Record<string, string>;
  locale?: "en" | "zh";
}

export function ExportButton({
  projectName,
  storyOutline,
  characters,
  episodes,
  storyboard,
  videoPrompts,
  locale = "zh",
}: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);

  const labels = {
    export: locale === "zh" ? "导出" : "Export",
    markdown: locale === "zh" ? "导出为 Markdown" : "Export as Markdown",
    json: locale === "zh" ? "导出为 JSON" : "Export as JSON",
  };

  const exportData = {
    projectName,
    storyOutline: storyOutline || undefined,
    characters,
    episodes,
    storyboard,
    videoPrompts,
  };

  const handleExportMarkdown = () => {
    exportAndDownloadMarkdown(exportData, locale);
    setIsOpen(false);
  };

  const handleExportJSON = () => {
    exportAndDownloadJSON(exportData);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Download className="w-4 h-4 mr-1" />
        {labels.export}
        <ChevronDown className="w-4 h-4 ml-1" />
      </Button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-zinc-900 rounded-lg shadow-lg border border-zinc-200 dark:border-zinc-800 z-20">
            <button
              onClick={handleExportMarkdown}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-t-lg"
            >
              <FileText className="w-4 h-4" />
              {labels.markdown}
            </button>
            <button
              onClick={handleExportJSON}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-b-lg"
            >
              <FileJson className="w-4 h-4" />
              {labels.json}
            </button>
          </div>
        </>
      )}
    </div>
  );
}
