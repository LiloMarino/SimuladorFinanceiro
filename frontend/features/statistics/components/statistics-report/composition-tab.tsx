import { Fragment, useState, type CSSProperties } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/shared/components/ui/table";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber, type SortColumns } from "@/shared/lib/table-sort";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { MetricHint } from "@/shared/components/metric-hint";
import { TeamBadge } from "@/shared/components/team-badge";
import { teamColor } from "@/shared/lib/teams";
import {
  displayMoney,
  displayMonthSlashYear,
  displayNumber,
  displayPercent,
  displayShortMonthYear,
} from "@/shared/lib/utils/display";
import type { CompositionPlayer, CompositionReport, TeamNaming } from "@/types";
import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";
import { EFFECTIVE_SECTORS, SECTOR_PROFIT } from "../../lib/metrics";
import { playerKey, playerLabel } from "../../lib/player-label";
import { groupByTeam } from "../../lib/teams";
import { PlayerCell, TabStatus, type ReportProps } from "./shared";

type TeamComposition = CompositionReport["teams"][number];
type Unit = "PCT" | "MONEY";

const SERIES = [
  { key: "total_cash", label: "Caixa", color: "var(--chart-3)" },
  { key: "total_equity", label: "Renda variável", color: "var(--chart-1)" },
  { key: "total_fixed", label: "Renda fixa", color: "var(--chart-2)" },
] as const;

const NO_SECTOR = "Sem setor";

/** A diversificação em palavras: 1 é tudo num setor; 4 é dividido igual em quatro. */
function diversificationWord(value: number) {
  if (value < 2) return "concentrado";
  if (value < 3) return "moderado";
  return "diversificado";
}

