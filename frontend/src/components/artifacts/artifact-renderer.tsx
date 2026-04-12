import type { ReactNode } from "react";

import { ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { truncate } from "@/lib/utils";
import type {
  AnalysisResult,
  ArtifactResult,
  ConfluencePageResult,
  DocumentationResult,
  JiraIssueResult,
  SourceSummaryResult,
  TicketResult,
} from "@/types/api";

// ── Shared primitives ─────────────────────────────────────────────────────────

function Label({ children }: { children: ReactNode }) {
  return (
    <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-primary">
      {children}
    </p>
  );
}

function Divider() {
  return <div className="border-t border-border/50" />;
}

function ListBlock({
  title,
  items,
  variant = "default",
}: {
  title: string;
  items?: string[];
  variant?: "default" | "warning" | "success";
}) {
  if (!items?.length) return null;
  const cls = {
    default: "rounded-xl bg-secondary px-3.5 py-2.5 text-sm text-muted-foreground",
    warning: "rounded-xl bg-amber-50 border border-amber-200/70 px-3.5 py-2.5 text-sm text-amber-900",
    success: "rounded-xl bg-emerald-50 border border-emerald-200/70 px-3.5 py-2.5 text-sm text-emerald-900",
  }[variant];
  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {title}
      </h4>
      <ul className="space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className={cls}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function InfoBlock({ label, content }: { label: string; content: string }) {
  return (
    <div className="rounded-xl bg-secondary px-3.5 py-3">
      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-1.5 text-sm leading-6">{content}</p>
    </div>
  );
}

// ── Analysis ──────────────────────────────────────────────────────────────────

function AnalysisCard({ r }: { r: AnalysisResult }) {
  const hasBehaviors = r.current_behavior || r.expected_behavior;
  const hasImpacts = r.business_impacts?.length || r.technical_impacts?.length || r.dependencies?.length;
  const hasIssues = r.ambiguities?.length || r.risks?.length || r.open_questions?.length;
  const hasReco = r.recommended_next_step || r.recommended_output;

  return (
    <Card className="shadow-card">
      <CardContent className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Label>Analyse</Label>
          {r.detected_type ? (
            <Badge variant="outline" className="text-[10px]">
              {r.detected_type}
            </Badge>
          ) : null}
        </div>

        <div>
          <h3 className="text-xl font-semibold leading-snug">{r.reformulation}</h3>
          {r.request_summary ? (
            <p className="mt-2 text-sm leading-7 text-muted-foreground">{r.request_summary}</p>
          ) : null}
        </div>

        {hasBehaviors ? (
          <>
            <Divider />
            <div className="grid gap-3 md:grid-cols-2">
              {r.current_behavior ? (
                <InfoBlock label="Comportement actuel" content={r.current_behavior} />
              ) : null}
              {r.expected_behavior ? (
                <InfoBlock label="Comportement attendu" content={r.expected_behavior} />
              ) : null}
            </div>
          </>
        ) : null}

        {hasImpacts ? (
          <>
            <Divider />
            <div className="space-y-4">
              <ListBlock title="Impacts métier" items={r.business_impacts} />
              <ListBlock title="Impacts techniques" items={r.technical_impacts} />
              <ListBlock title="Dépendances" items={r.dependencies} />
            </div>
          </>
        ) : null}

        {hasIssues ? (
          <>
            <Divider />
            <div className="space-y-4">
              <ListBlock title="Ambiguïtés" items={r.ambiguities} variant="warning" />
              <ListBlock title="Risques" items={r.risks} variant="warning" />
              <ListBlock title="Questions ouvertes" items={r.open_questions} />
            </div>
          </>
        ) : null}

        {hasReco ? (
          <>
            <Divider />
            <div className="rounded-xl bg-accent/60 px-4 py-3 space-y-2">
              {r.recommended_next_step ? (
                <p className="text-sm leading-6">
                  <span className="font-medium">Prochaine étape : </span>
                  {r.recommended_next_step}
                </p>
              ) : null}
              {r.recommended_output ? (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">Sortie recommandée</span>
                  <Badge className="text-[10px]">{r.recommended_output}</Badge>
                </div>
              ) : null}
            </div>
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

// ── Ticket ────────────────────────────────────────────────────────────────────

const TICKET_LABELS: Record<string, string> = {
  bug: "Bug",
  story: "Story",
  test: "Recette",
  task: "Tâche",
};

function TicketCard({ r }: { r: TicketResult }) {
  const typeLabel = TICKET_LABELS[r.ticket_type] ?? r.ticket_type.toUpperCase();
  const hasBehaviors = r.current_behavior || r.expected_behavior;
  const hasImpacts = r.business_impacts?.length || r.technical_impacts?.length || r.dependencies?.length;

  return (
    <Card className="shadow-card">
      <CardContent className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Label>Ticket</Label>
          <Badge variant="outline" className="text-[10px]">{typeLabel}</Badge>
        </div>

        <div>
          <h3 className="text-xl font-semibold leading-snug">{r.title}</h3>
          {r.business_goal ? (
            <p className="mt-1.5 text-sm font-medium text-foreground/80">{r.business_goal}</p>
          ) : null}
          {r.description ? (
            <p className="mt-2 text-sm leading-7 text-muted-foreground">{r.description}</p>
          ) : null}
        </div>

        {hasBehaviors ? (
          <>
            <Divider />
            <div className="grid gap-3 md:grid-cols-2">
              {r.current_behavior ? (
                <InfoBlock label="Comportement actuel" content={r.current_behavior} />
              ) : null}
              {r.expected_behavior ? (
                <InfoBlock label="Comportement attendu" content={r.expected_behavior} />
              ) : null}
            </div>
          </>
        ) : null}

        {hasImpacts ? (
          <>
            <Divider />
            <div className="space-y-4">
              <ListBlock title="Impacts métier" items={r.business_impacts} />
              <ListBlock title="Impacts techniques" items={r.technical_impacts} />
              <ListBlock title="Dépendances" items={r.dependencies} />
            </div>
          </>
        ) : null}

        {r.acceptance_criteria?.length ? (
          <>
            <Divider />
            <ListBlock title="Critères d'acceptation" items={r.acceptance_criteria} variant="success" />
          </>
        ) : null}

        {r.open_points?.length ? (
          <>
            <Divider />
            <ListBlock title="Points ouverts" items={r.open_points} variant="warning" />
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

// ── Documentation ─────────────────────────────────────────────────────────────

function DocumentationCard({ r }: { r: DocumentationResult }) {
  return (
    <Card className="shadow-card">
      <CardContent className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Label>Documentation</Label>
          {r.document_type ? (
            <Badge variant="outline" className="text-[10px]">{r.document_type}</Badge>
          ) : null}
        </div>

        <div>
          <h3 className="text-xl font-semibold leading-snug">{r.title}</h3>
          {r.summary ? (
            <p className="mt-2 text-sm leading-7 text-muted-foreground">{r.summary}</p>
          ) : null}
        </div>

        {r.sections?.length ? (
          <>
            <Divider />
            <div className="grid gap-3">
              {r.sections.map((section) => (
                <div key={section.title} className="rounded-xl bg-secondary px-4 py-3">
                  <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    {section.title}
                  </h4>
                  <div className="mt-2 text-sm leading-7 text-foreground">
                    {Array.isArray(section.content) ? (
                      <ul className="space-y-1">
                        {section.content.map((item, i) => (
                          <li key={i} className="text-muted-foreground">{item}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground">{section.content}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

// ── Source summary ─────────────────────────────────────────────────────────────

function SourceSummaryCard({ r }: { r: SourceSummaryResult }) {
  return (
    <Card className="shadow-card">
      <CardContent className="space-y-5">
        <Label>Source summary</Label>
        <div>
          <h3 className="text-xl font-semibold leading-snug">
            {r.source_title ?? truncate(r.source_ref, 60)}
          </h3>
          {r.source_ref && r.source_title ? (
            <p className="mt-1 text-xs text-muted-foreground">{truncate(r.source_ref, 80)}</p>
          ) : null}
          <p className="mt-2 text-sm leading-7 text-muted-foreground">{r.summary}</p>
        </div>
        <ListBlock title="Points clés" items={r.key_points} />
        <ListBlock title="Questions ouvertes" items={r.open_questions} variant="warning" />
        {r.next_step_hint ? (
          <>
            <Divider />
            <div className="rounded-xl bg-accent/60 px-4 py-3">
              <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Prochaine étape
              </span>
              <p className="mt-1 text-sm">{r.next_step_hint}</p>
            </div>
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

// ── Jira ──────────────────────────────────────────────────────────────────────

function JiraCard({ r }: { r: JiraIssueResult }) {
  return (
    <Card className="shadow-card">
      <CardContent className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Label>Jira read</Label>
          {r.status ? <Badge variant="outline" className="text-[10px]">{r.status}</Badge> : null}
          {r.issue_type ? <Badge variant="outline" className="text-[10px]">{r.issue_type}</Badge> : null}
          {r.priority ? <Badge variant="outline" className="text-[10px]">{r.priority}</Badge> : null}
        </div>
        <div>
          <h3 className="text-xl font-semibold leading-snug">
            <span className="text-muted-foreground">{r.issue_key} </span>
            {r.title}
          </h3>
          {r.url ? (
            <a
              href={r.url}
              target="_blank"
              rel="noreferrer"
              className="mt-1 inline-flex items-center gap-1 text-xs text-primary hover:underline"
            >
              Ouvrir dans Jira <ExternalLink className="h-3 w-3" />
            </a>
          ) : null}
          <p className="mt-2 text-sm leading-7 text-muted-foreground">{truncate(r.summary, 300)}</p>
        </div>
        {r.labels?.length ? (
          <div className="flex flex-wrap gap-1.5">
            {r.labels.map((l) => (
              <Badge key={l} variant="outline" className="text-[10px]">{l}</Badge>
            ))}
          </div>
        ) : null}
        <ListBlock title="Points ouverts" items={r.open_points} variant="warning" />
      </CardContent>
    </Card>
  );
}

// ── Confluence ────────────────────────────────────────────────────────────────

function ConfluenceCard({ r }: { r: ConfluencePageResult }) {
  return (
    <Card className="shadow-card">
      <CardContent className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <Label>Confluence read</Label>
          {r.space_key ? <Badge variant="outline" className="text-[10px]">{r.space_key}</Badge> : null}
        </div>
        <div>
          <h3 className="text-xl font-semibold leading-snug">{r.title}</h3>
          {r.url ? (
            <a
              href={r.url}
              target="_blank"
              rel="noreferrer"
              className="mt-1 inline-flex items-center gap-1 text-xs text-primary hover:underline"
            >
              Ouvrir dans Confluence <ExternalLink className="h-3 w-3" />
            </a>
          ) : null}
          <p className="mt-2 text-sm leading-7 text-muted-foreground">{r.summary}</p>
        </div>
        <ListBlock title="Points clés" items={r.key_points} />
        <ListBlock title="Points ouverts" items={r.open_points} variant="warning" />
        {r.content_preview ? (
          <>
            <Divider />
            <details>
              <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                Aperçu du contenu
              </summary>
              <p className="mt-2 text-xs leading-6 text-muted-foreground">{r.content_preview}</p>
            </details>
          </>
        ) : null}
      </CardContent>
    </Card>
  );
}

// ── Dispatcher (via result_type discriminant) ─────────────────────────────────

export function ArtifactRenderer({ result }: { result: ArtifactResult }) {
  switch (result.result_type) {
    case "analysis":
      return <AnalysisCard r={result} />;
    case "ticket":
      return <TicketCard r={result} />;
    case "documentation":
      return <DocumentationCard r={result} />;
    case "source_summary":
      return <SourceSummaryCard r={result} />;
    case "jira_read":
      return <JiraCard r={result} />;
    case "confluence_read":
      return <ConfluenceCard r={result} />;
  }
}
