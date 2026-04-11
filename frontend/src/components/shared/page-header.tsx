export function PageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="mb-6 flex items-start justify-between gap-6 max-[900px]:flex-col">
      <div>
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-primary">{eyebrow}</p>
        <h1 className="font-display text-4xl leading-none">{title}</h1>
      </div>
      <p className="max-w-2xl text-sm leading-7 text-muted-foreground">{description}</p>
    </div>
  );
}
