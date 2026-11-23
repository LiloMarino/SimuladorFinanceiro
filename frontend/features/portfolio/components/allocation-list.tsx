import { InfoHint } from "@/shared/components/info-hint";
import type { AllocationRow } from "@/features/portfolio/lib/allocation-rows";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";

/** Colunas de no mínimo 160 px: a lista cresce com as linhas sem largura fixa. */
export function AllocationList({ rows }: { rows: AllocationRow[] }) {
  return (
    <ul className="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-3">
      {rows.map((row) => (
        <li key={row.label} className="grid gap-0.5">
          <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className={`size-2 rounded-sm ${row.color}`} aria-hidden="true" />
            {row.label}
            {row.exitRule && <InfoHint label={`Como sai o ${row.label}`}>{row.exitRule}</InfoHint>}
          </span>
          <span className="font-mono text-sm font-semibold">{displayMoney(row.value)}</span>
          <span className="font-mono text-xs text-muted-foreground">{displayPercent(row.pct)}</span>
        </li>
      ))}
    </ul>
  );
}
