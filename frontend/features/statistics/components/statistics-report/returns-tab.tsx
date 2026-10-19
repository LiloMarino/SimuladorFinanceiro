import { useState } from "react";
import { TableCell, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import {
  displayMoney,
  displayMoneyCompact,
  displayNumber,
  displayMonthSlashYear,
  displayPercent,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import { TeamBadge } from "@/shared/components/team-badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { teamColor, teamName } from "@/shared/lib/teams";
import type { ReturnsReport } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { playerLabel, simulationColor, simulationLetter, youLabel, labelColors } from "../../lib/player-label";
import {
  ANNUAL_RETURN,
  CAPITAL_PROVIDED,
  CUMULATIVE_RETURN,
  MONTHS_ABOVE_CDI,
  NETWORTH,
  POSITIVE_MONTHS,
  VS_CDI,
} from "../../lib/metrics";
import { PlayerLineChart, type LineSeries } from "./player-line-chart";
import type { ChartAxis } from "./player-line-chart/utils";
import { ChartCard, MetricsTable, TabStatus, type ReportProps } from "./shared";

// Pregões por mês, para ler o eixo "desde o início" em meses
const TRADING_DAYS_PER_MONTH = 21;

const BENCHMARK_COLORS = { CDI: "var(--faint-foreground)", IBOV: "var(--warning)" } as const;
const BENCHMARK_NAMES = { CDI: "CDI", IBOV: "Ibovespa" } as const;

type Benchmark = ReturnsReport["benchmarks"][number];
type Player = ReturnsReport["players"][number];
type View = "RETURN" | "NETWORTH";
// Partida em equipes: só as médias das equipes, os jogadores, ou os membros de uma equipe contra as outras
type Scope = "TEAMS" | "PLAYERS" | "TEAM";
type TeamReturns = ReturnsReport["teams"][number];

function benchmarkLabel(benchmark: Benchmark, simulationIds: number[]) {
  const name = BENCHMARK_NAMES[benchmark.series];
  return simulationIds.length > 1 ? `${name} · ${simulationLetter(simulationIds, benchmark.simulation_id)}` : name;
}

/** Cada mês da partida num quadradinho: colorido quando passou no teste da coluna, cinza quando não. */
function MonthStrip({
  months,
  passed,
  color,
}: {
  months: Player["monthly_returns"];
  passed: (m: Player["monthly_returns"][number]) => boolean;
  color: string;
}) {
  return (
    <span className="flex gap-0.5">
      {months.map((m) => (
        <Tooltip key={m.month}>
          <TooltipTrigger render={<span />}>
            <span className={cn("block size-3 rounded-[3px]", passed(m) ? color : "bg-muted")} />
          </TooltipTrigger>
          <TooltipContent>
            {displayMonthSlashYear(m.month)}: {displaySignedPercent(m.value)} · CDI {displayPercent(m.cdi)}
          </TooltipContent>
        </Tooltip>
      ))}
    </span>
  );
}

/** Faixa de meses e a contagem ("8 de 12") lado a lado. */
function MonthsCell({
  months,
  count,
  passed,
  color,
}: {
  months: Player["monthly_returns"];
  count: number;
  passed: (m: Player["monthly_returns"][number]) => boolean;
  color: string;
}) {
  return (
    <span className="flex items-center justify-end gap-2.5">
      <MonthStrip months={months} passed={passed} color={color} />
      <span className="font-mono">
        {count} de {months.length}
      </span>
    </span>
  );
}

/** Contagem da equipe: média de meses entre os membros, arredondada na faixa e exata entre parênteses. */
function TeamMonthsCell({ average, months, color }: { average: string; months: number; color: string }) {
  const rounded = Math.round(Number(average));
  const exact = Number.isInteger(Number(average)) ? null : displayNumber(average, 1);
  return (
    <span className="flex items-center justify-end gap-2.5">
      <span className="flex gap-0.5">
        {Array.from({ length: months }, (_, i) => (
          <span key={i} className={cn("block size-3 rounded-[3px]", i < rounded ? color : "bg-muted")} />
        ))}
      </span>
      <span className="font-mono">
        {rounded} de {months}
        {exact && <span className="text-muted-foreground"> ({exact})</span>}
      </span>
    </span>
  );
}

const aboveCdi = (m: Player["monthly_returns"][number]) => Number(m.value) > Number(m.cdi);
const positive = (m: Player["monthly_returns"][number]) => Number(m.value) > 0;

export function ReturnsTab({ simulationIds, currentPlayerName, onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("returns", simulationIds, onlyPlayer);
  const [view, setView] = useState<View>("RETURN");
  const [axis, setAxis] = useState<ChartAxis>("index");
  const [scopeChoice, setScope] = useState<Scope>("TEAMS");
  const [focusChoice, setFocus] = useState<number | null>(null);
  if (!data)
    return <TabStatus loading={isLoading} title="a Rentabilidade" error={error} onRetry={() => void refetch()} />;

  const comparing = simulationIds.length > 1;
  const players = data.players.map((p) => ({ player: p, label: playerLabel(p, simulationIds, currentPlayerName) }));
  const colorOf = labelColors(data.players, simulationIds, currentPlayerName);
  const isYou = (p: Player) => p.player_nickname === currentPlayerName;
  const cdiOf = new Map(data.benchmarks.filter((b) => b.series === "CDI").map((b) => [b.simulation_id, b.annual_return]));

  // Comparando partidas, a cor é da partida: você nela em destaque, os outros em cinza
  const playerSeries = (points: (p: Player) => Player["networth"]): LineSeries[] =>
    players.map(({ player, label }) => ({
      key: label,
      label: youLabel(label, isYou(player)),
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

  const inTeams = data.teams.length > 0;
  const naming = data.team_naming;
  const scope: Scope = inTeams ? scopeChoice : "PLAYERS";
  const myTeam = data.players.find(isYou)?.team ?? data.teams[0]?.team ?? null;
  const focus = data.teams.some((t) => t.team === focusChoice) ? focusChoice : myTeam;
  const playerPoints = view === "RETURN" ? (p: Player) => p.cumulative_return : (p: Player) => p.networth;
  const teamSeries = (t: TeamReturns, options: Partial<LineSeries> = {}): LineSeries => ({
    key: `team-${t.team}`,
    label: `${teamName(t.team, naming)} · média`,
    color: teamColor(t.team),
    points: view === "RETURN" ? t.cumulative_return : t.networth,
    emphasis: true,
    ...options,
  });
  const references = view === "RETURN" ? benchmarkSeries : [];
  const focusMembers = new Set(
    data.players.filter((p) => p.team === focus).map((p) => playerLabel(p, simulationIds, currentPlayerName)),
  );
  const series =
    scope === "TEAMS"
      ? [...data.teams.map((t) => teamSeries(t)), ...references]
      : scope === "TEAM"
        ? [
            ...playerSeries(playerPoints).filter((s) => focusMembers.has(s.key)),
            ...data.teams.map((t) =>
              teamSeries(t, t.team === focus ? {} : { emphasis: false, muted: true, dashed: true }),
            ),
            ...references.filter((r) => r.key === "CDI"),
          ]
        : [...playerSeries(playerPoints), ...references];
  const chartAxis = comparing ? axis : "date";
  // Entre partidas, o eixo "desde o início" marca de 3 em 3 meses: mês 0, 3, 6...
  const longest = Math.max(...series.map((s) => s.points.length), 0);
  const monthTicks =
    comparing && chartAxis === "index"
      ? Array.from(
          { length: Math.floor((longest - 1) / (TRADING_DAYS_PER_MONTH * 3)) + 1 },
          (_, i) => 1 + i * TRADING_DAYS_PER_MONTH * 3,
        )
      : undefined;
  const seriesSetKey = `${scope}|${focus}|${view}|${chartAxis}|${series.map((s) => s.key).join("|")}`;

  return (
    <div className="grid gap-5">
      <ChartCard
        metric={view === "RETURN" ? CUMULATIVE_RETURN : NETWORTH}
        description={
          scope === "TEAMS"
            ? "Uma linha por equipe, na cor dela: a média dos membros. Compara equipe com equipe, sem os jogadores."
            : scope === "TEAM"
              ? "Os membros na cor de cada um e a média da equipe em destaque. As outras equipes ficam como referência, finas e apagadas."
              : view !== "RETURN"
                ? undefined
                : comparing
                  ? "Cada partida traz o CDI do próprio período, na cor dela. Linhas cinza: os outros jogadores."
                  : "Quanto a carteira rendeu desde o começo, sem contar aportes. Tracejado: CDI e Ibovespa no mesmo período."
        }
        action={
          <div className="flex flex-wrap gap-2">
            {inTeams && (
              <>
                <ToggleGroup
                  variant="segmented"
                  aria-label="Visão do gráfico"
                  value={[scope]}
                  onValueChange={(values) => values[0] && setScope(values[0] as Scope)}
                >
                  <ToggleGroupItem value="TEAMS">Equipes</ToggleGroupItem>
                  <ToggleGroupItem value="PLAYERS">Jogadores</ToggleGroupItem>
                  <ToggleGroupItem value="TEAM">Dentro da equipe</ToggleGroupItem>
                </ToggleGroup>
                {scope === "TEAM" && focus !== null && (
                  <Select
                    value={String(focus)}
                    onValueChange={(value) => setFocus(Number(value))}
                    items={Object.fromEntries(data.teams.map((t) => [String(t.team), teamName(t.team, naming)]))}
                  >
                    <SelectTrigger aria-label="Equipe">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {data.teams.map((t) => (
                        <SelectItem key={t.team} value={String(t.team)}>
                          <TeamBadge team={t.team} naming={naming} form="full" size="sm" />
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </>
            )}
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
          axisFormat={view === "RETURN" ? (v) => displaySignedPercent(v, 0) : (v) => displayMoneyCompact(v)}
          xTicks={monthTicks}
          xTickFormat={monthTicks ? (x) => `mês ${Math.round((x - 1) / TRADING_DAYS_PER_MONTH)}` : undefined}
        />
      </ChartCard>

      <MetricsTable
        title={inTeams ? "Rentabilidade por equipe" : "Rentabilidade por jogador"}
        description={
          inTeams
            ? "Linha da equipe = média dos membros. Nos meses, a equipe mostra a média arredondada (entre parênteses, a exata)."
            : "Cada quadradinho é um mês da partida: colorido bateu o teste da coluna, cinza não."
        }
        groups={inTeams ? { naming, teams: data.teams } : undefined}
        rows={data.players}
        simulationIds={simulationIds}
        currentPlayerName={currentPlayerName}
        columns={[
          { metric: CAPITAL_PROVIDED, value: (r) => r.capital_provided, teamValue: (t) => t.capital_provided },
          {
            metric: ANNUAL_RETURN,
            value: (r) => r.annual_return,
            teamValue: (t) => t.annual_return,
            best: "max",
            tone: (r) => (r.annual_return && Number(r.annual_return) < 0 ? "negative" : undefined),
          },
          {
            metric: VS_CDI,
            teamValue: (t) => {
              const cdi = cdiOf.get(t.simulation_id);
              return t.annual_return !== null && cdi ? Number(t.annual_return) - Number(cdi) : null;
            },
            value: (r) => {
              const cdi = cdiOf.get(r.simulation_id);
              return r.annual_return !== null && cdi ? Number(r.annual_return) - Number(cdi) : null;
            },
            tone: (r) => {
              const cdi = cdiOf.get(r.simulation_id);
              if (r.annual_return === null || !cdi) return undefined;
              return Number(r.annual_return) >= Number(cdi) ? "positive" : "negative";
            },
          },
          {
            metric: MONTHS_ABOVE_CDI,
            value: (r) => r.months_above_cdi,
            cell: (r) => <MonthsCell months={r.monthly_returns} count={r.months_above_cdi} passed={aboveCdi} color="bg-success" />,
            teamCell: (t) => <TeamMonthsCell average={t.months_above_cdi} months={t.months} color="bg-success" />,
          },
          {
            metric: POSITIVE_MONTHS,
            value: (r) => r.positive_months,
            cell: (r) => <MonthsCell months={r.monthly_returns} count={r.positive_months} passed={positive} color="bg-chart-1" />,
            teamCell: (t) => <TeamMonthsCell average={t.positive_months} months={t.months} color="bg-chart-1" />,
          },
        ]}
        footer={data.benchmarks.map((b) => (
          <TableRow key={`${b.simulation_id}|${b.series}`}>
            <TableCell>
              <span className="text-muted-foreground">{benchmarkLabel(b, simulationIds)} · referência</span>
            </TableCell>
            <TableCell numeric>—</TableCell>
            <TableCell numeric>{b.annual_return ? displayPercent(b.annual_return) : "—"}</TableCell>
            <TableCell numeric>—</TableCell>
            <TableCell numeric>—</TableCell>
            <TableCell numeric>—</TableCell>
          </TableRow>
        ))}
      />
    </div>
  );
}
