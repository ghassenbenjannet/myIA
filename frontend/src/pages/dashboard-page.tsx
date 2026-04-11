import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { PageHeader } from "@/components/shared/page-header";
import { EmptyState, QueryError, QueryLoading } from "@/components/shared/query-state";
import { TopicCard } from "@/components/topics/topic-card";
import { Card, CardContent } from "@/components/ui/card";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["topics", "dashboard"],
    queryFn: shadowPoApi.getTopics,
  });
  const recentRuns = useWorkspaceStore((state) => state.recentRuns);

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Vue d'ensemble"
        title="Workspace premium orienté dossier de travail"
        description="Le parcours principal part du sujet, déroule la timeline des runs, expose l'artefact courant puis propose les actions suivantes utiles."
      />

      <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="overflow-hidden bg-[linear-gradient(135deg,rgba(15,118,110,0.12),rgba(255,255,255,0.82))]">
          <CardContent className="space-y-6">
            <div>
              <p className="text-xs uppercase tracking-[0.16em] text-primary">Hero</p>
              <h2 className="mt-3 font-display text-5xl leading-none">Vue d'ensemble</h2>
              <p className="mt-4 max-w-2xl text-sm leading-7 text-muted-foreground">
                Ouvrir les topics récents, repartir d’un artefact utile et déclencher un nouveau travail sans passer par une page de debug.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link className="inline-flex rounded-2xl bg-primary px-4 py-3 text-sm text-primary-foreground" to="/workspace">
                Nouveau travail
              </Link>
              <Link className="inline-flex rounded-2xl bg-secondary px-4 py-3 text-sm text-foreground" to="/topics">
                Explorer les topics
              </Link>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4">
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Reprendre</p>
            <h3 className="text-2xl font-semibold">Historique local utile</h3>
            {recentRuns.length ? (
              <div className="grid gap-3">
                {recentRuns.slice(0, 3).map((run) => (
                  <div key={run.runId} className="rounded-2xl bg-secondary p-4">
                    <p className="text-sm font-medium">{run.label}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{run.runId}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Aucun run recent memorise cote front.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <section className="space-y-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Topics recents</p>
            <h2 className="text-3xl font-semibold">Sujets actifs</h2>
          </div>
          <Link className="inline-flex rounded-2xl border border-border px-4 py-3 text-sm" to="/topics">
            Voir tous les topics
          </Link>
        </div>

        {isLoading ? <QueryLoading label="Chargement des topics..." /> : null}
        {isError ? <QueryError label="Les topics n'ont pas pu etre charges." /> : null}
        {!isLoading && !isError && !data?.length ? (
          <EmptyState
            title="Aucun topic cote serveur"
            description="Lancez un process, un read Jira, une lecture source ou un read Confluence pour initialiser un dossier de travail."
          />
        ) : null}
        {data?.length ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {data.slice(0, 6).map((topic) => (
              <TopicCard key={topic.topic_id} topic={topic} />
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}
