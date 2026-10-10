import { TableCell, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayMoneyCompact, displayPercent, isLoss } from "@/shared/lib/utils/display";
import type { ReturnsReport } from "@/types";
import { stringToColor } from "@/shared/lib/utils";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { playerLabel } from "../../lib/player-label";
import {
  ANNUAL_RETURN,
  CAPITAL_PROVIDED,
  CUMULATIVE_RETURN,
  MONTHS_ABOVE_CDI,
  NETWORTH,
  POSITIVE_MONTHS,
} from "../../lib/metrics";
import { PlayerLineChart, type LineSeries } from "./player-line-chart";
import { ChartCard, MetricsTable, TabStatus, type ReportProps } from "./shared";

const BENCHMARK_COLORS = { CDI: "var(--color-chart-4)", IBOV: "var(--color-chart-3)" } as const;
const BENCHMARK_NAMES = { CDI: "CDI", IBOV: "Ibovespa" } as const;

type Benchmark = ReturnsReport["benchmarks"][number];

function benchmarkLabel(benchmark: Benchmark, showSimulation: boolean) {
  const name = BENCHMARK_NAMES[benchmark.series];
  return showSimulation ? `${name}#${benchmark.simulation_name}` : name;
}

function fraction(done: number, total: number) {
  return `${done} de ${total}`;
}

export function ReturnsTab({ simulationIds, showSimulation, currentPlayerName }: ReportProps) {
  const { data, isLoading } = useStatisticsReport("returns", simulationIds);
  if (!data) return <TabStatus loading={isLoading} />;

  const players = data.players.map((p) => ({ player: p, label: playerLabel(p, showSimulation) }));
  const cumulative: LineSeries[] = [
    ...players.map(({ player, label }) => ({
      key: label,
      label,
      color: stringToColor(label),
      points: player.cumulative_return,
    })),
    ...data.benchmarks.map((b) => {
      const label = benchmarkLabel(b, showSimulation);
      return { key: label, label, color: BENCHMARK_COLORS[b.series], points: b.cumulative_return, dashed: true };
    }),
  ];
  const networth: LineSeries[] = players.map(({ player, label }) => ({
    key: label,
    label,
    color: stringToColor(label),
    points: player.networth,
  }));
  const seriesSetKey = cumulative.map((s) => s.key).join("|");

  return (
    <div className="space-y-6">
      <ChartCard metric={CUMULATIVE_RETURN}>
        <PlayerLineChart
          key={seriesSetKey}
          series={cumulative}
          format={(v) => displayPercent(v)}
          axisFormat={(v) => displayPercent(v, 0)}
        />
      </ChartCard>

      <ChartCard metric={NETWORTH}>
        <PlayerLineChart
          key={seriesSetKey}
          series={networth}
          format={(v) => displayMoney(v)}
          axisFormat={(v) => displayMoneyCompact(v)}
        />
      </ChartCard>

      <MetricsTable
        title="Rentabilidade por jogador"
        rows={data.players}
        showSimulation={showSimulation}
        currentPlayerName={currentPlayerName}
        columns={[
          { metric: CAPITAL_PROVIDED, value: (p) => p.capital_provided },
          {
            metric: ANNUAL_RETURN,
            value: (p) => p.annual_return,
            className: (p) => (p.annual_return && isLoss(p.annual_return) ? "text-destructive" : ""),
          },
          { metric: MONTHS_ABOVE_CDI, value: (p) => fraction(p.months_above_cdi, p.months) },
          { metric: POSITIVE_MONTHS, value: (p) => fraction(p.positive_months, p.months) },
        ]}
        footer={data.benchmarks.map((b) => (
          <TableRow key={benchmarkLabel(b, true)} className="text-muted-foreground">
            <TableCell>{benchmarkLabel(b, showSimulation)} (referência)</TableCell>
            <TableCell className="text-center">—</TableCell>
            <TableCell className="text-center">{b.annual_return ? displayPercent(b.annual_return) : "—"}</TableCell>
            <TableCell className="text-center">—</TableCell>
            <TableCell className="text-center">—</TableCell>
          </TableRow>
        ))}
      />
    </div>
  );
}
