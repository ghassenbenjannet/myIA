import { useQuery } from "@tanstack/react-query";
import { BookOpen, FileText, Layers3, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { PageHeader } from "@/components/shared/page-header";
import { EmptyState, QueryError, QueryLoading } from "@/components/shared/query-state";
import { TopicCard } from "@/components/topics/topic-card";
import { Card, CardContent } from "@/components/ui/card";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { truncate } from "@/lib/utils";
import { useWorkspaceStore } from "@/stores/workspace-store";

const WORKFLOW_LABELS: Record<string, string> = {
  analysis: "Analyse",
  ticket: "Ticket",
  documentation: "Doc",
  source_summary: "Source",
  jira_read: "Jira",
  confluence_read: "Confluence",
};

const QUICK_ACTIONS = [
  {
    to: "/workspace",
    icon: Sparkles,
    label: "Nouvelle analyse",
    description: "Qualifier un besoin, bug ou demande",
    color: "text-primary",
    bg: "bg-accent/60",
  },
  {
    to: "/reads",
    icon: BookOpen,
    label: "Lire une source",
    description: "URL, Jira ou page Confluence",
    color: "text-indigo-600",
    bg: "bg-indigo-50",
  },
  {
    to: "/topics",
    icon: Layers3,
    label: "Voir les sujets",
    description: "Reprendre un dossier en cours",
    color: "text-amber-600",
    bg: "bg-amber-50",
  },
];

export function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["topics", "dashboard"],
    queryFn: shadowPoApi.getTopics,
  });
  const recentRuns = useWorkspaceStore((s) => s.recentRuns);

  const activeCount = data?.filter((t) => t.status === "active").length ?? 0;

  return (
    <div className="space-y-10">
      <div className="flex items-end justify-between gap-6">
        <PageHeader
          eyebrow="Tableau de bord"
          title="Shadow PO AI"
          description="Qualifiez vos besoins, lisez vos sources et organisez votre travail par sujet."
        />

        {/* Stats inline */}
        <div className="flex shrink-0 items-center gap-6 rounded-2xl bg-card px-5 py-3 shadow-card text-sm">
          <div className="text-center">
            <p className="text-2xl font-semibold leading-none">{data?.length ?? "—"}</p>
            <p className="mt-1 text-xs text-muted-foreground">sujets</p>
          </div>
          <div className="h-8 w-px bg-border" />
          <div className="text-center">
            <p className="text-2xl font-semibold leading-none">{activeCount || "—"}</p>
            <p className="mt-1 text-xs text-muted-foreground">actifs</p>
          </div>
          <div className="h-8 w-px bg-border" />
          <div className="text-center">
            <p className="text-2xl font-semibold leading-none">{recentRuns.length || "—"}</p>
            <p className="mt-1 text-xs text-muted-foreground">récents</p>
          </div>
        </div>
      </div>

      {/* ── Quick actions ─────────────────────────────────── */}
      <section>
        <p className="mb-4 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
          Actions rapides
        </p>
        <div className="grid gap-3 sm:grid-cols-3">
          {QUICK_ACTIONS.map(({ to, icon: Icon, label, description, color, bg }) => (
            <Link
              key={to}
              to={to}
              className="group flex items-center gap-4 rounded-2xl bg-card px-5 py-4 shadow-card transition-shadow hover:shadow-card-hover"
            >
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${bg}`}>
                <Icon className={`h-5 w-5 ${color}`} />
              </div>
              <div>
                <p className="text-sm font-semibold">{label}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{description}</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      <div className="grid gap-8 lg:grid-cols-[1fr_280px]">
        {/* ── Recent topics ─────────────────────────────────── */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Sujets récents
            </p>
            <Link to="/topics" className="text-xs text-primary hover:underline">
              Voir tout →
            </Link>
          </div>

          {isLoading ? <QueryLoading label="Chargement des sujets…" /> : null}
          {isError ? <QueryError label="Impossible de charger les sujets." /> : null}
          {!isLoading && !isError && !data?.length ? (
            <EmptyState
              title="Aucun sujet"
              description="Lancez une analyse ou lisez une source pour créer votre premier dossier."
              action={
                <Link
                  to="/workspace"
                  className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground"
                >
                  <Sparkles className="h-4 w-4" />
                  Commencer
                </Link>
              }
            />
          ) : null}

          {data?.length ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {data.slice(0, 6).map((topic) => (
                <TopicCard key={topic.topic_id} topic={topic} />
              ))}
            </div>
          ) : null}
        </section>

        {/* ── Recent runs sidebar ───────────────────────────── */}
        <aside className="space-y-4">
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
            Derniers runs
          </p>
          {recentRuns.length ? (
            <div className="space-y-2">
              {recentRuns.slice(0, 5).map((run) => (
                <Link
                  key={run.runId}
                  to={`/topics/${run.topicId}`}
                  className="group flex items-start gap-3 rounded-2xl bg-card px-4 py-3 shadow-card transition-shadow hover:shadow-card-hover"
                >
                  <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-primary/10">
                    <FileText className="h-3 w-3 text-primary" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{truncate(run.label, 44)}</p>
                    <p className="mt-0.5 text-[10px] text-muted-foreground">
                      {WORKFLOW_LABELS[run.workflow] ?? run.workflow}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-sm text-muted-foreground">
                  Aucun run récent mémorisé.
                </p>
              </CardContent>
            </Card>
          )}
        </aside>
      </div>
    </div>
  );
}
