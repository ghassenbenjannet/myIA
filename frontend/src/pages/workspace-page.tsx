import { useQuery } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { Link } from "react-router-dom";

import { ProcessForm } from "@/components/forms/process-form";
import { PageHeader } from "@/components/shared/page-header";
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

export function WorkspacePage() {
  const recentRuns = useWorkspaceStore((s) => s.recentRuns);
  const { data: topics } = useQuery({
    queryKey: ["topics", "workspace"],
    queryFn: shadowPoApi.getTopics,
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Nouveau travail"
        title="Qualifier une demande"
        description="Décrivez votre besoin — le moteur détecte le type, structure l'analyse et propose les actions suivantes."
      />

      <div className="grid gap-8 xl:grid-cols-[1fr_300px]">
        <ProcessForm />

        <aside className="space-y-5">
          {/* Runs récents */}
          {recentRuns.length ? (
            <div className="space-y-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Runs récents
              </p>
              <div className="space-y-2">
                {recentRuns.map((run) => (
                  <Link
                    key={run.runId}
                    to={`/topics/${run.topicId}`}
                    className="group flex items-start gap-3 rounded-2xl bg-card px-4 py-3 shadow-card transition-shadow hover:shadow-card-hover"
                  >
                    <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-primary/10">
                      <FileText className="h-3 w-3 text-primary" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">
                        {truncate(run.label, 42)}
                      </p>
                      <p className="mt-0.5 text-[10px] text-muted-foreground">
                        {WORKFLOW_LABELS[run.workflow] ?? run.workflow}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ) : null}

          {/* Topics récents */}
          {topics?.length ? (
            <div className="space-y-3">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Sujets récents
              </p>
              <div className="space-y-2">
                {topics.slice(0, 3).map((topic) => (
                  <TopicCard key={topic.topic_id} topic={topic} />
                ))}
              </div>
            </div>
          ) : null}
        </aside>
      </div>
    </div>
  );
}
