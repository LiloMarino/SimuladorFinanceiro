import { ArrowRight } from "lucide-react";
import { Kpi } from "@/shared/components/kpi";
import { MetricLabel } from "@/shared/components/metric-hint";
import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import type { YearReview } from "@/types";
import { YEAR_CDI, YEAR_IBOV } from "../../lib/summary-metrics";

type NetworthChangeProps = {
  start: YearReview["networth_start"];
  end: YearReview["networth_end"];
};

/** Patrimônio no início e no fim do período. */
export function NetworthChange({ start, end }: NetworthChangeProps) {
  return (
    <div className="grid gap-1">
      <span className="text-xs font-medium text-muted-foreground">Patrimônio</span>
      <span className="flex flex-wrap items-center gap-2 font-mono text-[15px] font-semibold tabular-nums">
        {displayMoney(start)}
        <ArrowRight className="size-3.5 text-muted-foreground" />
        {displayMoney(end)}
      </span>
    </div>
  );
}

type ReturnComparisonProps = {
  metric: MetricInfo;
  value: YearReview["return_pct"];
  cdi: YearReview["cdi_pct"];
  ibov: YearReview["ibov_pct"];
};

/** A rentabilidade do jogador ao lado do CDI e do Ibovespa do mesmo período. */
export function ReturnComparison({ metric, value, cdi, ibov }: ReturnComparisonProps) {
  const tone = value === null || Number(value) === 0 ? "default" : Number(value) > 0 ? "success" : "destructive";
  return (
    <div className="grid grid-cols-3 gap-3">
      <Kpi
        label={<MetricLabel metric={metric} />}
        value={value === null ? "—" : displaySignedPercent(value)}
        note={value === null ? "Sem pregão para medir" : undefined}
        tone={tone}
      />
      <Kpi label={<MetricLabel metric={YEAR_CDI} />} value={displaySignedPercent(cdi)} />
      <Kpi
        label={<MetricLabel metric={YEAR_IBOV} />}
        value={ibov === null ? "—" : displaySignedPercent(ibov)}
        note={ibov === null ? "Sem a série do índice" : undefined}
      />
    </div>
  );
}
