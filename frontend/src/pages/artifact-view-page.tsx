import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState, QueryError, QueryLoading } from "@/components/shared/query-state";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import { shadowPoApi } from "@/lib/api/shadow-po-api";

export function ArtifactViewPage() {
  const { runId = "" } = useParams();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["run", runId],
    queryFn: () => shadowPoApi.getRun(runId),
    enabled: Boolean(runId),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Artifact View"
        title="Artefact courant"
        description="Vue dédiée d'un run avec sa sortie structurée et ses métadonnées secondaires accessibles sans prendre le dessus sur le contenu métier."
      />

      {isLoading ? <QueryLoading label="Chargement du run..." /> : null}
      {isError ? <QueryError label="Le run n'a pas pu etre charge." /> : null}
      {!isLoading && !isError && !data ? (
        <EmptyState title="Run introuvable" description="Le run demandé n'existe pas ou n'est plus disponible." />
      ) : null}

      {data ? (
        <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
          <ArtifactRenderer result={data.result} />
          <Card>
            <CardContent className="space-y-4">
              <p className="text-xs uppercase tracking-[0.16em] text-primary">Meta secondaire</p>
              <div className="grid gap-3 text-sm text-muted-foreground">
                <div className="rounded-2xl bg-secondary p-4">
                  <p className="text-xs uppercase tracking-wide">Run</p>
                  <strong className="mt-2 block text-foreground">{data.run_id}</strong>
                </div>
                <div className="rounded-2xl bg-secondary p-4">
                  <p className="text-xs uppercase tracking-wide">Topic</p>
                  <strong className="mt-2 block text-foreground">{data.topic_id ?? "Aucun"}</strong>
                </div>
                <div className="rounded-2xl bg-secondary p-4">
                  <p className="text-xs uppercase tracking-wide">Created at</p>
                  <strong className="mt-2 block text-foreground">{formatDate(data.created_at)}</strong>
                </div>
              </div>
              <details className="rounded-2xl bg-secondary p-4">
                <summary className="cursor-pointer text-sm font-medium">Debug payload</summary>
                <pre className="mt-4 overflow-auto rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">
                  {JSON.stringify(data, null, 2)}
                </pre>
              </details>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
