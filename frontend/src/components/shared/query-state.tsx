import { AlertCircle, Inbox, Loader2 } from "lucide-react";

export function QueryLoading({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3 py-12 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin text-primary" />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function QueryError({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
      <AlertCircle className="h-4 w-4 shrink-0" />
      <span>{label}</span>
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-secondary/40 px-8 py-16 text-center">
      <Inbox className="mb-4 h-8 w-8 text-muted-foreground/40" />
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-2 max-w-sm text-sm leading-6 text-muted-foreground">{description}</p>
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}
