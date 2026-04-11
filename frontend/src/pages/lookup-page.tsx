import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { shadowPoApi } from "@/lib/api/shadow-po-api";

export function LookupPage() {
  const [runId, setRunId] = useState("");
  const [continueRunId, setContinueRunId] = useState("");
  const [action, setAction] = useState("draft_ticket");
  const mutation = useMutation({
    mutationFn: shadowPoApi.getRun,
  });
  const continueMutation = useMutation({
    mutationFn: ({ runId, action }: { runId: string; action: string }) => shadowPoApi.continueRun(runId, action),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Lookup"
        title="Relire un run"
        description="Retrouver un artefact produit, son contexte et sa filiation sans passer par les endpoints bruts."
      />

      <div className="grid gap-5 xl:grid-cols-2">
        <Card>
          <CardContent className="flex gap-3 max-md:flex-col">
            <Input value={runId} onChange={(event) => setRunId(event.target.value)} placeholder="UUID du run" />
            <Button onClick={() => mutation.mutate(runId)}>Lire /runs/{`{run_id}`}</Button>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
            <Input value={continueRunId} onChange={(event) => setContinueRunId(event.target.value)} placeholder="UUID du run parent" />
            <select
              className="flex h-11 rounded-2xl border border-border bg-white px-4 py-2 text-sm"
              value={action}
              onChange={(event) => setAction(event.target.value)}
            >
              <option value="refine_analysis">refine_analysis</option>
              <option value="draft_ticket">draft_ticket</option>
              <option value="draft_documentation">draft_documentation</option>
            </select>
            <Button onClick={() => continueMutation.mutate({ runId: continueRunId, action })}>
              Continuer
            </Button>
          </CardContent>
        </Card>
      </div>

      {mutation.data ? <ArtifactRenderer result={mutation.data.result} /> : null}
      {continueMutation.data ? <ArtifactRenderer result={continueMutation.data.result} /> : null}
    </div>
  );
}
