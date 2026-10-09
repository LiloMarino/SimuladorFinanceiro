import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import type { PlayerPerformance } from "@/types";
import { RISK_METRICS, displayRiskMetric } from "../lib/risk-metrics";
import { RiskMetricHint } from "./risk-metric-hint";

interface Props {
  player: PlayerPerformance;
}

export function RiskSummaryCard({ player }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Risco da sua carteira</CardTitle>
        <CardDescription>Calculado sobre {player.history.length} dias de simulação</CardDescription>
      </CardHeader>

      <CardContent className="grid gap-6 md:grid-cols-3">
        {RISK_METRICS.map((metric) => (
          <div key={metric.key} className="space-y-1">
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              {metric.label}
              <RiskMetricHint metric={metric} />
            </div>
            <p className="text-2xl font-semibold">{displayRiskMetric(metric, player.risk)}</p>
            <p className="text-xs text-muted-foreground">{metric.description}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
