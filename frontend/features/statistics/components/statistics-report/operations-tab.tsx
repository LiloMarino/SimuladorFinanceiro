import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { displayMoney, displayMoneyCompact, displayMonthYear } from "@/shared/lib/utils/display";
import { stringToColor } from "@/shared/lib/utils";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { playerLabel } from "../../lib/player-label";
import {
  BUY_TRADES,
  IMPACT_COST,
  INCOME_TAX_PAID,
  MONTHLY_VOLUME,
  SELL_TRADES,
  TRADED_VOLUME,
  TURNOVER,
} from "../../lib/metrics";
import { ChartCard, MetricsTable, TabStatus, type ReportProps } from "./shared";

export function OperationsTab({ simulationIds, showSimulation, currentPlayerName }: ReportProps) {
  const { data, isLoading } = useStatisticsReport("operations", simulationIds);
  if (!data) return <TabStatus loading={isLoading} />;

  const players = data.players.map((p) => ({ player: p, label: playerLabel(p, showSimulation) }));

  // Uma linha por mês, uma barra por jogador com o total negociado (compras + vendas)
  const months = new Map<string, Record<string, number | string>>();
  for (const { player, label } of players) {
    for (const m of player.monthly_volume) {
      const row = months.get(m.month) ?? { month: m.month };
      row[label] = Number(m.bought) + Number(m.sold);
      months.set(m.month, row);
    }
  }
  const chartData = [...months.values()].sort((a, b) => String(a.month).localeCompare(String(b.month)));

  return (
    <div className="space-y-6">
      <ChartCard metric={MONTHLY_VOLUME}>
        {chartData.length === 0 ? (
          <div className="h-72 flex items-center justify-center border border-dashed rounded-md text-sm text-muted-foreground">
            Nenhuma ação negociada.
          </div>
        ) : (
          <div className="h-[380px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 12, right: 16, left: 24, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                <XAxis dataKey="month" tickFormatter={(v: string) => displayMonthYear(new Date(`${v}T00:00:00`))} />
                <YAxis tickFormatter={(v: number) => displayMoneyCompact(v)} width={96} />
                <Tooltip
                  labelFormatter={(v: string) => displayMonthYear(new Date(`${v}T00:00:00`))}
                  formatter={(value: number) => displayMoney(value)}
                />
                <Legend />
                {players.map(({ label }) => (
                  <Bar key={label} dataKey={label} fill={stringToColor(label)} radius={[4, 4, 0, 0]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </ChartCard>

      <MetricsTable
        title="Operações por jogador"
        rows={data.players}
        showSimulation={showSimulation}
        currentPlayerName={currentPlayerName}
        columns={[
          { metric: BUY_TRADES, value: (p) => p.buy_trades },
          { metric: SELL_TRADES, value: (p) => p.sell_trades },
          { metric: TRADED_VOLUME, value: (p) => p.traded_volume },
          { metric: TURNOVER, value: (p) => p.turnover },
          { metric: INCOME_TAX_PAID, value: (p) => p.income_tax_paid },
          {
            metric: IMPACT_COST,
            value: (p) => p.impact_cost,
            className: (p) => (Number(p.impact_cost) > 0 ? "text-destructive" : ""),
          },
        ]}
      />
    </div>
  );
}
