import type { ReactNode } from "react";

import { useQuery } from "@tanstack/react-query";
import {
  BookOpen,
  BrainCircuit,
  LayoutDashboard,
  Layers3,
  Search,
  Sparkles,
} from "lucide-react";
import { Link, NavLink } from "react-router-dom";

import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { cn, truncate } from "@/lib/utils";

// ── Nav items ─────────────────────────────────────────────────────────────────

const NAV_ITEMS = [
  { to: "/", label: "Tableau de bord", icon: LayoutDashboard, end: true },
  { to: "/workspace", label: "Nouveau travail", icon: Sparkles, end: false },
  { to: "/topics", label: "Sujets", icon: Layers3, end: false },
  { to: "/reads", label: "Lectures", icon: BookOpen, end: false },
  { to: "/lookup", label: "Rechercher", icon: Search, end: false },
];

// ── Sidebar nav ───────────────────────────────────────────────────────────────

function SidebarNav() {
  return (
    <nav className="space-y-0.5">
      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors",
              isActive
                ? "bg-sidebar-accent font-medium text-sidebar-active"
                : "text-sidebar-fg hover:bg-white/[0.06] hover:text-sidebar-active"
            )
          }
        >
          <Icon className="h-4 w-4 shrink-0" />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

// ── Sidebar recent topics ─────────────────────────────────────────────────────

function SidebarTopics() {
  const { data, isLoading } = useQuery({
    queryKey: ["topics"],
    queryFn: shadowPoApi.getTopics,
    refetchInterval: 30_000,
    staleTime: 15_000,
  });

  return (
    <div className="space-y-2">
      <p className="px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-sidebar-muted">
        Sujets récents
      </p>
      <div className="space-y-0.5">
        {isLoading ? (
          [1, 2, 3].map((i) => (
            <div key={i} className="mx-1 h-8 animate-pulse rounded-xl bg-white/[0.05]" />
          ))
        ) : data?.length ? (
          data.slice(0, 7).map((topic) => (
            <NavLink
              key={topic.topic_id}
              to={`/topics/${topic.topic_id}`}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-active"
                    : "text-sidebar-fg hover:bg-white/[0.06] hover:text-sidebar-active"
                )
              }
            >
              <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
              <span className="truncate text-xs">{truncate(topic.topic_label, 30)}</span>
            </NavLink>
          ))
        ) : (
          <p className="px-3 text-xs text-sidebar-muted">
            Aucun sujet pour l'instant
          </p>
        )}
      </div>
      {(data?.length ?? 0) > 7 ? (
        <Link
          to="/topics"
          className="block px-3 text-xs text-sidebar-muted hover:text-sidebar-fg transition-colors"
        >
          Voir tous les sujets →
        </Link>
      ) : null}
    </div>
  );
}

// ── Sidebar status ────────────────────────────────────────────────────────────

function SidebarStatus() {
  const { isError, isFetching } = useQuery({
    queryKey: ["health"],
    queryFn: () => fetch("/health").then((r) => { if (!r.ok) throw new Error(); return r.json(); }),
    retry: 1,
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

  return (
    <div className="flex items-center gap-2 px-3 py-2.5">
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full",
          isError ? "bg-red-400" : isFetching ? "bg-amber-400" : "bg-emerald-400"
        )}
      />
      <span className="text-xs text-sidebar-muted">
        {isError ? "Backend hors ligne" : "Backend actif"}
      </span>
    </div>
  );
}

// ── AppShell ──────────────────────────────────────────────────────────────────

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      {/* ── Sidebar ─────────────────────────────────── */}
      <aside className="sidebar-scroll flex h-screen w-64 shrink-0 flex-col overflow-y-auto border-r border-white/[0.07] bg-sidebar sticky top-0">
        {/* Brand */}
        <div className="border-b border-white/[0.07] px-4 py-5">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary">
              <BrainCircuit className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold leading-none text-sidebar-active">
                Shadow PO AI
              </p>
              <p className="mt-0.5 text-[10px] text-sidebar-muted">
                Workspace produit
              </p>
            </div>
          </Link>
        </div>

        {/* Navigation + Topics */}
        <div className="flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-4 sidebar-scroll">
          <SidebarNav />
          <div className="border-t border-white/[0.07]" />
          <SidebarTopics />
        </div>

        {/* Status */}
        <div className="border-t border-white/[0.07] px-1 py-1">
          <SidebarStatus />
        </div>
      </aside>

      {/* ── Main ────────────────────────────────────── */}
      <div className="flex flex-1 flex-col min-w-0">
        <main className="flex-1 px-6 py-8 md:px-10">
          <div className="mx-auto max-w-[1200px] animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
