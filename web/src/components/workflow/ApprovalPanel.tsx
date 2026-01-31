"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Check, X, Edit2 } from "lucide-react";

interface ApprovalPanelProps {
  approvalType: string;
  data: unknown;
  onApprove: () => void;
  onReject: (feedback: string) => void;
  onEdit?: (edits: unknown) => void;
  loading?: boolean;
  locale?: "en" | "zh";
}

const APPROVAL_TYPE_LABELS: Record<string, { en: string; zh: string }> = {
  story_outline: { en: "Story Outline", zh: "故事大纲" },
  character_design: { en: "Character Design", zh: "角色设计" },
  episode_writing: { en: "Episode Writing", zh: "剧集编写" },
  storyboard: { en: "Storyboard", zh: "分镜脚本" },
  video_prompts: { en: "Video Prompts", zh: "视频提示词" },
};

export function ApprovalPanel({
  approvalType,
  onApprove,
  onReject,
  onEdit,
  loading = false,
  locale = "zh",
}: ApprovalPanelProps) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState("");

  const label = APPROVAL_TYPE_LABELS[approvalType] || {
    en: approvalType,
    zh: approvalType,
  };

  const handleReject = () => {
    if (showFeedback) {
      onReject(feedback);
      setFeedback("");
      setShowFeedback(false);
    } else {
      setShowFeedback(true);
    }
  };

  // Localized labels
  const waitingApprovalLabel = locale === "zh" ? "等待审批" : "Waiting for Approval";
  const feedbackLabel = locale === "zh" ? "修改建议" : "Feedback";
  const feedbackPlaceholder = locale === "zh" ? "请输入修改建议..." : "Enter your feedback...";
  const confirmRejectLabel = locale === "zh" ? "确认拒绝" : "Confirm Reject";
  const rejectLabel = locale === "zh" ? "拒绝重做" : "Reject";
  const cancelLabel = locale === "zh" ? "取消" : "Cancel";
  const editLabel = locale === "zh" ? "编辑" : "Edit";
  const approveLabel = locale === "zh" ? "通过继续" : "Approve";

  return (
    <Card className="border-2 border-yellow-400 dark:border-yellow-600">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <span className="inline-block w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
          {waitingApprovalLabel}: {locale === "zh" ? label.zh : label.en}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {showFeedback && (
          <div className="space-y-2">
            <label className="text-sm font-medium">{feedbackLabel}</label>
            <Textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder={feedbackPlaceholder}
              rows={3}
            />
          </div>
        )}

        <div className="flex items-center gap-3">
          <Button
            variant="destructive"
            onClick={handleReject}
            disabled={loading}
            className="flex-1"
          >
            <X className="w-4 h-4 mr-1" />
            {showFeedback ? confirmRejectLabel : rejectLabel}
          </Button>

          {showFeedback && (
            <Button
              variant="outline"
              onClick={() => {
                setShowFeedback(false);
                setFeedback("");
              }}
              disabled={loading}
            >
              {cancelLabel}
            </Button>
          )}

          {onEdit && !showFeedback && (
            <Button
              variant="outline"
              onClick={() => onEdit({})}
              disabled={loading}
              className="flex-1"
            >
              <Edit2 className="w-4 h-4 mr-1" />
              {editLabel}
            </Button>
          )}

          {!showFeedback && (
            <Button
              variant="success"
              onClick={onApprove}
              disabled={loading}
              loading={loading}
              className="flex-1"
            >
              <Check className="w-4 h-4 mr-1" />
              {approveLabel}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
