import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, BrainCircuit, Loader2, Zap } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { truncate } from "@/lib/utils";
import type { ProcessMode } from "@/types/api";
import { useWorkspaceStore } from "@/stores/workspace-store";

const WORKFLOW_LABELS: Record<string, string> = {
  analysis: "Analyse",
  ticket: "Ticket",
  documentation: "Documentation",
};
const TYPE_LABELS: Record<string, string> = {
  bug: "Bug",
  evolution: "Évolution",
  recipe: "Recette",
  documentation: "Documentation",
  po_pilotage: "PO Pilotage",
  analysis: "Analyse",
};

export function ProcessForm() {
  const rememberRun = useWorkspaceStore((s) => s.rememberRun);
  const queryClient = useQueryClient();
  const [userInput, setUserInput] = useState("");
  const [contextHint, setContextHint] = useState("");
  const [targetOutput, setTargetOutput] = useState("auto");
  const [mode, setMode] = useState<ProcessMode>("deterministic");

  const mutation = useMutation({
    mutationFn: shadowPoApi.process,
    onSuccess: (payload) => {
      rememberRun({
        runId: payload.run_id,
        topicId: payload.topic_id,
        workflow: payload.selected_workflow,
        label: truncate(userInput, 60),
      });
      queryClient.invalidateQueries({ queryKey: ["topics"] });
    },
  });

  const canSubmit = userInput.trim().length >= 3 && !mutation.isPending;

  return (
    <div className="space-y-5">
      <Card className="shadow-card">
        <CardContent className="space-y-5">
          <Textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Décrivez votre besoin : incident métier, demande d'évolution, besoin de documentation, note de pilotage PO…"
            rows={6}
            className="resize-none text-base"
          />

          <div className="grid gap-3 sm:grid-cols-[1fr_200px]">
            <Input
              value={contextHint}
              onChange={(e) => setContextHint(e.target.value)}
              placeholder="Contexte optionnel (ex: flux de remise, module facturation…)"
            />
            <Select
              value={targetOutput}
              onChange={(e) => setTargetOutput(e.target.value)}
            >
              <option value="auto">Sortie automatique</option>
              <option value="analysis">Analyse</option>
              <option value="ticket">Ticket</option>
              <option value="documentation">Documentation</option>
            </Select>
          </div>

          {/* ── Mode toggle ── */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setMode("deterministic")}
              className={`flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium transition ${
                mode === "deterministic"
                  ? "bg-secondary text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Zap className="h-3.5 w-3.5" />
              Déterministe
            </button>
            <button
              type="button"
              onClick={() => setMode("assisted")}
              className={`flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-medium transition ${
                mode === "assisted"
                  ? "bg-primary/10 text-primary shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <BrainCircuit className="h-3.5 w-3.5" />
              Assisté LLM
            </button>
          </div>

          <div className="flex items-center justify-between gap-4">
            <Button onClick={() => mutation.mutate({ user_input: userInput, context_hint: contextHint || null, target_output: targetOutput, mode })} disabled={!canSubmit} className="gap-2">
              {mutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Traitement…
                </>
              ) : (
                <>
                  Analyser
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </Button>
            {mutation.isError ? (
              <p className="text-sm text-red-600">
                Erreur — vérifiez que le backend est disponible.
              </p>
            ) : null}
          </div>
        </CardContent>
      </Card>

      {/* ── Résultat ──────────���──────────────────────── */}
      {mutation.data ? (
        <div className="animate-slide-up space-y-4">
          {/* Bande de résultat */}
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-accent/60 px-5 py-3">
            <div className="flex flex-wrap items-center gap-2">
              <Badge>
                {WORKFLOW_LABELS[mutation.data.selected_workflow] ?? mutation.data.selected_workflow}
              </Badge>
              <Badge variant="outline">
                {TYPE_LABELS[mutation.data.request_type] ?? mutation.data.request_type}
              </Badge>
              <span className="text-xs text-muted-foreground">
                Confiance {Math.round(mutation.data.confidence * 100)}%
              </span>
              {mutation.data.mode_used === "assisted" ? (
                <span className="flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-[10px] font-medium text-primary">
                  <BrainCircuit className="h-3 w-3" />
                  {mutation.data.llm_provider ?? "LLM"}
                </span>
              ) : null}
              {mutation.data.warnings?.length ? (
                <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-[10px] font-medium text-amber-700">
                  {mutation.data.warnings.length} avertissement{mutation.data.warnings.length > 1 ? "s" : ""}
                </span>
              ) : null}
            </div>
            <Link
              to={`/topics/${mutation.data.topic_id}`}
              className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-xs font-medium text-primary-foreground"
            >
              Ouvrir le sujet <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <ArtifactRenderer result={mutation.data.result} />

          {mutation.data.intermediate_analysis ? (
            <details className="group">
              <summary className="cursor-pointer rounded-xl bg-secondary px-4 py-2.5 text-xs text-muted-foreground hover:text-foreground">
                Voir l'analyse intermédiaire ayant guidé ce résultat
              </summary>
              <div className="mt-3">
                <ArtifactRenderer result={mutation.data.intermediate_analysis} />
              </div>
            </details>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
