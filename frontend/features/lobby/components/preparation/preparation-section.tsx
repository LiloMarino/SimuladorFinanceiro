import type { ReactNode } from "react";

type PreparationSectionProps = { title: string; hint?: string; children: ReactNode };

/** Bloco da preparação: título, onde a escolha fica guardada e os campos. */
export function PreparationSection({ title, hint, children }: PreparationSectionProps) {
  return (
    <section className="grid min-w-0 gap-2.5">
      <div className="flex items-baseline justify-between gap-2">
        <b className="text-sm font-semibold">{title}</b>
        {hint && <span className="text-xs text-muted-foreground">{hint}</span>}
      </div>
      {children}
    </section>
  );
}
