import { useMutation } from "@tanstack/react-query";
import { ArrowRight, Hash, Loader2, Repeat2 } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import type { AvailableAction } from "@/types/api";

const ACTION_LABELS: Record<AvailableAction, string> = {
  refine_analysis: "Affiner l'analyse",
  draft_ticket: "Générer un ticket",
  draft_documentation: "Générer la documentation",
};

export function LookupPage() {
  const [runId, setRunId] = useState("");
  const [continueRunId, setContinueRunId] = useState("");
  const [action, setAction] = useState<AvailableAction>("draft_ticket");

  const lookupMutation = useMutation({
    mutationFn: shadowPoApi.getRun,
  });

  const continueMutation = useMutation({
    mutationFn: ({ runId, action }: { runId: string; action: string }) =>
      shadowPoApi.continueRun(runId, action),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Rechercher"
        title="Retrouver un artefact"
        description="Accédez à un run par son identifiant ou déclenchez une continuation depuis un run existant."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        {/* ── Lookup par ID ── */}
        <div className="flex flex-col gap-4">
          <Card className="shadow-card">
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-accent">
                  <Hash className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Lookup
                  </p>
                  <h3 className="text-base font-semibold">Lire un run</h3>
                </div>
              </div>
              <p className="text-xs leading-5 text-muted-foreground">
                Collez l'UUID d'un run pour retrouver son artefact et ses métadonnées.
              </p>
              <div className="flex gap-2">
                <Input
                  value={runId}
                  onChange={(e) => setRunId(e.target.value)}
                  placeholder="UUID du run…"
                  className="font-mono text-xs"
                />
                <Button
                  onClick={() => lookupMutation.mutate(runId)}
                  disabled={!runId.trim() || lookupMutation.isPending}
                  className="shrink-0 gap-2"
                >
                  {lookupMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <ArrowRight className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {lookupMutation.isError ? (
                <p className="rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">
                  Run introuvable ou backend indisponible.
                </p>
              ) : null}
              {lookupMutation.data?.topic_id ? (
                <Link
                  to={`/topics/${lookupMutation.data.topic_id}`}
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-primary hover:underline"
                >
                  Ouvrir le sujet associé <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              ) : null}
            </CardContent>
          </Card>
          {lookupMutation.data ? (
            <ArtifactRenderer result={lookupMutation.data.result} />
          ) : null}
        </div>

        {/* ── Continuer un run ── */}
        <div className="flex flex-col gap-4">
          <Card className="shadow-card">
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-accent">
                  <Repeat2 className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                    Continuation
                  </p>
                  <h3 className="text-base font-semibold">Continuer un run</h3>
                </div>
              </div>
              <p className="text-xs leading-5 text-muted-foreground">
                Entrez l'UUID d'un run source et choisissez l'action à enchaîner.
              </p>
              <Input
                value={continueRunId}
                onChange={(e) => setContinueRunId(e.target.value)}
                placeholder="UUID du run parent…"
                className="font-mono text-xs"
              />
              <Select
                value={action}
                onChange={(e) => setAction(e.target.value as AvailableAction)}
              >
                {(Object.keys(ACTION_LABELS) as AvailableAction[]).map((a) => (
                  <option key={a} value={a}>
                    {ACTION_LABELS[a]}
                  </option>
                ))}
              </Select>
              <Button
                onClick={() => continueMutation.mutate({ runId: continueRunId, action })}
                disabled={!continueRunId.trim() || continueMutation.isPending}
                className="w-full gap-2"
              >
                {continueMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Repeat2 className="h-4 w-4" />
                )}
                Déclencher la continuation
              </Button>
              {continueMutation.isError ? (
                <p className="rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">
                  Continuation échouée — run introuvable ou action non supportée.
                </p>
              ) : null}
              {continueMutation.data?.topic_id ? (
                <Link
                  to={`/topics/${continueMutation.data.topic_id}`}
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-primary hover:underline"
                >
                  Ouvrir le sujet mis à jour <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              ) : null}
            </CardContent>
          </Card>
          {continueMutation.data ? (
            <ArtifactRenderer result={continueMutation.data.result} />
          ) : null}
        </div>
      </div>
    </div>
  );
}
