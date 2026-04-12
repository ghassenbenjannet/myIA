import { useQuery } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { EmptyState, QueryError, QueryLoading } from "@/components/shared/query-state";
import { Card, CardContent } from "@/components/ui/card";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { formatDate } from "@/lib/utils";

export function ArtifactViewPage() {
  const { runId = "" } = useParams();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["run", runId],
    queryFn: () => shadowPoApi.getRun(runId),
    enabled: Boolean(runId),
  });

  return (
    <div className="space-y-8">
      {/* ── Fil d'Ariane ──────────────────────────────── */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        {data?.topic_id ? (
          <Link
            to={`/topics/${data.topic_id}`}
            className="flex items-center gap-1 hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Retour au sujet
          </Link>
        ) : (
          <Link
            to="/topics"
            className="flex items-center gap-1 hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Sujets
          </Link>
        )}
        <span>/</span>
        <span className="font-mono text-xs">{runId.slice(0, 16)}…</span>
      </div>

      {isLoading ? <QueryLoading label="Chargement de l'artefact…" /> : null}
      {isError ? <QueryError label="L'artefact n'a pas pu être chargé." /> : null}
      {!isLoading && !isError && !data ? (
        <EmptyState
          title="Artefact introuvable"
          description="Ce run n'existe pas ou n'est plus disponible en mémoire."
        />
      ) : null}

      {data ? (
        <div className="grid gap-6 xl:grid-cols-[1fr_260px]">
          <ArtifactRenderer result={data.result} />

          <div className="space-y-4">
            <Card className="shadow-card">
              <CardContent className="space-y-3">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  Métadonnées
                </p>
                <div className="space-y-2 text-sm">
                  <div>
                    <p className="text-xs text-muted-foreground">Run ID</p>
                    <p className="mt-0.5 font-mono text-xs break-all">{data.run_id}</p>
                  </div>
                  {data.topic_id ? (
                    <div>
                      <p className="text-xs text-muted-foreground">Sujet</p>
                      <Link
                        to={`/topics/${data.topic_id}`}
                        className="mt-0.5 block font-mono text-xs text-primary hover:underline break-all"
                      >
                        {data.topic_id}
                      </Link>
                    </div>
                  ) : null}
                  <div>
                    <p className="text-xs text-muted-foreground">Créé</p>
                    <p className="mt-0.5 text-xs font-medium">{formatDate(data.created_at)}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Workflow</p>
                    <p className="mt-0.5 text-xs font-medium">{data.final_workflow}</p>
                  </div>
                  {data.continuation_action ? (
                    <div>
                      <p className="text-xs text-muted-foreground">Continuation</p>
                      <p className="mt-0.5 text-xs font-medium">{data.continuation_action}</p>
                    </div>
                  ) : null}
                </div>
              </CardContent>
            </Card>

            <details className="rounded-2xl bg-card shadow-card">
              <summary className="cursor-pointer px-5 py-3.5 text-xs font-medium text-muted-foreground hover:text-foreground">
                Payload brut
              </summary>
              <pre className="overflow-auto rounded-b-2xl bg-slate-950 px-5 py-4 text-[11px] leading-5 text-slate-300">
                {JSON.stringify(data, null, 2)}
              </pre>
            </details>
          </div>
        </div>
      ) : null}
    </div>
  );
}
