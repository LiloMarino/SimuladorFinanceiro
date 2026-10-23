import { Kpi } from "@/shared/components/kpi";
import { MetricHint, MetricLabel } from "@/shared/components/metric-hint";
import type { StrategyPanel as Panel } from "@/types";
import { IBOVESPA_SAME_PERIOD, STRATEGY_RETURN } from "../lib/metrics";
import { lastOrderTitle, lastOrderWhen, ordersBreakdown } from "../lib/strategy-display";

type StrategyPanelProps = {
  panel: Panel;
  currentDate: string | undefined;
};

const tone = (value: string | number) =>
  Number(value) > 0 ? "success" : Number(value) < 0 ? "destructive" : "default";

/** O que a estratégia fez desde que o jogador a ligou: ordens, patrimônio contra o Ibovespa e a última ordem. */
export function StrategyPanel({ panel, currentDate }: StrategyPanelProps) {
  return (
    <div className="grid gap-5 sm:grid-cols-3">
      <Kpi label="Ordens desde que ligou" value={panel.orders_total} note={ordersBreakdown(panel)} />

      <Kpi
        label={<MetricLabel metric={STRATEGY_RETURN} />}
        value={panel.return_pct === null ? "—" : STRATEGY_RETURN.format(panel.return_pct)}
        tone={panel.return_pct === null ? "default" : tone(panel.return_pct)}
        note={
          <span className="inline-flex items-center gap-1">
            Ibovespa no mesmo período:
            <MetricHint metric={IBOVESPA_SAME_PERIOD} />
            <b
              className={`font-mono ${panel.ibov_pct !== null && Number(panel.ibov_pct) < 0 ? "text-destructive" : "text-foreground"}`}
            >
              {panel.ibov_pct === null ? "—" : IBOVESPA_SAME_PERIOD.format(panel.ibov_pct)}
            </b>
          </span>
        }
      />

      <div className="grid content-start gap-1">
        <span className="text-xs font-medium text-muted-foreground">Última ordem</span>
        {panel.last_order ? (
          <>
            <span className="pt-1 text-base font-semibold">{lastOrderTitle(panel.last_order)}</span>
            <span className="text-xs text-muted-foreground">{lastOrderWhen(panel.last_order, currentDate)}</span>
          </>
        ) : (
          <span className="pt-1 text-sm text-muted-foreground">Nenhuma ordem ainda</span>
        )}
      </div>
    </div>
  );
}
