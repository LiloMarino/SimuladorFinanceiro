import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/shared/components/ui/tabs";
import { MetricLineChart } from "./metric-line-chart";
import type { PerformanceMetric, PlayerPerformance } from "@/types";
import { playerLabel } from "../../lib/player-label";

const TABS: { key: PerformanceMetric; label: string }[] = [
  { key: "total_networth", label: "Patrimônio Total" },
  { key: "total_equity", label: "Renda Variável" },
  { key: "total_fixed", label: "Renda Fixa" },
  { key: "total_cash", label: "Caixa" },
  { key: "total_contribution", label: "Total Aportado" },
] as const;

interface PerformanceChartProps {
  players: PlayerPerformance[];
  showSimulation?: boolean;
}

export function PerformanceChart({ players, showSimulation = false }: PerformanceChartProps) {
  // A visibilidade das séries nasce com o gráfico: um conjunto novo de séries remonta o gráfico
  const seriesSetKey = players.map((p) => playerLabel(p, showSimulation)).join("|");

  return (
    <Card>
      <CardHeader className="space-y-4">
        <CardTitle>Desempenho da Partida</CardTitle>

        <Tabs defaultValue={TABS[0].key}>
          <TabsList>
            {TABS.map((t) => (
              <TabsTrigger key={t.key} value={t.key}>
                {t.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {TABS.map((t) => (
            <TabsContent key={t.key} value={t.key}>
              <MetricLineChart
                key={seriesSetKey}
                metric={t.key}
                players={players}
                showSimulation={showSimulation}
              />
            </TabsContent>
          ))}
        </Tabs>
      </CardHeader>

      <CardContent />
    </Card>
  );
}
