"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Film,
  Home,
  FolderOpen,
  Plus,
  Settings,
  Globe,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocale } from "@/i18n/context";

interface NavItem {
  href: string;
  labelKey: string;
  icon: React.ReactNode;
}

const NAV_ITEMS: NavItem[] = [
  {
    href: "/",
    labelKey: "nav.home",
    icon: <Home className="w-5 h-5" />,
  },
  {
    href: "/projects",
    labelKey: "nav.projects",
    icon: <FolderOpen className="w-5 h-5" />,
  },
  {
    href: "/workflow/new",
    labelKey: "nav.newProject",
    icon: <Plus className="w-5 h-5" />,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { locale, setLocale, t } = useLocale();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center gap-2 border-b border-zinc-200 px-6 dark:border-zinc-800">
          <Film className="h-6 w-6 text-zinc-900 dark:text-white" />
          <span className="text-lg font-semibold">AI Movie</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          {NAV_ITEMS.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-white"
                    : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/50 dark:hover:text-white"
                )}
              >
                {item.icon}
                {t(item.labelKey)}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-zinc-200 p-4 dark:border-zinc-800">
          {/* Language switcher */}
          <div className="flex items-center gap-2 mb-4">
            <Globe className="w-4 h-4 text-zinc-500" />
            <div className="flex gap-1">
              <Button
                variant={locale === "zh" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setLocale("zh")}
                className="h-7 px-2 text-xs"
              >
                中文
              </Button>
              <Button
                variant={locale === "en" ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setLocale("en")}
                className="h-7 px-2 text-xs"
              >
                EN
              </Button>
            </div>
          </div>

          <Link
            href="/settings"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-800/50 dark:hover:text-white"
          >
            <Settings className="w-5 h-5" />
            {t("nav.settings")}
          </Link>
        </div>
      </div>
    </aside>
  );
}