export function CompositionTab({ simulationIds, currentPlayerName, onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("composition", simulationIds, onlyPlayer);
  const [unit, setUnit] = useState<Unit>("PCT");
  if (!data)
    return (
      <TabStatus
        simulationIds={simulationIds}
        loading={isLoading}
        title="a Composição"
        error={error}
        onRetry={() => void refetch()}
      />
    );

  const naming = data.team_naming;
  const groups = groupByTeam(
    data.players,
    data.teams.map((t) => t.team),
  );
  const teamOf = (team: number | null) => data.teams.find((t) => t.team === team);

  return (
    <div className="grid gap-5">
      {/* Como cada um dividiu o dinheiro */}
      <Card>
        <CardHeader>
          <CardTitle>Como cada um dividiu o dinheiro</CardTitle>
          <CardDescription>
            {data.teams.length > 0
              ? "Agrupado por equipe. A média da equipe fica no cabeçalho do grupo."
              : "Fatia do patrimônio em caixa, ações e renda fixa, dia a dia. Todos lado a lado."}
          </CardDescription>
          <CardAction>
            <ToggleGroup
              variant="segmented"
              aria-label="Unidade"
              value={[unit]}
              onValueChange={(values) => values[0] && setUnit(values[0] as Unit)}
            >
              <ToggleGroupItem value="PCT">Em %</ToggleGroupItem>
              <ToggleGroupItem value="MONEY">Em R$</ToggleGroupItem>
            </ToggleGroup>
          </CardAction>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
              {SERIES.map((s) => (
                <span key={s.key} className="flex items-center gap-1.5">
                  <span className="size-2.5 rounded-sm" style={{ backgroundColor: s.color }} aria-hidden="true" />
                  {s.label}
                </span>
              ))}
            </div>
            {groups.map((group) => (
              <div key={group.team ?? "all"} className="grid gap-3">
                {group.team !== null && (
                  <TeamGroupHeader team={group.team} naming={naming} composition={teamOf(group.team)} />
                )}
                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  {group.players.map((p) => {
                    const label = playerLabel(p, simulationIds, currentPlayerName);
                    return (
                      <SmallMultiple
                        key={playerKey(p)}
                        player={p}
                        label={label}
                        simulationIds={simulationIds}
                        isYou={p.player_nickname === currentPlayerName}
                        unit={unit}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <SectorExposure
        players={data.players}
        groups={groups}
        naming={naming}
        simulationIds={simulationIds}
        currentPlayerName={currentPlayerName}
      />
      <SectorProfit
        players={data.players}
        groups={groups}
        naming={naming}
        simulationIds={simulationIds}
        currentPlayerName={currentPlayerName}
      />
    </div>
  );
}

type Groups = ReturnType<typeof groupByTeam<CompositionPlayer>>;

/** Cabeçalho do grupo da equipe: o selo, e a divisão média do dinheiro dos membros. */
function TeamGroupHeader({
  team,
  naming,
  composition,
}: {
  team: number;
  naming: TeamNaming;
  composition: TeamComposition | undefined;
}) {
  const share = (value: string | null | undefined) =>
    value === null || value === undefined ? "—" : displayPercent(value, 0);
  return (
    <div
      className="flex flex-wrap items-center gap-3 border-l-[3px] border-(--team) pl-3"
      style={{ "--team": teamColor(team) } as CSSProperties}
    >
      <TeamBadge team={team} naming={naming} form="full" />
      {composition && (
        <span className="text-xs text-muted-foreground">
          média: <span className="text-chart-3">{share(composition.cash_share)} caixa</span> ·{" "}
          <span className="text-chart-1">{share(composition.equity_share)} RV</span> ·{" "}
          <span className="text-chart-2">{share(composition.fixed_share)} RF</span>
        </span>
      )}
    </div>
  );
}

function SmallMultiple({
  player,
  label,
  simulationIds,
  isYou,
  unit,
}: {
  player: CompositionPlayer;
  label: string;
  simulationIds: number[];
  isYou: boolean;
  unit: Unit;
}) {
  const rows = player.history.map((h) => ({
    date: h.snapshot_date,
    total_cash: Number(h.total_cash),
    total_equity: Number(h.total_equity),
    total_fixed: Number(h.total_fixed),
  }));
  const first = rows[0];
  const last = rows.at(-1);
  const total = last ? last.total_cash + last.total_equity + last.total_fixed : 0;
  const share = (value: number) => displayPercent(total > 0 ? value / total : 0, 0);

  return (
    <div className="grid content-start gap-1.5">
      <span className="text-[13px] font-semibold">
        <PlayerCell player={player} label={label} simulationIds={simulationIds} isYou={isYou} />
      </span>
      {rows.length < 2 || !first || !last ? (
        <div className="flex h-36 items-center justify-center rounded-lg border border-dashed border-input text-xs text-muted-foreground">
          Sem histórico ainda
        </div>
      ) : (
        <>
          <div className="h-36">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={rows}
                stackOffset={unit === "PCT" ? "expand" : "none"}
                margin={{ top: 4, right: 4, left: 0, bottom: 0 }}
              >
                <XAxis dataKey="date" hide />
                <YAxis hide />
                <Tooltip
                  contentStyle={{ borderRadius: 10, borderColor: "var(--border)", fontSize: 11 }}
                  labelFormatter={(d) => (typeof d === "string" ? displayMonthSlashYear(d) : d)}
                  formatter={(v, name) => [displayMoney(Number(v)), SERIES.find((s) => s.key === name)?.label ?? name]}
                />
                {SERIES.map((s) => (
                  <Area
                    key={s.key}
                    type="monotone"
                    dataKey={s.key}
                    stackId="1"
                    stroke="none"
                    fill={s.color}
                    fillOpacity={0.9}
                  />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-between font-mono text-[10px] text-faint-foreground">
            <span>{displayShortMonthYear(first.date)}</span>
            <span>{displayShortMonthYear(last.date)}</span>
          </div>
          {/* Como terminou: a fatia de cada classe no último dia */}
          <span className="text-xs font-medium">
            <span className="text-chart-3">{share(last.total_cash)} caixa</span>
            {" · "}
            <span className="text-chart-1">{share(last.total_equity)} RV</span>
            {" · "}
            <span className="text-chart-2">{share(last.total_fixed)} RF</span>
          </span>
        </>
      )}
    </div>
  );
}

/** Jogador × setor: quanto mais escuro, maior a aposta; a diversificação em número e em palavras. */
function SectorExposure({
  players,
  groups,
  naming,
  simulationIds,
  currentPlayerName,
}: {
  players: CompositionPlayer[];
  groups: Groups;
  naming: TeamNaming;
  simulationIds: number[];
  currentPlayerName?: string | undefined;
}) {
  const sectors = [...new Set(players.flatMap((p) => p.sectors.map((s) => s.sector ?? NO_SECTOR)))].sort((a, b) =>
    a === NO_SECTOR ? 1 : b === NO_SECTOR ? -1 : a.localeCompare(b),
  );
  const columns: SortColumns<CompositionPlayer> = {
    player: (p) => playerLabel(p, simulationIds, currentPlayerName),
    diversification: (p) => sortNumber(p.effective_sectors),
  };
  for (const sector of sectors) {
    columns[`sector:${sector}`] = (p) =>
      Number(p.sectors.find((s) => (s.sector ?? NO_SECTOR) === sector)?.fraction ?? 0);
  }
  const sorting = useTableSort(players, columns);

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>Em que setores cada um apostou</CardTitle>
        <CardDescription>
          Fatia da renda variável em cada setor no último dia. Quanto mais escuro, maior a aposta.
        </CardDescription>
      </CardHeader>
      {sectors.length === 0 ? (
        <CardContent>
          <p className="py-6 text-center text-[13px] text-muted-foreground">Ninguém tinha ações no último dia.</p>
        </CardContent>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <SortableTableHead label="Jogador" {...sorting.header("player")} />
              {sectors.map((s) => (
                <SortableTableHead key={s} label={s} numeric {...sorting.header(`sector:${s}`)} />
              ))}
              <SortableTableHead
                label="Diversificação"
                {...sorting.header("diversification")}
                hint={<MetricHint metric={EFFECTIVE_SECTORS} />}
              />
            </TableRow>
          </TableHeader>
          <TableBody>
            {groups.map((group) => (
              <Fragment key={group.team ?? "all"}>
                {group.team !== null && (
                  <TableRow variant="team" style={{ "--team": teamColor(group.team) } as CSSProperties}>
                    <TableCell colSpan={sectors.length + 2}>
                      <TeamBadge team={group.team} naming={naming} form="full" />
                    </TableCell>
                  </TableRow>
                )}
                {sorting.rows
                  .filter((p) => group.players.includes(p))
                  .map((p) => {
                    const label = playerLabel(p, simulationIds, currentPlayerName);
                    const isYou = p.player_nickname === currentPlayerName;
                    const bySector = new Map(p.sectors.map((s) => [s.sector ?? NO_SECTOR, Number(s.fraction)]));
                    const effective = p.effective_sectors !== null ? Number(p.effective_sectors) : null;
                    return (
                      <TableRow
                        key={playerKey(p)}
                        variant={group.team !== null ? "member" : isYou ? "current" : "default"}
                        style={group.team !== null ? ({ "--team": teamColor(group.team) } as CSSProperties) : undefined}
                      >
                        <TableCell>
                          <PlayerCell player={p} label={label} simulationIds={simulationIds} isYou={isYou} />
                        </TableCell>
                        {sectors.map((s) => {
                          const fraction = bySector.get(s);
                          return (
                            <TableCell key={s} numeric>
                              {fraction ? (
                                <span
                                  className="inline-block w-14 rounded px-1.5 py-1 text-center"
                                  style={{
                                    backgroundColor: `color-mix(in oklab, var(--primary) ${Math.round(fraction * 80)}%, transparent)`,
                                    color: fraction > 0.45 ? "var(--primary-foreground)" : undefined,
                                  }}
                                >
                                  {displayPercent(fraction, 0)}
                                </span>
                              ) : (
                                <span className="text-faint-foreground">·</span>
                              )}
                            </TableCell>
                          );
                        })}
                        <TableCell>
                          {effective === null ? (
                            <span className="text-[13px] text-muted-foreground">Sem ações no último dia</span>
                          ) : (
                            <span className="text-[13px]">
                              <b className="font-mono">{displayNumber(effective, 2)}</b> ·{" "}
                              {diversificationWord(effective)}
                            </span>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
              </Fragment>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  );
}

/** Lucro ou prejuízo por setor, em barras para os dois lados e com a mesma escala pra todos. */
function SectorProfit({
  players,
  groups,
  naming,
  simulationIds,
  currentPlayerName,
}: {
  players: CompositionPlayer[];
  groups: Groups;
  naming: TeamNaming;
  simulationIds: number[];
  currentPlayerName?: string | undefined;
}) {
  const scale = Math.max(...players.flatMap((p) => p.sector_profit.map((s) => Math.abs(Number(s.profit)))), 1);

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1">
            De onde veio o resultado em ações
            <MetricHint metric={SECTOR_PROFIT} />
          </span>
        </CardTitle>
        <CardDescription>
          Lucro ou prejuízo por setor, antes do IR. Mesma escala pra todos: barras do mesmo tamanho valem o mesmo.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-5">
          {groups.map((group) => (
            <div key={group.team ?? "all"} className="grid gap-3">
              {group.team !== null && (
                <div
                  className="border-l-[3px] border-(--team) pl-3"
                  style={{ "--team": teamColor(group.team) } as CSSProperties}
                >
                  <TeamBadge team={group.team} naming={naming} form="full" />
                </div>
              )}
              <div className="grid gap-4 md:grid-cols-2">
                {group.players.map((p) => {
                  const total = p.sector_profit.reduce((sum, s) => sum + Number(s.profit), 0);
                  return (
                    <div
                      key={playerKey(p)}
                      className="grid content-start gap-2 rounded-[10px] border border-border p-4"
                    >
                      <div className="flex justify-between">
                        <span className="font-semibold">{playerLabel(p, simulationIds, currentPlayerName)}</span>
                        <span className={total >= 0 ? "font-mono text-success" : "font-mono text-destructive"}>
                          {p.sector_profit.length ? `${total >= 0 ? "+" : ""}${displayMoney(total)}` : "—"}
                        </span>
                      </div>
                      {p.sector_profit.length === 0 ? (
                        <span className="text-[13px] text-muted-foreground">Não negociou ações.</span>
                      ) : (
                        p.sector_profit.map((s) => {
                          const value = Number(s.profit);
                          const width = (Math.abs(value) / scale) * 50;
                          return (
                            <div
                              key={s.sector ?? NO_SECTOR}
                              className="grid grid-cols-[110px_1fr_90px] items-center gap-2 text-xs"
                            >
                              <span className="truncate text-muted-foreground">{s.sector ?? NO_SECTOR}</span>
                              <span className="relative h-2.5">
                                <span className="absolute inset-y-0 left-1/2 w-px bg-input" />
                                <span
                                  className={
                                    value >= 0
                                      ? "absolute inset-y-0 left-1/2 rounded-r bg-success"
                                      : "absolute inset-y-0 right-1/2 rounded-l bg-destructive"
                                  }
                                  style={{ width: `${width}%` }}
                                />
                              </span>
                              <span
                                className={
                                  value >= 0
                                    ? "text-right font-mono text-success"
                                    : "text-right font-mono text-destructive"
                                }
                              >
                                {value >= 0 ? "+" : ""}
                                {displayMoney(value)}
                              </span>
                            </div>
                          );
                        })
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
