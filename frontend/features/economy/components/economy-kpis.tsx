import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { signedIpca, signedStocks } from "@/shared/lib/effects";
import { GROWTH, UNEMPLOYMENT } from "@/shared/lib/budget-metrics";
import { displayPercent } from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";
import {
  dollarNote,
  governmentShift,
  ipcaExample,
  lastCopomNote,
  lastMonthChange,
  monthChangeNote,
  realRateTone,
  selicExample,
  stocksEffect,
  targetNote,
  unemploymentExample,
} from "../lib/economy";
import { DOLLAR, IBOVESPA, IPCA, REAL_RATE, SELIC } from "../lib/economy-metrics";

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

/** "+1,35 pelo governo": o que as medidas e as ligações somam ao número, em pontos ou em %. */
const governmentNote = (shift: string) => `${shift} pelo governo`;

/** Os pontos que o governo soma, quando passam da última casa mostrada. */
const visibleShift = (shift: number | null) => (shift !== null && Math.abs(shift) >= 0.005 ? shift : null);

/** " Na história, 3,75% hoje.": o número da série guardada, sem o governo; vazio sem a expansão Governo. */
const historyNote = (stored: string | null, format: (value: string) => string) =>
  stored === null ? "" : ` Na história, ${format(stored)} hoje.`;

/** Os números de hoje: SELIC, crescimento, Ibovespa (só com a expansão Governo), inflação, juro real e desemprego. */
export function EconomyKpis({ panel }: EconomyKpisProps) {
  const today = panel.points.at(-1);
  if (!today) return null;
  const { effects } = panel;
  const selicShift = visibleShift(governmentShift(today.selic, today.stored_selic));
  const ipcaShift = visibleShift(governmentShift(today.ipca, today.stored_ipca));
  const stocksShift = stocksEffect(today);

  return (
    <div className={cn("grid gap-3 sm:grid-cols-3", effects ? "xl:grid-cols-7" : "xl:grid-cols-6")}>
      {/* SELIC */}
      <Tile
        metric={SELIC}
        value={SELIC.format(today.selic)}
        note={selicShift !== null ? governmentNote(signedIpca(selicShift)) : lastCopomNote(panel.copom_changes)}
        description={`${selicExample(today)}${historyNote(today.stored_selic, (value) => displayPercent(value, 2))}`}
      />

      {/* Crescimento do PIB */}
      <Tile
        metric={GROWTH}
        value={GROWTH.format(today.growth)}
        note={monthChangeNote(lastMonthChange(panel.points, "growth"))}
        description={`${GROWTH.description}.${historyNote(panel.links && panel.growth_parts.history_growth, (value) => displayPercent(value, 1))}`}
        tone={Number(today.growth) < 0 ? "destructive" : "default"}
      />

      {/* Ibovespa */}
      {effects && today.ibovespa !== null && (
        <Tile
          metric={IBOVESPA}
          value={IBOVESPA.format(today.ibovespa)}
          note={
            stocksShift !== null && Math.abs(stocksShift) >= 0.0005
              ? governmentNote(signedStocks(stocksShift))
              : "sem efeito do governo"
          }
          description={`${IBOVESPA.description}.${historyNote(today.stored_ibovespa, IBOVESPA.format)}`}
        />
      )}

      {/* IPCA */}
      <Tile
        metric={IPCA}
        value={IPCA.format(today.ipca)}
        note={ipcaShift !== null ? governmentNote(signedIpca(ipcaShift)) : targetNote(today)}
        description={`${ipcaExample(today)}${historyNote(today.stored_ipca, (value) => displayPercent(value, 2))}`}
      />

      {/* Dólar */}
      <Tile
        metric={DOLLAR}
        value={DOLLAR.format(today.dollar)}
        note={dollarNote(today)}
        description={`${DOLLAR.description}.${historyNote(today.stored_dollar, DOLLAR.format)}`}
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
