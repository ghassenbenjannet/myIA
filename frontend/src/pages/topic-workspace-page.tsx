import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, GitCommit, Loader2 } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { EmptyState, QueryError, QueryLoading } from "@/components/shared/query-state";
import { TopicTimeline } from "@/components/topics/topic-timeline";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { formatDate } from "@/lib/utils";
import type { AvailableAction } from "@/types/api";

const ACTION_META: Record<AvailableAction, { label: string; hint: string }> = {
  refine_analysis: {
    label: "Affiner l'analyse",
    hint: "Approfondir les impacts et ambiguïtés",
  },
  draft_ticket: {
    label: "Générer un ticket",
    hint: "Produire un ticket structuré et priorisable",
  },
  draft_documentation: {
    label: "Générer la documentation",
    hint: "Créer un document de travail structuré",
  },
};

export function TopicWorkspacePage() {
  const { topicId = "" } = useParams();
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["topic", topicId],
    queryFn: () => shadowPoApi.getTopic(topicId),
    enabled: Boolean(topicId),
  });

  const continueMutation = useMutation({
    mutationFn: ({ runId, action }: { runId: string; action: string }) =>
      shadowPoApi.continueRun(runId, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["topic", topicId] });
      queryClient.invalidateQueries({ queryKey: ["topics"] });
    },
  });

  const latestActions = data?.latest_run?.available_actions ?? [];
  const latestRunId = data?.latest_run?.run_id;
  const currentResult =
    data?.latest_run?.result ?? (data?.runs?.length ? data.runs[0].result : null);

  return (
    <div className="space-y-8">
      {/* ── Fil d'Ariane ──────────────────────────────── */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link to="/topics" className="flex items-center gap-1 hover:text-foreground transition-colors">
          <ArrowLeft className="h-3.5 w-3.5" />
          Sujets
        </Link>
        <span>/</span>
        <span className="font-medium text-foreground truncate max-w-[320px]">
          {data?.topic.topic_label ?? "Chargement…"}
        </span>
      </div>

      {isLoading ? <QueryLoading label="Chargement du sujet…" /> : null}
      {isError ? <QueryError label="Le sujet n'a pas pu être chargé." /> : null}
      {!isLoading && !isError && !data ? (
        <EmptyState
          title="Sujet introuvable"
          description="Ce dossier n'existe pas ou n'est plus disponible en mémoire."
        />
      ) : null}

      {data ? (
        <>
          {/* ── Titre + meta ─────────────────────────────── */}
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="font-display text-3xl leading-tight">{data.topic.topic_label}</h1>
              <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                <Badge>{data.topic.status}</Badge>
                <span className="flex items-center gap-1.5">
                  <GitCommit className="h-3.5 w-3.5" />
                  {data.runs.length} run{data.runs.length > 1 ? "s" : ""}
                </span>
                <span>Mis à jour {formatDate(data.topic.updated_at)}</span>
              </div>
            </div>
          </div>

          {/* ── Actions suivantes ─────────────────────────── */}
          {latestActions.length && latestRunId ? (
            <Card className="border-primary/20 bg-accent/40 shadow-none">
              <CardContent className="space-y-3">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">
                  Actions suivantes
                </p>
                <div className="grid gap-2.5 sm:grid-cols-3">
                  {latestActions.map((action) => {
                    const meta = ACTION_META[action];
                    const isRunning =
                      continueMutation.isPending &&
                      continueMutation.variables?.action === action;
                    return (
                      <button
                        key={action}
                        onClick={() =>
                          continueMutation.mutate({ runId: latestRunId, action })
                        }
                        disabled={continueMutation.isPending}
                        className="flex items-start gap-3 rounded-xl bg-white/70 px-4 py-3 text-left shadow-action transition hover:bg-white hover:shadow-card disabled:opacity-50"
                      >
                        {isRunning ? (
                          <Loader2 className="mt-0.5 h-4 w-4 shrink-0 animate-spin text-primary" />
                        ) : (
                          <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                        )}
                        <div>
                          <p className="text-sm font-medium">{meta?.label ?? action}</p>
                          {meta?.hint ? (
                            <p className="mt-0.5 text-xs text-muted-foreground">{meta.hint}</p>
                          ) : null}
                        </div>
                      </button>
                    );
                  })}
                </div>
                {continueMutation.isError ? (
                  <p className="rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">
                    La continuation a échoué. Vérifiez que le backend est disponible.
                  </p>
                ) : null}
              </CardContent>
            </Card>
          ) : null}

          {/* ── Artefact courant + meta ───────────────────── */}
          {currentResult ? (
            <div className="grid gap-6 xl:grid-cols-[1fr_260px]">
              <ArtifactRenderer result={currentResult} />

              <div className="space-y-4">
                <Card className="shadow-card">
                  <CardContent className="space-y-4">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Dossier
                    </p>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between gap-2">
                        <span className="text-muted-foreground">Statut</span>
                        <Badge>{data.topic.status}</Badge>
                      </div>
                      <div className="flex justify-between gap-2">
                        <span className="text-muted-foreground">Runs</span>
                        <span className="font-medium">{data.runs.length}</span>
                      </div>
                      <div className="flex justify-between gap-2">
                        <span className="text-muted-foreground">Créé</span>
                        <span className="font-medium text-xs">{formatDate(data.topic.created_at)}</span>
                      </div>
                      <div className="flex justify-between gap-2">
                        <span className="text-muted-foreground">Modifié</span>
                        <span className="font-medium text-xs">{formatDate(data.topic.updated_at)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {data.root_run && data.root_run.run_id !== data.latest_run?.run_id ? (
                  <Card className="shadow-card">
                    <CardContent className="space-y-2">
                      <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                        Run racine
                      </p>
                      <Link
                        to={`/artifacts/${data.root_run.run_id}`}
                        className="block truncate font-mono text-xs text-primary hover:underline"
                      >
                        {data.root_run.run_id}
                      </Link>
                    </CardContent>
                  </Card>
                ) : null}
              </div>
            </div>
          ) : (
            <EmptyState
              title="Aucun artefact"
              description="Ce sujet ne contient pas encore de résultat."
            />
          )}

          {/* ── Timeline ─────────────────────────────────── */}
          {data.runs.length ? (
            <div className="space-y-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Historique des runs
              </p>
              <TopicTimeline runs={data.runs} topicId={topicId} />
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
