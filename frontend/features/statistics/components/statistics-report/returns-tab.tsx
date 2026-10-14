import { useState } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { TableCell, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import {
  displayMoney,
  displayMoneyCompact,
  displayMonthSlashYear,
  displayPercent,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { ReturnsReport } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { playerColors } from "../../lib/player-colors";
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

const BENCHMARK_COLORS = { CDI: "var(--faint-foreground)", IBOV: "var(--foreground)" } as const;
const BENCHMARK_NAMES = { CDI: "CDI", IBOV: "Ibovespa" } as const;

type Benchmark = ReturnsReport["benchmarks"][number];
type Player = ReturnsReport["players"][number];
type View = "RETURN" | "NETWORTH";

function benchmarkLabel(benchmark: Benchmark, showSimulation: boolean) {
  const name = BENCHMARK_NAMES[benchmark.series];
  return showSimulation ? `${name}#${benchmark.simulation_name}` : name;
}

/** Cada mês da partida num quadradinho: verde bateu o CDI, azul só subiu, cinza caiu. */
function MonthStrip({ months }: { months: Player["monthly_returns"] }) {
  return (
    <span className="flex gap-0.5">
      {months.map((m) => {
        const aboveCdi = Number(m.value) > Number(m.cdi);
        const positive = Number(m.value) > 0;
        return (
          <Tooltip key={m.month}>
            <TooltipTrigger render={<span />}>
              <span
                className={cn(
                  "block size-3 rounded-[3px]",
                  aboveCdi ? "bg-success" : positive ? "bg-chart-1/60" : "bg-muted",
                )}
              />
            </TooltipTrigger>
            <TooltipContent>
              {displayMonthSlashYear(m.month)}: {displaySignedPercent(m.value)} · CDI {displayPercent(m.cdi)}
            </TooltipContent>
          </Tooltip>
        );
      })}
    </span>
  );
}

export function ReturnsTab({ simulationIds, showSimulation, currentPlayerName }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("returns", simulationIds);
  const [view, setView] = useState<View>("RETURN");
  if (!data)
    return <TabStatus loading={isLoading} title="a Rentabilidade" error={error} onRetry={() => void refetch()} />;

  const players = data.players.map((p) => ({ player: p, label: playerLabel(p, showSimulation) }));
  const colorOf = playerColors(players.map((p) => p.label));
  const isYou = (p: Player) => p.player_nickname === currentPlayerName;

  const series: LineSeries[] =
    view === "RETURN"
      ? [
          ...players.map(({ player, label }) => ({
            key: label,
            label,
            color: colorOf(label),
            points: player.cumulative_return,
            emphasis: isYou(player),
          })),
          ...data.benchmarks.map((b) => {
            const label = benchmarkLabel(b, showSimulation);
            return { key: label, label, color: BENCHMARK_COLORS[b.series], points: b.cumulative_return, dashed: true };
          }),
        ]
      : players.map(({ player, label }) => ({
          key: label,
          label,
          color: colorOf(label),
          points: player.networth,
          emphasis: isYou(player),
        }));
  const seriesSetKey = `${view}|${series.map((s) => s.key).join("|")}`;

  return (
    <div className="grid gap-5">
      <ChartCard
        metric={view === "RETURN" ? CUMULATIVE_RETURN : NETWORTH}
        description={
          view === "RETURN"
            ? "Quanto a carteira rendeu desde o começo, sem contar aportes. Tracejado: CDI e Ibovespa no mesmo período."
            : undefined
        }
        action={
          <ToggleGroup
            variant="segmented"
            aria-label="Medida do gráfico"
            value={[view]}
            onValueChange={(values) => values[0] && setView(values[0] as View)}
          >
            <ToggleGroupItem value="RETURN">Retorno %</ToggleGroupItem>
            <ToggleGroupItem value="NETWORTH">Patrimônio R$</ToggleGroupItem>
          </ToggleGroup>
        }
      >
        <PlayerLineChart
          key={seriesSetKey}
          series={series}
          format={view === "RETURN" ? (v) => displayPercent(v) : (v) => displayMoney(v)}
          axisFormat={view === "RETURN" ? (v) => displayPercent(v, 0) : (v) => displayMoneyCompact(v)}
        />
      </ChartCard>

      <MetricsTable
        title="Rentabilidade por jogador"
        description="Cada quadradinho é um mês da partida: verde bateu o CDI, azul subiu, cinza caiu."
        rows={data.players}
        showSimulation={showSimulation}
        currentPlayerName={currentPlayerName}
        colorOf={colorOf}
        extraColumn={{ header: "Meses", cell: (row) => <MonthStrip months={row.monthly_returns} /> }}
        columns={[
          { metric: CAPITAL_PROVIDED, value: (r) => r.capital_provided },
          {
            metric: ANNUAL_RETURN,
            value: (r) => r.annual_return,
            best: "max",
            tone: (r) => (r.annual_return && Number(r.annual_return) < 0 ? "negative" : undefined),
          },
          { metric: MONTHS_ABOVE_CDI, value: (r) => `${r.months_above_cdi} de ${r.months}`, best: undefined },
          { metric: POSITIVE_MONTHS, value: (r) => `${r.positive_months} de ${r.months}` },
        ]}
        footer={data.benchmarks.map((b) => (
          <TableRow key={benchmarkLabel(b, true)}>
            <TableCell>
              <span className="text-muted-foreground">{benchmarkLabel(b, showSimulation)} · referência</span>
            </TableCell>
            <TableCell />
            <TableCell numeric>—</TableCell>
            <TableCell numeric>{b.annual_return ? displayPercent(b.annual_return) : "—"}</TableCell>
            <TableCell numeric>—</TableCell>
            <TableCell numeric>—</TableCell>
          </TableRow>
        ))}
      />
      {data.players.length === 0 && <Badge variant="secondary">Sem jogadores com patrimônio ainda</Badge>}
    </div>
  );
}
