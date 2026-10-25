import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber, sortTableRows } from "@/shared/lib/table-sort";
import { Fragment, type CSSProperties } from "react";
import { Info } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { MetricHint } from "@/shared/components/metric-hint";
import { TeamBadge } from "@/shared/components/team-badge";
import { teamColor, teamName } from "@/shared/lib/teams";
import {
  displayMoney,
  displayMoneyCompact,
  displayMonthShort,
  displayMonthSlashYear,
  displayNumber,
  displayShortMonthYear,
} from "@/shared/lib/utils/display";
import type { OperationsPlayer, OperationsReport, TeamNaming } from "@/types";
import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";
import { IMPACT_COST, INCOME_TAX_PAID, MONTHLY_VOLUME, TRADED_VOLUME, TURNOVER } from "../../lib/metrics";
import { playerKey, playerLabel } from "../../lib/player-label";
import { groupByTeam } from "../../lib/teams";
import { PlayerCell, TabStatus, type ReportProps } from "./shared";

type TeamOperations = OperationsReport["teams"][number];

export function OperationsTab({ simulationIds, currentPlayerName, onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("operations", simulationIds, onlyPlayer);
  const sorting = useTableSort(data?.players ?? [], {
    player: (p) => playerLabel(p, simulationIds, currentPlayerName),
    trades: (p) => p.buy_trades + p.sell_trades,
    volume: (p) => sortNumber(p.traded_volume),
    turnover: (p) => sortNumber(p.turnover),
    tax: (p) => sortNumber(p.income_tax_paid),
    impact: (p) => sortNumber(p.impact_cost),
  });
  if (!data)
    return (
      <TabStatus
        simulationIds={simulationIds}
        loading={isLoading}
        title="as Operações"
        error={error}
        onRetry={() => void refetch()}
      />
    );

  const mostTrades = Math.max(...data.players.map((p) => p.buy_trades + p.sell_trades), 1);
  const mostTeamTrades = Math.max(...data.teams.map((t) => t.buy_trades + t.sell_trades), 1);
  const impactOn = data.players.some((p) => p.impact_cost !== null);
  const naming = data.team_naming;
  const groups = groupByTeam(
    sorting.rows,
    sortTableRows(
      data.teams,
      {
        player: (t) => teamName(t.team, data.team_naming),
        trades: (t) => t.buy_trades + t.sell_trades,
        volume: (t) => sortNumber(t.traded_volume),
        turnover: (t) => sortNumber(t.turnover),
        tax: (t) => sortNumber(t.income_tax_paid),
        impact: (t) => sortNumber(t.impact_cost),
      },
      sorting.sort,
    ).map((t) => t.team),
  );
  const teamOf = (team: number | null) => data.teams.find((t) => t.team === team);

  return (
    <div className="grid gap-5">
      <VolumeHeatmap
        players={data.players}
        groups={groups}
        naming={naming}
        teams={data.teams}
        simulationIds={simulationIds}
        currentPlayerName={currentPlayerName}
      />

      <Card className="overflow-hidden">
        <CardHeader>
          <CardTitle>Como cada um operou</CardTitle>
          <CardDescription>
            Giro = volume ÷ patrimônio médio. Não é bom nem ruim: mostra o estilo.
            {data.teams.length > 0 && " Na equipe, volume, IR e negócios são a soma dos membros; o giro é a média."}
          </CardDescription>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <SortableTableHead
                label={data.teams.length > 0 ? "Equipe e membros" : "Jogador"}
                {...sorting.header("player")}
              />
              <SortableTableHead label={"Negócios"} {...sorting.header("trades")} numeric />
              <SortableTableHead
                label={TRADED_VOLUME.label}
                {...sorting.header("volume")}
                numeric
                hint={<MetricHint metric={TRADED_VOLUME} />}
              />
              <SortableTableHead
                label={TURNOVER.label}
                {...sorting.header("turnover")}
                numeric
                hint={<MetricHint metric={TURNOVER} />}
              />
              <SortableTableHead
                label={INCOME_TAX_PAID.label}
                {...sorting.header("tax")}
                numeric
                hint={<MetricHint metric={INCOME_TAX_PAID} />}
              />
              <SortableTableHead
                label={IMPACT_COST.label}
                {...sorting.header("impact")}
                numeric
                hint={<MetricHint metric={IMPACT_COST} />}
              />
            </TableRow>
          </TableHeader>
          <TableBody>
            {groups.map((group) => {
              const team = teamOf(group.team);
              const teamStyle =
                group.team !== null ? ({ "--team": teamColor(group.team) } as CSSProperties) : undefined;
              return (
                <Fragment key={group.team ?? "all"}>
                  {group.team !== null && team && (
                    <TableRow variant="team" style={teamStyle}>
                      <TableCell>
                        <span className="flex items-center gap-2.5">
                          <TeamBadge team={group.team} naming={naming} form="full" />
                          <span className="text-xs font-normal text-muted-foreground">total da equipe</span>
                        </span>
                      </TableCell>
                      <TableCell>
                        <TradesBar buys={team.buy_trades} sells={team.sell_trades} most={mostTeamTrades} />
                      </TableCell>
                      <TableCell numeric>
                        <span className="font-semibold">{displayMoney(team.traded_volume)}</span>
                      </TableCell>
                      <TableCell>
                        <span className="font-mono">{team.turnover !== null ? displayNumber(team.turnover) : "—"}</span>
                      </TableCell>
                      <TableCell numeric>
                        <span className="font-semibold">{displayMoney(team.income_tax_paid)}</span>
                      </TableCell>
                      <TableCell numeric>
                        <ImpactCost value={team.impact_cost} />
                      </TableCell>
                    </TableRow>
                  )}
                  {group.players.map((p: OperationsPlayer) => {
                    const label = playerLabel(p, simulationIds, currentPlayerName);
                    const isYou = p.player_nickname === currentPlayerName;
                    return (
                      <TableRow
                        key={playerKey(p)}
                        variant={group.team !== null ? "member" : isYou ? "current" : "default"}
                        style={teamStyle}
                      >
                        <TableCell>
                          <span className={group.team !== null ? "block pl-5" : undefined}>
                            <PlayerCell player={p} label={label} simulationIds={simulationIds} isYou={isYou} />
                          </span>
                        </TableCell>
                        <TableCell>
                          <TradesBar buys={p.buy_trades} sells={p.sell_trades} most={mostTrades} />
                        </TableCell>
                        <TableCell numeric>{displayMoney(p.traded_volume)}</TableCell>
                        <TableCell>
                          <span className="flex items-center gap-2">
                            <span className="font-mono">{p.turnover !== null ? displayNumber(p.turnover) : "—"}</span>
                            {p.turnover_style && <Badge variant="secondary">{p.turnover_style}</Badge>}
                          </span>
                        </TableCell>
                        <TableCell numeric>{displayMoney(p.income_tax_paid)}</TableCell>
                        <TableCell numeric>
                          <ImpactCost value={p.impact_cost} />
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </Fragment>
              );
            })}
          </TableBody>
        </Table>
        <CardContent>
          <Alert variant="muted">
            <Info />
            <AlertDescription>
              Custo de impacto: quanto as ordens grandes mexeram no preço contra o jogador. Vermelho é custo; verde, o
              impacto jogou a favor. Nesta partida o impacto de preço está <b>{impactOn ? "ligado" : "desligado"}</b>.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}

/** Barra de negócios: compras e vendas, proporcional a quem mais negociou, com no mínimo 20 px. */
function TradesBar({ buys, sells, most }: { buys: number; sells: number; most: number }) {
  const trades = buys + sells;
  return (
    <div className="grid w-44 gap-1">
      <span
        className="flex h-2 gap-0.5 overflow-hidden rounded-full bg-muted"
        style={{ width: trades > 0 ? `max(20px, ${(trades / most) * 100}%)` : "20px" }}
      >
        {trades > 0 && (
          <>
            <span className="bg-success" style={{ width: `${(buys / trades) * 100}%` }} />
            <span className="bg-destructive" style={{ width: `${(sells / trades) * 100}%` }} />
          </>
        )}
      </span>
      <span className="text-xs text-muted-foreground">
        <span className="text-success">{buys} compras</span> · <span className="text-destructive">{sells} vendas</span>
      </span>
    </div>
  );
}

/** Custo de impacto: vermelho é custo, verde o impacto a favor; sem o impacto ligado fica "—". */
function ImpactCost({ value }: { value: string | null }) {
  const impact = value !== null ? Number(value) : null;
  if (impact === null || impact === 0) {
    return <span className="text-faint-foreground">{impact === 0 ? displayMoney(0) : "—"}</span>;
  }
  return (
    <span className={impact > 0 ? "text-destructive" : "text-success"}>
      {impact > 0 ? "+" : ""}
      {displayMoney(impact)}
    </span>
  );
}

/** Quando cada um negociou: jogador × mês, mais escuro é mais dinheiro girando; cinza, mês só segurando. */
function VolumeHeatmap({
  players,
  groups,
  naming,
  teams,
  simulationIds,
  currentPlayerName,
}: {
  players: OperationsPlayer[];
  groups: { team: number | null; players: OperationsPlayer[] }[];
  naming: TeamNaming;
  teams: TeamOperations[];
  simulationIds: number[];
  currentPlayerName?: string;
}) {
  const months = [...new Set(players.flatMap((p) => p.monthly_volume.map((m) => m.month)))].sort();
  const volumeOf = (m: OperationsPlayer["monthly_volume"][number]) => Number(m.bought) + Number(m.sold);
  const max = Math.max(...players.flatMap((p) => p.monthly_volume.map(volumeOf)), 1);
  // O ano aparece só no primeiro mês e na virada
  const monthLabel = (month: string, i: number) =>
    i === 0 || month.slice(0, 4) !== months[i - 1].slice(0, 4)
      ? displayShortMonthYear(month)
      : displayMonthShort(month);

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1">
            Quando cada um negociou
            <MetricHint metric={MONTHLY_VOLUME} />
          </span>
        </CardTitle>
        <CardDescription>
          {teams.length > 0
            ? "Volume de compras + vendas por mês, agrupado por equipe e na cor dela: mais escuro, mais dinheiro girando. Passando o mouse, o valor exato."
            : "Volume de compras + vendas de ações por mês. Mais escuro, mais dinheiro girando; cinza, mês só segurando."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {months.length === 0 ? (
          <p className="py-6 text-center text-[13px] text-muted-foreground">Ninguém negociou ações ainda.</p>
        ) : (
          <div className="overflow-x-auto">
            <div
              className="grid gap-1"
              style={{ gridTemplateColumns: `180px repeat(${months.length}, minmax(28px, 56px)) 96px` }}
            >
              <span />
              {months.map((m, i) => (
                <span key={m} className="text-center font-mono text-[10px] whitespace-nowrap text-faint-foreground">
                  {months.length <= 12 || i % 3 === 0 ? monthLabel(m, i) : ""}
                </span>
              ))}
              <span className="text-right text-[11px] font-medium text-muted-foreground">Total</span>
              {groups.map((group) => (
                <Fragment key={group.team ?? "all"}>
                  {group.team !== null && (
                    <span
                      className="col-span-full mt-2 flex items-center gap-2.5 border-l-[3px] border-(--team) pl-3 text-xs text-muted-foreground"
                      style={{ "--team": teamColor(group.team) } as CSSProperties}
                    >
                      <TeamBadge team={group.team} naming={naming} form="full" />
                      total da equipe{" "}
                      <b className="font-mono text-foreground">
                        {displayMoneyCompact(
                          teams
                            .find((t) => t.team === group.team)
                            ?.monthly_volume.reduce((sum, m) => sum + volumeOf(m), 0) ?? 0,
                        )}
                      </b>
                    </span>
                  )}
                  {group.players.map((p) => {
                    const byMonth = new Map(p.monthly_volume.map((m) => [m.month, m]));
                    const label = playerLabel(p, simulationIds, currentPlayerName);
                    const total = p.monthly_volume.reduce((sum, m) => sum + volumeOf(m), 0);
                    const heat = group.team !== null ? teamColor(group.team) : "var(--primary)";
                    return (
                      <div key={playerKey(p)} className="contents">
                        <span className="min-w-0 self-center text-[13px]">
                          <PlayerCell
                            player={p}
                            label={label}
                            simulationIds={simulationIds}
                            isYou={p.player_nickname === currentPlayerName}
                          />
                        </span>
                        {months.map((month) => {
                          const entry = byMonth.get(month);
                          const volume = entry ? volumeOf(entry) : 0;
                          return (
                            <Tooltip key={month}>
                              <TooltipTrigger render={<span />}>
                                <span
                                  className="flex h-7 items-center justify-center rounded text-[11px] text-faint-foreground"
                                  style={{
                                    backgroundColor: volume
                                      ? `color-mix(in oklab, ${heat} ${Math.round(15 + (volume / max) * 85)}%, transparent)`
                                      : "var(--muted)",
                                  }}
                                >
                                  {volume ? "" : "—"}
                                </span>
                              </TooltipTrigger>
                              <TooltipContent>
                                {label}
                                {group.team !== null && ` · ${teamName(group.team, naming)}`} ·{" "}
                                {displayMonthSlashYear(month)}
                                <br />
                                {entry && volume
                                  ? `${displayMoney(volume)} · ${entry.buy_count} compras, ${entry.sell_count} vendas`
                                  : "Sem negócios"}
                              </TooltipContent>
                            </Tooltip>
                          );
                        })}
                        <span className="self-center text-right font-mono text-xs">
                          {total ? displayMoneyCompact(total) : "—"}
                        </span>
                      </div>
                    );
                  })}
                </Fragment>
              ))}
            </div>
            <div className="mt-3 flex items-center gap-2 text-[11px] text-faint-foreground">
              R$ 0
              <span className="h-2 w-24 rounded-full bg-linear-to-r from-primary/15 to-primary" />
              {displayMoneyCompact(max)} por mês
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
