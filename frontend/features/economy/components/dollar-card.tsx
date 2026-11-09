import { InfoHint } from "@/shared/components/info-hint";
import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { displayMoney } from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";
import { dollarLines, economyRows, type DollarLine } from "../lib/economy";
import { DOLLAR, DOLLAR_LINK, signedPoints } from "../lib/economy-metrics";
import { SeriesChart } from "./series-chart";

type DollarCardProps = { panel: EconomyPanel };

// Dólar mais caro encarece o que se importa: sobe em vermelho, cai em verde
const TONE_CLASS: Record<DollarLine["tone"], string> = {
  up: "text-destructive",
  down: "text-success",
  neutral: "text-foreground",
};

/** O dólar da partida ao longo do tempo e, embaixo, a história mais o que o prêmio de risco e o juro real somam. */
export function DollarCard({ panel }: DollarCardProps) {
  const { dollar_parts: parts } = panel;
  const passThrough = Number(parts.inflation);
  const passTone = Math.abs(passThrough) < 0.005 ? "neutral" : passThrough > 0 ? "up" : "down";

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3">
          <div className="flex items-center gap-1.5">
            <h2 className="text-[15px] font-semibold">Dólar, em reais</h2>
            <InfoHint label="Como ler o dólar">
              <div className="space-y-1 text-left">
                <p>{DOLLAR.definition}</p>
                <p>{DOLLAR.example}</p>
              </div>
            </InfoHint>
          </div>

          <SeriesChart
            rows={economyRows(panel)}
            dataKey="dollar"
            label="Dólar"
            color="var(--chart-2)"
            format={(value) => displayMoney(value)}
          />

          {/* Por que o dólar está onde está */}
          <span className="text-xs font-medium text-muted-foreground">Por que {displayMoney(parts.total)}</span>
          <div className="grid gap-1.5 text-[13px]">
            <div className="flex items-start justify-between gap-4">
              <span className="grid">
                Dólar da história
                <span className="text-xs text-muted-foreground">A PTAX no último mês fechado</span>
              </span>
              <span className="font-mono font-semibold">{displayMoney(parts.history)}</span>
            </div>
            {panel.links !== null &&
              dollarLines(parts).map((line) => (
                <div key={line.label} className="flex items-start justify-between gap-4">
                  <span className="grid">
                    <span className="inline-flex items-center gap-1">
                      {line.label}
                      <MetricHint metric={line.metric} />
                    </span>
                    <span className="text-xs text-muted-foreground">{line.detail}</span>
                  </span>
                  <span className={cn("font-mono font-semibold", TONE_CLASS[line.tone])}>{line.value}</span>
                </div>
              ))}
            <div className="flex items-center justify-between gap-4 border-t pt-1.5">
              <span className="font-medium">Dólar hoje</span>
              <span className="font-mono font-semibold">{displayMoney(parts.total)}</span>
            </div>
            {panel.links !== null && (
              <div className="flex items-start justify-between gap-4 pt-1.5">
                <span className="grid">
                  <span className="inline-flex items-center gap-1">
                    Repasse ao IPCA
                    <MetricHint metric={DOLLAR_LINK} />
                  </span>
                  <span className="text-xs text-muted-foreground">
                    A alta do dólar em 12 meses contra a da história encarece o importado
                  </span>
                </span>
                <span className={cn("font-mono font-semibold", TONE_CLASS[passTone])}>
                  {signedPoints(passThrough / 100)} ponto{Math.abs(passThrough) >= 1.95 ? "s" : ""}
                </span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
