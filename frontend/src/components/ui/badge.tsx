import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: ReactNode;
  variant?: "default" | "outline";
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
        variant === "outline"
          ? "border border-border bg-background text-foreground"
          : "bg-accent text-accent-foreground",
        className
      )}
    >
      {children}
    </span>
  );
}
