import { Card, CardContent } from "@/components/ui/card";
import { truncate } from "@/lib/utils";
import type {
  AnalysisResult,
  ConfluencePageResult,
  DocumentationResult,
  JiraIssueResult,
  SourceSummaryResult,
  TicketResult,
} from "@/types/api";

function ListBlock({ title, items }: { title: string; items?: string[] }) {
  if (!items?.length) {
    return null;
  }
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold">{title}</h4>
      <ul className="space-y-2 text-sm text-muted-foreground">
        {items.map((item) => (
          <li key={item} className="rounded-2xl bg-secondary px-4 py-3">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ArtifactRenderer({
  result,
}: {
  result:
    | AnalysisResult
    | TicketResult
    | DocumentationResult
    | SourceSummaryResult
    | JiraIssueResult
    | ConfluencePageResult;
}) {
  if ("reformulation" in result && "recommended_output" in result) {
    return (
      <Card>
        <CardContent className="space-y-5">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Analyse</p>
            <h3 className="mt-2 text-2xl font-semibold">{result.reformulation}</h3>
            <p className="mt-3 text-sm leading-7 text-muted-foreground">{result.request_summary}</p>
          </div>
          <ListBlock title="Questions ouvertes" items={result.open_questions} />
          <ListBlock title="Risques" items={result.risks} />
        </CardContent>
      </Card>
    );
  }

  if ("ticket_type" in result && "acceptance_criteria" in result) {
    return (
      <Card>
        <CardContent className="space-y-5">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Ticket</p>
            <h3 className="mt-2 text-2xl font-semibold">{result.title}</h3>
            <p className="mt-3 text-sm leading-7 text-muted-foreground">{result.description}</p>
          </div>
          <ListBlock title="Acceptance criteria" items={result.acceptance_criteria} />
          <ListBlock title="Open points" items={result.open_points} />
        </CardContent>
      </Card>
    );
  }

  if ("sections" in result) {
    return (
      <Card>
        <CardContent className="space-y-5">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-primary">Documentation</p>
            <h3 className="mt-2 text-2xl font-semibold">{result.title}</h3>
          </div>
          <div className="grid gap-4">
            {result.sections.map((section) => (
              <div key={section.title} className="rounded-2xl bg-secondary p-4">
                <h4 className="font-semibold">{section.title}</h4>
                <div className="mt-2 text-sm leading-7 text-muted-foreground">
                  {Array.isArray(section.content) ? section.content.join(" ") : section.content}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if ("source_type" in result) {
    return (
      <Card>
        <CardContent className="space-y-4">
          <p className="text-xs uppercase tracking-[0.16em] text-primary">Source summary</p>
          <h3 className="text-2xl font-semibold">{result.source_title ?? result.source_ref}</h3>
          <p className="text-sm leading-7 text-muted-foreground">{result.summary}</p>
          <ListBlock title="Key points" items={result.key_points} />
        </CardContent>
      </Card>
    );
  }

  if ("issue_key" in result) {
    return (
      <Card>
        <CardContent className="space-y-4">
          <p className="text-xs uppercase tracking-[0.16em] text-primary">Jira read</p>
          <h3 className="text-2xl font-semibold">
            {result.issue_key} - {result.title}
          </h3>
          <p className="text-sm leading-7 text-muted-foreground">{truncate(result.summary, 220)}</p>
          <ListBlock title="Open points" items={result.open_points} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="space-y-4">
        <p className="text-xs uppercase tracking-[0.16em] text-primary">Confluence read</p>
        <h3 className="text-2xl font-semibold">{result.title}</h3>
        <p className="text-sm leading-7 text-muted-foreground">{result.summary}</p>
        <ListBlock title="Key points" items={result.key_points} />
      </CardContent>
    </Card>
  );
}
