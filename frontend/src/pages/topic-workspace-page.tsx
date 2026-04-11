import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { PageHeader } from "@/components/shared/page-header";
import { EmptyState, QueryError, QueryLoading } from "@/components/shared/query-state";
import { TopicTimeline } from "@/components/topics/topic-timeline";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import { shadowPoApi } from "@/lib/api/shadow-po-api";

export function TopicWorkspacePage() {
  const { topicId = "" } = useParams();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["topic", topicId],
    queryFn: () => shadowPoApi.getTopic(topicId),
    enabled: Boolean(topicId),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Topic Workspace"
        title={data?.topic.topic_label ?? "Dossier topic"}
        description="Vue dossier d'un sujet : artefact courant, timeline ordonnée, run racine, latest run et prochaines actions réellement supportées."
      />

      {isLoading ? <QueryLoading label="Chargement du topic..." /> : null}
      {isError ? <QueryError label="Le topic n'a pas pu etre charge." /> : null}
      {!isLoading && !isError && !data ? (
        <EmptyState title="Topic introuvable" description="Ce dossier n'existe pas ou n'est plus disponible." />
      ) : null}

      {data ? (
        <>
          <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
            <ArtifactRenderer result={data.latest_run?.result ?? data.runs[0].result} />
            <Card>
              <CardContent className="space-y-4">
                <p className="text-xs uppercase tracking-[0.16em] text-primary">Etat du sujet</p>
                <h3 className="text-2xl font-semibold">{data.topic.topic_label}</h3>
                <div className="grid gap-3 text-sm text-muted-foreground">
                  <div className="rounded-2xl bg-secondary p-4">
                    <p className="text-xs uppercase tracking-wide">Updated</p>
                    <strong className="mt-2 block text-foreground">{formatDate(data.topic.updated_at)}</strong>
                  </div>
                  <div className="rounded-2xl bg-secondary p-4">
                    <p className="text-xs uppercase tracking-wide">Latest run</p>
                    <strong className="mt-2 block text-foreground">{data.topic.latest_run_id}</strong>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
            <Card>
              <CardContent className="space-y-4">
                <p className="text-xs uppercase tracking-[0.16em] text-primary">Runs structurants</p>
                {data.root_run ? (
                  <div className="rounded-2xl bg-secondary p-4">
                    <h4 className="font-semibold">Root run</h4>
                    <p className="mt-2 text-sm text-muted-foreground">{data.root_run.run_id}</p>
                  </div>
                ) : null}
                {data.latest_run ? (
                  <div className="rounded-2xl bg-secondary p-4">
                    <h4 className="font-semibold">Latest run</h4>
                    <p className="mt-2 text-sm text-muted-foreground">{data.latest_run.run_id}</p>
                  </div>
                ) : null}
              </CardContent>
            </Card>

            <div className="space-y-4">
              <p className="text-xs uppercase tracking-[0.16em] text-primary">Timeline</p>
              <TopicTimeline runs={data.runs} />
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
