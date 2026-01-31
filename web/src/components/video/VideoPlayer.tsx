"use client";

import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize,
  Download,
  RefreshCw,
  X,
} from "lucide-react";

interface VideoPlayerProps {
  url: string;
  poster?: string;
  onEnded?: () => void;
  onDownload?: () => void;
  onRegenerate?: () => void;
  onClose?: () => void;
  locale?: "en" | "zh";
}

export function VideoPlayer({
  url,
  poster,
  onEnded,
  onDownload,
  onRegenerate,
  onClose,
  locale = "zh",
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const labels = {
    play: locale === "zh" ? "播放" : "Play",
    pause: locale === "zh" ? "暂停" : "Pause",
    mute: locale === "zh" ? "静音" : "Mute",
    unmute: locale === "zh" ? "取消静音" : "Unmute",
    fullscreen: locale === "zh" ? "全屏" : "Fullscreen",
    download: locale === "zh" ? "下载" : "Download",
    regenerate: locale === "zh" ? "重新生成" : "Regenerate",
    close: locale === "zh" ? "关闭" : "Close",
  };

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => setCurrentTime(video.currentTime);
    const handleDurationChange = () => setDuration(video.duration);
    const handleEnded = () => {
      setIsPlaying(false);
      onEnded?.();
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("durationchange", handleDurationChange);
    video.addEventListener("ended", handleEnded);

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("durationchange", handleDurationChange);
      video.removeEventListener("ended", handleEnded);
    };
  }, [onEnded]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const toggleFullscreen = () => {
    const video = videoRef.current;
    if (!video) return;

    if (!isFullscreen) {
      if (video.requestFullscreen) {
        video.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setIsFullscreen(!isFullscreen);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current;
    if (!video) return;

    const time = parseFloat(e.target.value);
    video.currentTime = time;
    setCurrentTime(time);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="relative bg-black rounded-lg overflow-hidden">
      {/* Close button */}
      {onClose && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="absolute top-2 right-2 z-10 text-white hover:bg-white/20"
        >
          <X className="w-5 h-5" />
        </Button>
      )}

      {/* Video element */}
      <video
        ref={videoRef}
        src={url}
        poster={poster}
        className="w-full aspect-video"
        onClick={togglePlay}
      />

      {/* Controls overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
        {/* Progress bar */}
        <div className="mb-3">
          <input
            type="range"
            min={0}
            max={duration || 100}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1 bg-white/30 rounded-full appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, white ${
                (currentTime / duration) * 100
              }%, rgba(255,255,255,0.3) ${(currentTime / duration) * 100}%)`,
            }}
          />
        </div>

        {/* Control buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* Play/Pause */}
            <Button
              variant="ghost"
              size="sm"
              onClick={togglePlay}
              className="text-white hover:bg-white/20"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5" />
              ) : (
                <Play className="w-5 h-5" />
              )}
            </Button>

            {/* Mute */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleMute}
              className="text-white hover:bg-white/20"
            >
              {isMuted ? (
                <VolumeX className="w-5 h-5" />
              ) : (
                <Volume2 className="w-5 h-5" />
              )}
            </Button>

            {/* Time display */}
            <span className="text-white text-sm">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Regenerate */}
            {onRegenerate && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRegenerate}
                className="text-white hover:bg-white/20"
                title={labels.regenerate}
              >
                <RefreshCw className="w-4 h-4" />
              </Button>
            )}

            {/* Download */}
            {onDownload && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onDownload}
                className="text-white hover:bg-white/20"
                title={labels.download}
              >
                <Download className="w-4 h-4" />
              </Button>
            )}

            {/* Fullscreen */}
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleFullscreen}
              className="text-white hover:bg-white/20"
              title={labels.fullscreen}
            >
              <Maximize className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Modal wrapper for video preview
interface VideoModalProps {
  isOpen: boolean;
  onClose: () => void;
  url: string;
  title?: string;
  onDownload?: () => void;
  onRegenerate?: () => void;
  locale?: "en" | "zh";
}

export function VideoModal({
  isOpen,
  onClose,
  url,
  title,
  onDownload,
  onRegenerate,
  locale = "zh",
}: VideoModalProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
      onClick={onClose}
    >
      <div
        className="max-w-4xl w-full mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        {title && (
          <h3 className="text-white text-lg font-medium mb-2">{title}</h3>
        )}
        <VideoPlayer
          url={url}
          onClose={onClose}
          onDownload={onDownload}
          onRegenerate={onRegenerate}
          locale={locale}
        />
      </div>
    </div>
  );
}
