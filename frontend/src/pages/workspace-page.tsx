import { useQuery } from "@tanstack/react-query";

import { ProcessForm } from "@/components/forms/process-form";
import { PageHeader } from "@/components/shared/page-header";
import { TopicCard } from "@/components/topics/topic-card";
import { Card, CardContent } from "@/components/ui/card";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function WorkspacePage() {
  const recentRuns = useWorkspaceStore((state) => state.recentRuns);
  const { data } = useQuery({
    queryKey: ["topics", "workspace"],
    queryFn: shadowPoApi.getTopics,
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Nouveau travail"
        title="Demande métier, lectures, prochaines actions"
        description="Le workspace full stack est pensé comme une base produit : créer, relire, rattacher à un topic et reprendre l'étape suivante utile."
      />

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <ProcessForm />

        <div className="space-y-5">
          <Card>
            <CardContent className="space-y-4">
              <p className="text-xs uppercase tracking-[0.16em] text-primary">Bloc reprendre</p>
              <h3 className="text-2xl font-semibold">Derniers runs utiles</h3>
              {recentRuns.length ? (
                <div className="grid gap-3">
                  {recentRuns.map((run) => (
                    <div key={run.runId} className="rounded-2xl bg-secondary p-4">
                      <p className="font-medium">{run.label}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{run.runId}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Aucun historique local pour le moment.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="space-y-4">
              <p className="text-xs uppercase tracking-[0.16em] text-primary">Sujets recents</p>
              <div className="grid gap-3">
                {data?.slice(0, 2).map((topic) => (
                  <TopicCard key={topic.topic_id} topic={topic} />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
