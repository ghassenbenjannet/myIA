import { Loader2 } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

export function QueryLoading({ label }: { label: string }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 py-8 text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>{label}</span>
      </CardContent>
    </Card>
  );
}

export function QueryError({ label }: { label: string }) {
  return (
    <Card className="border-red-200 bg-red-50/80">
      <CardContent className="py-8 text-sm text-red-700">{label}</CardContent>
    </Card>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <Card>
      <CardContent className="py-10">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="mt-2 max-w-xl text-sm leading-7 text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
