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
import { playerLabel, simulationColor, simulationLetter } from "../../lib/player-label";
import {
  ANNUAL_RETURN,
  CAPITAL_PROVIDED,
  CUMULATIVE_RETURN,
  MONTHS_ABOVE_CDI,
  NETWORTH,
  POSITIVE_MONTHS,
} from "../../lib/metrics";
import { PlayerLineChart, type LineSeries } from "./player-line-chart";
import type { ChartAxis } from "./player-line-chart/utils";
import { ChartCard, MetricsTable, TabStatus, type ReportProps } from "./shared";

const BENCHMARK_COLORS = { CDI: "var(--faint-foreground)", IBOV: "var(--foreground)" } as const;
const BENCHMARK_NAMES = { CDI: "CDI", IBOV: "Ibovespa" } as const;

type Benchmark = ReturnsReport["benchmarks"][number];
type Player = ReturnsReport["players"][number];
type View = "RETURN" | "NETWORTH";

function benchmarkLabel(benchmark: Benchmark, simulationIds: number[]) {
  const name = BENCHMARK_NAMES[benchmark.series];
  return simulationIds.length > 1 ? `${name} · ${simulationLetter(simulationIds, benchmark.simulation_id)}` : name;
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

export function ReturnsTab({ simulationIds, currentPlayerName, onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("returns", simulationIds, onlyPlayer);
  const [view, setView] = useState<View>("RETURN");
  const [axis, setAxis] = useState<ChartAxis>("index");
  if (!data)
    return <TabStatus loading={isLoading} title="a Rentabilidade" error={error} onRetry={() => void refetch()} />;

  const comparing = simulationIds.length > 1;
  const players = data.players.map((p) => ({ player: p, label: playerLabel(p, simulationIds) }));
  const colorOf = playerColors(players.map((p) => p.label));
  const isYou = (p: Player) => p.player_nickname === currentPlayerName;

  // Comparando partidas, a cor é da partida: você nela em destaque, os outros em cinza
  const playerSeries = (points: (p: Player) => Player["networth"]): LineSeries[] =>
    players.map(({ player, label }) => ({
      key: label,
      label,
      color: !comparing
        ? colorOf(label)
        : isYou(player)
          ? simulationColor(simulationIds, player.simulation_id)
          : "var(--faint-foreground)",
      points: points(player),
      emphasis: isYou(player),
      muted: comparing && !isYou(player),
    }));
  const benchmarkSeries: LineSeries[] = data.benchmarks.map((b) => {
    const label = benchmarkLabel(b, simulationIds);
    return {
      key: label,
      label,
      color:
        comparing && b.series === "CDI" ? simulationColor(simulationIds, b.simulation_id) : BENCHMARK_COLORS[b.series],
      points: b.cumulative_return,
      dashed: true,
      defaultVisible: !comparing || b.series === "CDI",
    };
  });

  const series =
    view === "RETURN"
      ? [...playerSeries((p) => p.cumulative_return), ...benchmarkSeries]
      : playerSeries((p) => p.networth);
  const chartAxis = comparing ? axis : "date";
  const seriesSetKey = `${view}|${chartAxis}|${series.map((s) => s.key).join("|")}`;

  return (
    <div className="grid gap-5">
      <ChartCard
        metric={view === "RETURN" ? CUMULATIVE_RETURN : NETWORTH}
        description={
          view !== "RETURN"
            ? undefined
            : comparing
              ? "Cada partida traz o CDI do próprio período, na cor dela. Linhas cinza: os outros jogadores."
              : "Quanto a carteira rendeu desde o começo, sem contar aportes. Tracejado: CDI e Ibovespa no mesmo período."
        }
        action={
          <div className="flex flex-wrap gap-2">
            {comparing && (
              <ToggleGroup
                variant="segmented"
                aria-label="Eixo do tempo"
                value={[axis]}
                onValueChange={(values) => values[0] && setAxis(values[0] as ChartAxis)}
              >
                <ToggleGroupItem value="index">Desde o início</ToggleGroupItem>
                <ToggleGroupItem value="date">Data real</ToggleGroupItem>
              </ToggleGroup>
            )}
            <ToggleGroup
              variant="segmented"
              aria-label="Medida do gráfico"
              value={[view]}
              onValueChange={(values) => values[0] && setView(values[0] as View)}
            >
              <ToggleGroupItem value="RETURN">Retorno %</ToggleGroupItem>
              <ToggleGroupItem value="NETWORTH">Patrimônio R$</ToggleGroupItem>
            </ToggleGroup>
          </div>
        }
      >
        <PlayerLineChart
          key={seriesSetKey}
          series={series}
          axis={chartAxis}
          format={view === "RETURN" ? (v) => displayPercent(v) : (v) => displayMoney(v)}
          axisFormat={view === "RETURN" ? (v) => displayPercent(v, 0) : (v) => displayMoneyCompact(v)}
        />
      </ChartCard>

      <MetricsTable
        title="Rentabilidade por jogador"
        description="Cada quadradinho é um mês da partida: verde bateu o CDI, azul subiu, cinza caiu."
        rows={data.players}
        simulationIds={simulationIds}
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
          <TableRow key={`${b.simulation_id}|${b.series}`}>
            <TableCell>
              <span className="text-muted-foreground">{benchmarkLabel(b, simulationIds)} · referência</span>
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
