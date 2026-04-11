import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import type { TopicSummary } from "@/types/api";

export function TopicCard({ topic }: { topic: TopicSummary }) {
  return (
    <Card className="h-full bg-white/90">
      <CardContent className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.14em] text-muted-foreground">Topic recent</p>
            <h3 className="mt-2 text-xl font-semibold">{topic.topic_label}</h3>
          </div>
          <Badge>{topic.status}</Badge>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm text-muted-foreground">
          <div className="rounded-2xl bg-secondary p-3">
            <p className="text-xs uppercase tracking-wide">Updated</p>
            <strong className="mt-2 block text-foreground">{formatDate(topic.updated_at)}</strong>
          </div>
          <div className="rounded-2xl bg-secondary p-3">
            <p className="text-xs uppercase tracking-wide">Runs</p>
            <strong className="mt-2 block text-foreground">{topic.run_count}</strong>
          </div>
        </div>

        <Link
          className="inline-flex items-center gap-2 rounded-2xl bg-primary px-4 py-3 text-sm text-primary-foreground"
          to={`/topics/${topic.topic_id}`}
        >
          Ouvrir le dossier
          <ArrowRight className="h-4 w-4" />
        </Link>
      </CardContent>
    </Card>
  );
}
