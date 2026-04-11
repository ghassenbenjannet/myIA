import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { ArtifactRenderer } from "@/components/artifacts/artifact-renderer";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { shadowPoApi } from "@/lib/api/shadow-po-api";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function ReadsPage() {
  const rememberRun = useWorkspaceStore((state) => state.rememberRun);
  const [sourceRef, setSourceRef] = useState("");
  const [sourceHint, setSourceHint] = useState("");
  const [issueKey, setIssueKey] = useState("");
  const [pageId, setPageId] = useState("");

  const sourceMutation = useMutation({
    mutationFn: shadowPoApi.sourceSummary,
    onSuccess: (payload) =>
      rememberRun({
        runId: payload.run_id,
        topicId: payload.topic_id,
        workflow: "source_summary",
        label: payload.result.source_title ?? "Source summary",
      }),
  });

  const jiraMutation = useMutation({
    mutationFn: shadowPoApi.jiraRead,
    onSuccess: (payload) =>
      rememberRun({
        runId: payload.run_id,
        topicId: payload.topic_id,
        workflow: "jira_read",
        label: `${payload.result.issue_key} - ${payload.result.title}`,
      }),
  });

  const confluenceMutation = useMutation({
    mutationFn: shadowPoApi.confluenceRead,
    onSuccess: (payload) =>
      rememberRun({
        runId: payload.run_id,
        topicId: payload.topic_id,
        workflow: "confluence_read",
        label: payload.result.title,
      }),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Reads"
        title="Reads et enrichissements"
        description="Fondation des points d'entree read-first du produit : source summary, lecture Jira, lecture Confluence et transformation vers les artefacts suivants."
      />

      <div className="grid gap-5 xl:grid-cols-3">
        <Card>
          <CardContent className="space-y-4">
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Source</p>
            <h3 className="text-xl font-semibold">Source Summary</h3>
            <div className="grid gap-3">
              <Select defaultValue="url">
                <option value="url">url</option>
              </Select>
              <Input value={sourceRef} onChange={(event) => setSourceRef(event.target.value)} placeholder="https://example.com/article" />
              <Input value={sourceHint} onChange={(event) => setSourceHint(event.target.value)} placeholder="Context hint optionnel" />
              <Button
                onClick={() =>
                  sourceMutation.mutate({
                    source_type: "url",
                    source_ref: sourceRef,
                    context_hint: sourceHint || null,
                  })
                }
              >
                Executer /source-summary
              </Button>
            </div>
            {sourceMutation.data ? <ArtifactRenderer result={sourceMutation.data.result} /> : null}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4">
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Jira</p>
            <h3 className="text-xl font-semibold">Jira Read</h3>
            <div className="grid gap-3">
              <Input value={issueKey} onChange={(event) => setIssueKey(event.target.value)} placeholder="PO-123" />
              <Button onClick={() => jiraMutation.mutate({ issue_key: issueKey })}>Executer /jira-read</Button>
            </div>
            {jiraMutation.data ? <ArtifactRenderer result={jiraMutation.data.result} /> : null}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4">
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Confluence</p>
            <h3 className="text-xl font-semibold">Confluence Read</h3>
            <div className="grid gap-3">
              <Input value={pageId} onChange={(event) => setPageId(event.target.value)} placeholder="42" />
              <Button onClick={() => confluenceMutation.mutate({ page_id: pageId })}>Executer /confluence-read</Button>
            </div>
            {confluenceMutation.data ? <ArtifactRenderer result={confluenceMutation.data.result} /> : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
