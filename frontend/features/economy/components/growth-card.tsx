import { InfoHint } from "@/shared/components/info-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { GROWTH } from "@/shared/lib/budget-metrics";
import { cn } from "@/shared/lib/utils";
import { displayPercent } from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";
import { economyRows, growthLines, type GrowthLine } from "../lib/economy";
import { SeriesChart } from "./series-chart";

type GrowthCardProps = { panel: EconomyPanel };

const TONE_CLASS: Record<GrowthLine["tone"], string> = {
  up: "text-success",
  down: "text-destructive",
  neutral: "text-foreground",
};

/** O crescimento do PIB em 12 meses ao longo da partida e, embaixo, o que soma o alvo de hoje. */
export function GrowthCard({ panel }: GrowthCardProps) {
  const rows = economyRows(panel);
  const { growth_parts: parts } = panel;

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3">
          <div className="flex items-center gap-1.5">
            <h2 className="text-[15px] font-semibold">Crescimento do PIB, em 12 meses</h2>
            <InfoHint label="Como ler o crescimento">
              <div className="space-y-1 text-left">
                <p>{GROWTH.definition}</p>
                <p>
                  O crescimento caminha um quarto do trecho até o alvo a cada mês. O alvo soma a tendência de{" "}
                  {displayPercent(parts.trend, 0)}, o que o juro real empurra e o que a bolsa empurra.
                </p>
                <p>{GROWTH.example}</p>
              </div>
            </InfoHint>
          </div>

          <SeriesChart
            rows={rows}
            dataKey="growth"
            label="Crescimento"
            color="var(--chart-3)"
            reference={{ value: Number(parts.trend), label: "tendência" }}
          />

          {/* Por que o crescimento está onde está */}
          <span className="text-xs font-medium text-muted-foreground">Por que {displayPercent(parts.growth, 1)}</span>
          <div className="grid gap-1.5 text-[13px]">
            {growthLines(parts).map((line) => (
              <div key={line.label} className="flex items-start justify-between gap-4">
                <span className="grid">
                  {line.label}
                  {line.detail && <span className="text-xs text-muted-foreground">{line.detail}</span>}
                </span>
                <span className={cn("font-mono font-semibold", TONE_CLASS[line.tone])}>{line.value}</span>
              </div>
            ))}
            <div className="flex items-center justify-between gap-4 border-t pt-1.5">
              <span className="grid">
                Alvo do crescimento
                <span className="text-xs text-muted-foreground">
                  Para onde ele caminha, um quarto do trecho por mês
                </span>
              </span>
              <span className="font-mono font-semibold">{displayPercent(parts.target, 1)}</span>
            </div>
            <div className="flex items-center justify-between gap-4">
              <span className="font-medium">Crescimento hoje</span>
              <span className="font-mono font-semibold">{displayPercent(parts.growth, 1)}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
