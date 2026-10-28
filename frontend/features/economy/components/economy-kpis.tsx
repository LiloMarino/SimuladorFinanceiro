import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import type { EconomyPanel } from "@/types";
import { ipcaExample, lastCopomNote, realRateTone, selicExample, targetNote } from "../lib/economy";
import { IPCA, REAL_RATE, SELIC } from "../lib/economy-metrics";

type EconomyKpisProps = { panel: EconomyPanel };

type TileProps = {
  metric: typeof SELIC;
  value: string;
  note: string;
  description: string;
  tone?: "destructive" | "default";
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

/** Os três números de hoje: SELIC, inflação de 12 meses e o juro real que sobra entre as duas. */
export function EconomyKpis({ panel }: EconomyKpisProps) {
  const today = panel.points.at(-1);
  if (!today) return null;

  return (
    <div className="grid gap-3 sm:grid-cols-3">
      {/* SELIC */}
      <Tile
        metric={SELIC}
        value={SELIC.format(today.selic)}
        note={lastCopomNote(panel.copom_changes)}
        description={selicExample(today)}
      />

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
    </div>
  );
}
