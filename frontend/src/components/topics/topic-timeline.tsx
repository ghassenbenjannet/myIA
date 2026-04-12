import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { formatDate, truncate } from "@/lib/utils";
import type { AvailableAction, TopicRunView } from "@/types/api";

const ACTION_LABELS: Record<AvailableAction, string> = {
  refine_analysis: "Affiner l'analyse",
  draft_ticket: "Générer un ticket",
  draft_documentation: "Générer la documentation",
};

function ContinuationButton({
  runId,
  action,
  topicId,
  onResult,
}: {
  runId: string;
  action: AvailableAction;
  topicId: string;
  onResult: () => void;
}) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: () => shadowPoApi.continueRun(runId, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["topic", topicId] });
      queryClient.invalidateQueries({ queryKey: ["topics"] });
      onResult();
    },
  });

  return (
    <button
      onClick={() => mutation.mutate()}
      disabled={mutation.isPending}
      className="rounded-2xl bg-primary px-4 py-2 text-sm text-primary-foreground disabled:opacity-60 hover:bg-primary/90 transition"
    >
      {mutation.isPending ? "En cours…" : ACTION_LABELS[action]}
    </button>
  );
}

export function TopicTimeline({ runs, topicId }: { runs: TopicRunView[]; topicId: string }) {
  const [expandedRunId, setExpandedRunId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  function handleContinuationDone() {
    setExpandedRunId(null);
  }

  if (!runs.length) {
    return <p className="text-sm text-muted-foreground">Aucun run dans ce topic.</p>;
  }

  return (
    <div className="relative pl-6">
      <div className="absolute bottom-2 left-2 top-2 w-px bg-gradient-to-b from-primary/40 to-primary/10" />
      <div className="grid gap-4">
        {runs.map((run) => {
          const isExpanded = expandedRunId === run.run_id;
          return (
            <Card key={run.run_id} className="relative overflow-visible">
              <span className="absolute -left-[22px] top-8 h-3 w-3 rounded-full bg-primary shadow-[0_0_0_6px_rgba(15,118,110,0.12)]" />
              <CardContent className="space-y-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">
                      {run.final_workflow}
                      {run.continuation_action ? ` · ${run.continuation_action}` : ""}
                    </p>
                    <h4 className="mt-2 text-lg font-semibold">{truncate(run.raw_input, 96)}</h4>
                  </div>
                  <Badge>{formatDate(run.created_at)}</Badge>
                </div>

                {run.available_actions.length ? (
                  <div className="space-y-2">
                    <p className="text-xs uppercase tracking-[0.12em] text-muted-foreground">Actions suivantes</p>
                    <div className="flex flex-wrap gap-2">
                      {run.available_actions.map((action) => (
                        <ContinuationButton
                          key={action}
                          runId={run.run_id}
                          action={action}
                          topicId={topicId}
                          onResult={handleContinuationDone}
                        />
                      ))}
                    </div>
                  </div>
                ) : null}

                <div className="flex flex-wrap gap-3">
                  <button
                    onClick={() => setExpandedRunId(isExpanded ? null : run.run_id)}
                    className="rounded-2xl bg-secondary px-4 py-2 text-sm hover:bg-secondary/80 transition"
                  >
                    {isExpanded ? "Masquer l'artefact" : "Voir l'artefact"}
                  </button>
                  <Link
                    className="rounded-2xl bg-secondary px-4 py-2 text-sm hover:bg-secondary/80 transition"
                    to={`/artifacts/${run.run_id}`}
                  >
                    Page dédiée
                  </Link>
                </div>

                {isExpanded ? (
                  <div className="pt-2">
                    <ArtifactRenderer result={run.result} />
                  </div>
                ) : null}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
