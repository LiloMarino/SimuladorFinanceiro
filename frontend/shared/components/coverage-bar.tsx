import { displayIsoDate, displayMonthSlashYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { BacktestCoverage } from "@/types";

type CoverageBarProps = {
  coverage: BacktestCoverage;
  /** O período escolhido, destacado sobre a barra */
  window: { start: string; end: string } | null;
};

/** Até onde o mercado é real (azul claro) e gerado (listrado), com o período escolhido por cima. */
export function CoverageBar({ coverage, window }: CoverageBarProps) {
  const { first_date: first, real_end: realEnd, generated_end: generatedEnd } = coverage;
  if (!first || !realEnd || !generatedEnd) return null;

  const from = parseLocalDate(first).getTime();
  const span = parseLocalDate(generatedEnd).getTime() - from;
  const at = (iso: string) => Math.min(Math.max(((parseLocalDate(iso).getTime() - from) / span) * 100, 0), 100);

  const realWidth = at(realEnd);
  const windowStart = window ? at(window.start) : 0;
  const windowEnd = window ? at(window.end) : 0;

  return (
    <div className="grid gap-1.5">
      {/* Barra de cobertura */}
      <div className="relative h-7 overflow-hidden rounded-md bg-muted" role="img" aria-label="Cobertura do mercado">
        <span className="absolute inset-y-0 left-0 bg-info-border" style={{ width: `${realWidth}%` }} />
        <span className="absolute inset-y-0 bg-generated" style={{ left: `${realWidth}%`, width: `${100 - realWidth}%` }} />
        {window && windowEnd > windowStart && (
          <span
            className="absolute inset-y-[3px] rounded-[5px] border-2 border-primary bg-primary/10"
            style={{ left: `${windowStart}%`, width: `${windowEnd - windowStart}%` }}
          />
        )}
      </div>

      {/* Marcas de tempo */}
      <div className="flex justify-between font-mono text-[11px] text-faint-foreground">
        <span>{parseLocalDate(first).getFullYear()}</span>
        <span>real até {displayIsoDate(realEnd)}</span>
        <span>gerado até {displayMonthSlashYear(generatedEnd)}</span>
      </div>
    </div>
  );
}
