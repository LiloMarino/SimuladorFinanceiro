import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/shared/components/ui/tabs";
import { MetricLineChart } from "./metric-line-chart";
import type { PerformanceMetric, PlayerHistory } from "@/types";

const TABS: { key: PerformanceMetric; label: string }[] = [
  { key: "total_networth", label: "Patrimônio Total" },
  { key: "total_equity", label: "Renda Variável" },
  { key: "total_fixed", label: "Renda Fixa" },
  { key: "total_cash", label: "Caixa" },
  { key: "total_contribution", label: "Total Aportado" },
] as const;

interface PerformanceChartProps {
  playersHistory: PlayerHistory[];
}

export function PerformanceChart({ playersHistory }: PerformanceChartProps) {
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
              <MetricLineChart metric={t.key} players={playersHistory} />
            </TabsContent>
          ))}
        </Tabs>
      </CardHeader>

      <CardContent />
    </Card>
  );
}
