import { useMutation } from "@tanstack/react-query";
import { ArrowRight, BookOpen, ExternalLink, Loader2 } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { useWorkspaceStore } from "@/stores/workspace-store";

// ── Generic read card ─────────────────────────────────────────────────────────

function ReadCard({
  label,
  icon: Icon,
  title,
  description,
  children,
  result,
  topicId,
  isPending,
  isError,
}: {
  label: string;
  icon: React.ElementType;
  title: string;
  description: string;
  children: React.ReactNode;
  result?: React.ReactNode;
  topicId?: string;
  isPending: boolean;
  isError: boolean;
}) {
  return (
    <div className="flex flex-col gap-4">
      <Card className="shadow-card">
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-accent">
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                {label}
              </p>
              <h3 className="text-base font-semibold">{title}</h3>
            </div>
          </div>
          <p className="text-xs leading-5 text-muted-foreground">{description}</p>
          <div className="space-y-3">{children}</div>
          {isError ? (
            <p className="rounded-xl bg-red-50 px-3 py-2 text-xs text-red-700">
              Erreur — vérifiez la configuration ou la disponibilité du service.
            </p>
          ) : null}
          {topicId ? (
            <Link
              to={`/topics/${topicId}`}
              className="inline-flex items-center gap-1.5 text-xs font-medium text-primary hover:underline"
            >
              Ouvrir le sujet créé <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          ) : null}
        </CardContent>
      </Card>
      {result}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export function ReadsPage() {
  const rememberRun = useWorkspaceStore((s) => s.rememberRun);

  const [sourceRef, setSourceRef] = useState("");
  const [sourceHint, setSourceHint] = useState("");
  const [issueKey, setIssueKey] = useState("");
  const [pageId, setPageId] = useState("");

  const sourceMutation = useMutation({
    mutationFn: shadowPoApi.sourceSummary,
    onSuccess: (p) =>
      rememberRun({
        runId: p.run_id,
        topicId: p.topic_id,
        workflow: "source_summary",
        label: p.result.source_title ?? p.result.source_ref,
      }),
  });

  const jiraMutation = useMutation({
    mutationFn: shadowPoApi.jiraRead,
    onSuccess: (p) =>
      rememberRun({
        runId: p.run_id,
        topicId: p.topic_id,
        workflow: "jira_read",
        label: `${p.result.issue_key} — ${p.result.title}`,
      }),
  });

  const confluenceMutation = useMutation({
    mutationFn: shadowPoApi.confluenceRead,
    onSuccess: (p) =>
      rememberRun({
        runId: p.run_id,
        topicId: p.topic_id,
        workflow: "confluence_read",
        label: p.result.title,
      }),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Lectures"
        title="Lire une source externe"
        description="Résumez une URL, lisez un ticket Jira ou explorez une page Confluence. Chaque lecture crée un sujet et des continuations sont proposées."
      />

      <div className="grid gap-6 xl:grid-cols-3">
        {/* ── Source URL ── */}
        <ReadCard
          label="Web"
          icon={ExternalLink}
          title="Source URL"
          description="Collez une URL et obtenez un résumé structuré avec points clés et questions ouvertes."
          isPending={sourceMutation.isPending}
          isError={sourceMutation.isError}
          topicId={sourceMutation.data?.topic_id}
          result={
            sourceMutation.data ? (
              <ArtifactRenderer result={sourceMutation.data.result} />
            ) : undefined
          }
        >
          <Input
            value={sourceRef}
            onChange={(e) => setSourceRef(e.target.value)}
            placeholder="https://example.com/article"
          />
          <Input
            value={sourceHint}
            onChange={(e) => setSourceHint(e.target.value)}
            placeholder="Contexte optionnel"
          />
          <Button
            onClick={() =>
              sourceMutation.mutate({
                source_type: "url",
                source_ref: sourceRef,
                context_hint: sourceHint || null,
              })
            }
            disabled={!sourceRef.trim() || sourceMutation.isPending}
            className="w-full gap-2"
          >
            {sourceMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : null}
            Lire la source
          </Button>
        </ReadCard>

        {/* ── Jira ── */}
        <ReadCard
          label="Jira"
          icon={BookOpen}
          title="Ticket Jira"
          description="Entrez une clé de ticket Jira pour obtenir une synthèse et les points ouverts identifiés."
          isPending={jiraMutation.isPending}
          isError={jiraMutation.isError}
          topicId={jiraMutation.data?.topic_id}
          result={
            jiraMutation.data ? (
              <ArtifactRenderer result={jiraMutation.data.result} />
            ) : undefined
          }
        >
          <Input
            value={issueKey}
            onChange={(e) => setIssueKey(e.target.value)}
            placeholder="PO-123"
          />
          <Button
            onClick={() => jiraMutation.mutate({ issue_key: issueKey })}
            disabled={!issueKey.trim() || jiraMutation.isPending}
            className="w-full gap-2"
          >
            {jiraMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : null}
            Lire le ticket
          </Button>
        </ReadCard>

        {/* ── Confluence ── */}
        <ReadCard
          label="Confluence"
          icon={BookOpen}
          title="Page Confluence"
          description="Entrez l'identifiant d'une page Confluence pour en extraire le résumé et les points structurants."
          isPending={confluenceMutation.isPending}
          isError={confluenceMutation.isError}
          topicId={confluenceMutation.data?.topic_id}
          result={
            confluenceMutation.data ? (
              <ArtifactRenderer result={confluenceMutation.data.result} />
            ) : undefined
          }
        >
          <Input
            value={pageId}
            onChange={(e) => setPageId(e.target.value)}
            placeholder="42 ou /spaces/SPACE/pages/42"
          />
          <Button
            onClick={() => confluenceMutation.mutate({ page_id: pageId })}
            disabled={!pageId.trim() || confluenceMutation.isPending}
            className="w-full gap-2"
          >
            {confluenceMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : null}
            Lire la page
          </Button>
        </ReadCard>
      </div>
    </div>
  );
}
