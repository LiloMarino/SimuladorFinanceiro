import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { DEBT_GDP, GROWTH, UNEMPLOYMENT } from "@/shared/lib/budget-metrics";
import type { EconomyPanel } from "@/types";
import {
  debtNote,
  debtTone,
  growthExample,
  ipcaExample,
  lastCopomNote,
  lastMonthChange,
  monthChangeNote,
  realRateTone,
  selicExample,
  targetNote,
  unemploymentExample,
} from "../lib/economy";
import { IPCA, REAL_RATE, SELIC } from "../lib/economy-metrics";

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

/** Os números de hoje: SELIC, crescimento, dívida (só com a expansão Governo), inflação, juro real e desemprego. */
export function EconomyKpis({ panel }: EconomyKpisProps) {
  const today = panel.points.at(-1);
  if (!today) return null;
  const { debt, growth_parts: parts } = panel;

  return (
    <div className={cn("grid gap-3 sm:grid-cols-3", debt ? "xl:grid-cols-6" : "xl:grid-cols-5")}>
      {/* SELIC */}
      <Tile
        metric={SELIC}
        value={SELIC.format(today.selic)}
        note={lastCopomNote(panel.copom_changes)}
        description={selicExample(today)}
      />

      {/* Crescimento do PIB */}
      <Tile
        metric={GROWTH}
        value={GROWTH.format(today.growth)}
        note={monthChangeNote(lastMonthChange(panel.points, "growth"))}
        description={growthExample(parts.trend)}
        tone={Number(today.growth) < 0 ? "destructive" : "default"}
      />

      {/* Dívida em % do PIB */}
      {debt && (
        <Tile
          metric={DEBT_GDP}
          value={DEBT_GDP.format(debt.debt)}
          note={debtNote(debt.premium)}
          description="Quanto o governo deve perto de tudo o que o país produz num ano."
          tone={debtTone(debt.premium)}
        />
      )}

      {/* IPCA */}
      <Tile metric={IPCA} value={IPCA.format(today.ipca)} note={targetNote(today)} description={ipcaExample(today)} />

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
