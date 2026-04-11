import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate, truncate } from "@/lib/utils";
import type { TopicRunView } from "@/types/api";

export function TopicTimeline({ runs }: { runs: TopicRunView[] }) {
  return (
    <div className="relative pl-6">
      <div className="absolute bottom-2 left-2 top-2 w-px bg-gradient-to-b from-primary/40 to-primary/10" />
      <div className="grid gap-4">
        {runs.map((run) => (
          <Card key={run.run_id} className="relative overflow-visible">
            <span className="absolute -left-[22px] top-8 h-3 w-3 rounded-full bg-primary shadow-[0_0_0_6px_rgba(15,118,110,0.12)]" />
            <CardContent className="space-y-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">{run.final_workflow}</p>
                  <h4 className="mt-2 text-lg font-semibold">{truncate(run.raw_input, 96)}</h4>
                </div>
                <Badge>{formatDate(run.created_at)}</Badge>
              </div>

              <div className="flex flex-wrap gap-2">
                {run.available_actions.map((action) => (
                  <Badge key={action} className="bg-accent text-accent-foreground">
                    {action}
                  </Badge>
                ))}
              </div>

              <div className="flex flex-wrap gap-3">
                <Link className="rounded-2xl bg-secondary px-4 py-2 text-sm" to={`/artifacts/${run.run_id}`}>
                  Ouvrir l'artefact
                </Link>
                {run.topic_id ? (
                  <Link className="rounded-2xl bg-secondary px-4 py-2 text-sm" to={`/topics/${run.topic_id}`}>
                    Retour au topic
                  </Link>
                ) : null}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
