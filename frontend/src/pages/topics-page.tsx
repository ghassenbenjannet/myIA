import { useQuery } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

import { PageHeader } from "@/components/shared/page-header";
import { EmptyState, QueryError, QueryLoading } from "@/components/shared/query-state";
import { TopicCard } from "@/components/topics/topic-card";
import { shadowPoApi } from "@/lib/api/shadow-po-api";

export function TopicsPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["topics"],
    queryFn: shadowPoApi.getTopics,
  });

  const count = data?.length ?? 0;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Sujets"
        title={count ? `${count} sujet${count > 1 ? "s" : ""}` : "Sujets de travail"}
        description="Chaque sujet regroupe les runs d'un même dossier — run racine, historique des continuations, artefact courant."
        action={
          <Link
            to="/workspace"
            className="inline-flex items-center gap-2 rounded-2xl bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground"
          >
            <Sparkles className="h-4 w-4" />
            Nouveau
          </Link>
        }
      />

      {isLoading ? <QueryLoading label="Chargement des sujets…" /> : null}
      {isError ? <QueryError label="La liste des sujets n'a pas pu être chargée." /> : null}

      {!isLoading && !isError && !data?.length ? (
        <EmptyState
          title="Aucun sujet pour l'instant"
          description="Le backend ne contient pas encore de dossier de travail en mémoire. Lancez une analyse pour créer le premier."
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
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {data.map((topic) => (
            <TopicCard key={topic.topic_id} topic={topic} />
          ))}
        </div>
      ) : null}
    </div>
  );
}
