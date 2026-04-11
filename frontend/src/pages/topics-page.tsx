import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "@/components/shared/page-header";
import { EmptyState, QueryError, QueryLoading } from "@/components/shared/query-state";
import { TopicCard } from "@/components/topics/topic-card";
import { shadowPoApi } from "@/lib/api/shadow-po-api";

export function TopicsPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["topics"],
    queryFn: shadowPoApi.getTopics,
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Topics"
        title="Memoire par sujet"
        description="Chaque topic regroupe les runs d'un meme dossier de travail, le run racine, le latest run et les actions réellement disponibles."
      />

      {isLoading ? <QueryLoading label="Chargement des topics..." /> : null}
      {isError ? <QueryError label="La liste des topics n'a pas pu etre chargee." /> : null}
      {!isLoading && !isError && !data?.length ? (
        <EmptyState
          title="Aucun topic disponible"
          description="Le backend n'a encore aucun dossier de travail en mémoire."
        />
      ) : null}
      {data?.length ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.map((topic) => (
            <TopicCard key={topic.topic_id} topic={topic} />
          ))}
        </div>
      ) : null}
    </div>
  );
}
