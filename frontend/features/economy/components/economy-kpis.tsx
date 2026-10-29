import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { signedIpca, signedStocks } from "@/shared/lib/effects";
import { GROWTH, UNEMPLOYMENT } from "@/shared/lib/budget-metrics";
import { displayPercent } from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";
import {
  growthExample,
  ipcaExample,
  lastCopomNote,
  lastMonthChange,
  monthChangeNote,
  realRateTone,
  selicExample,
  stocksEffect,
  sumEffects,
  targetNote,
  unemploymentExample,
} from "../lib/economy";
import { IBOVESPA, IPCA, REAL_RATE, SELIC } from "../lib/economy-metrics";

type EconomyKpisProps = { panel: EconomyPanel };

type TileProps = {
  metric: typeof SELIC;
  value: string;
  note: string;
  description: string;
  tone?: "destructive" | "warning" | "default";
};

function Tile({ metric, value, note, description, tone = "default" }: TileProps) {
  return (
    <Card size="sm">
      <CardContent>
        <div className="grid gap-2">
          <Kpi
            label={
              <>
                {metric.label}
                <MetricHint metric={metric} />
              </>
            }
            value={value}
            note={note}
            tone={tone}
          />
          <p className="border-t pt-2 text-xs leading-snug text-muted-foreground">{description}</p>
        </div>
      </CardContent>
    </Card>
  );
}

/** "+1,35 pelas medidas": o que as medidas de gasto somam ao número, em pontos ou em %. */
const measuresNote = (shift: string) => `${shift} pelas medidas`;

/** " Na história, 3,75% hoje.": o número da série guardada, sem as medidas; vazio sem a expansão Governo. */
const historyNote = (stored: string | null, format: (value: string) => string) =>
  stored === null ? "" : ` Na história, ${format(stored)} hoje.`;

/** Os números de hoje: SELIC, crescimento, Ibovespa (só com a expansão Governo), inflação, juro real e desemprego. */
export function EconomyKpis({ panel }: EconomyKpisProps) {
  const today = panel.points.at(-1);
  if (!today) return null;
  const { effects, growth_parts: parts } = panel;
  const measured = effects !== null && effects.length > 0;
  const selicShift = effects ? sumEffects(effects, "selic") : 0;
  const ipcaShift = effects ? sumEffects(effects, "inflation") : 0;
  const stocksShift = stocksEffect(today);

  return (
    <div className={cn("grid gap-3 sm:grid-cols-3", effects ? "xl:grid-cols-6" : "xl:grid-cols-5")}>
      {/* SELIC */}
      <Tile
        metric={SELIC}
        value={SELIC.format(today.selic)}
        note={measured ? measuresNote(signedIpca(selicShift)) : lastCopomNote(panel.copom_changes)}
        description={`${selicExample(today)}${historyNote(today.stored_selic, (value) => displayPercent(value, 2))}`}
      />

      {/* Crescimento do PIB */}
      <Tile
        metric={GROWTH}
        value={GROWTH.format(today.growth)}
        note={monthChangeNote(lastMonthChange(panel.points, "growth"))}
        description={growthExample(parts.trend)}
        tone={Number(today.growth) < 0 ? "destructive" : "default"}
      />

      {/* Ibovespa */}
      {effects && today.ibovespa !== null && (
        <Tile
          metric={IBOVESPA}
          value={IBOVESPA.format(today.ibovespa)}
          note={
            stocksShift !== null && Math.abs(stocksShift) >= 0.0005
              ? measuresNote(signedStocks(stocksShift))
              : "sem efeito das medidas"
          }
          description={`${IBOVESPA.description}${historyNote(today.stored_ibovespa, IBOVESPA.format)}`}
        />
      )}

      {/* IPCA */}
      <Tile
        metric={IPCA}
        value={IPCA.format(today.ipca)}
        note={measured ? measuresNote(signedIpca(ipcaShift)) : targetNote(today)}
        description={`${ipcaExample(today)}${historyNote(today.stored_ipca, (value) => displayPercent(value, 2))}`}
      />

      {/* Juro real */}
      <Tile
        metric={REAL_RATE}
        value={REAL_RATE.format(today.real_rate)}
        note="SELIC − IPCA"
        description={`${REAL_RATE.description}.`}
        tone={realRateTone(today)}
      />

      {/* Desemprego */}
      <Tile
        metric={UNEMPLOYMENT}
        value={UNEMPLOYMENT.format(today.unemployment)}
        note={monthChangeNote(lastMonthChange(panel.points, "unemployment"))}
        description={unemploymentExample(today)}
      />
    </div>
  );
}
