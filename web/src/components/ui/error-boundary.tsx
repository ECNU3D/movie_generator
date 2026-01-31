"use client";

import { Component, ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./card";
import { Button } from "./button";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
  locale?: "en" | "zh";
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    this.props.onReset?.();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const locale = this.props.locale || "zh";
      const title = locale === "zh" ? "出错了" : "Something went wrong";
      const message =
        locale === "zh"
          ? "页面遇到了问题，请尝试刷新"
          : "The page encountered an issue. Please try refreshing.";
      const retryLabel = locale === "zh" ? "重试" : "Retry";

      return (
        <Card className="border-red-200 dark:border-red-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertCircle className="w-5 h-5" />
              {title}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              {message}
            </p>
            {this.state.error && (
              <pre className="p-3 bg-zinc-100 dark:bg-zinc-900 rounded text-xs overflow-auto max-h-40">
                {this.state.error.message}
              </pre>
            )}
            <Button onClick={this.handleReset}>
              <RefreshCw className="w-4 h-4 mr-1" />
              {retryLabel}
            </Button>
          </CardContent>
        </Card>
      );
    }

    return this.props.children;
  }
}

// Functional error display component
interface ErrorDisplayProps {
  error: string | Error | null;
  onRetry?: () => void;
  locale?: "en" | "zh";
}

export function ErrorDisplay({ error, onRetry, locale = "zh" }: ErrorDisplayProps) {
  if (!error) return null;

  const errorMessage = error instanceof Error ? error.message : error;
  const retryLabel = locale === "zh" ? "重试" : "Retry";

  return (
    <Card className="border-red-200 dark:border-red-800">
      <CardContent className="flex items-center justify-between py-4">
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span>{errorMessage}</span>
        </div>
        {onRetry && (
          <Button variant="outline" size="sm" onClick={onRetry}>
            <RefreshCw className="w-4 h-4 mr-1" />
            {retryLabel}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
