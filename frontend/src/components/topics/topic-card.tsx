import { ArrowRight, Clock, GitCommit } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import type { TopicSummary } from "@/types/api";

const STATUS_STYLES: Record<string, string> = {
  active: "bg-emerald-100 text-emerald-700 border-emerald-200",
  closed: "bg-gray-100 text-gray-600 border-gray-200",
};

export function TopicCard({ topic }: { topic: TopicSummary }) {
  return (
    <Link to={`/topics/${topic.topic_id}`} className="group block h-full">
      <Card className="h-full shadow-card transition-shadow duration-200 group-hover:shadow-card-hover">
        <CardContent className="flex h-full flex-col gap-4">
          <div className="flex items-start justify-between gap-3">
            <h3 className="flex-1 text-base font-semibold leading-snug line-clamp-2">
              {topic.topic_label}
            </h3>
            <span
              className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-medium ${
                STATUS_STYLES[topic.status] ?? STATUS_STYLES.active
              }`}
            >
              {topic.status}
            </span>
          </div>

          <div className="flex flex-1 items-end justify-between gap-3">
            <div className="space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span>{formatDate(topic.updated_at)}</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <GitCommit className="h-3 w-3" />
                <span>
                  {topic.run_count} run{topic.run_count > 1 ? "s" : ""}
                </span>
              </div>
            </div>

            <span className="flex items-center gap-1 text-xs font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100">
              Ouvrir <ArrowRight className="h-3.5 w-3.5" />
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
