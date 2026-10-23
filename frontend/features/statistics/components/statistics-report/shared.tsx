import { Fragment, type CSSProperties, type ReactNode } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { TeamBadge } from "@/shared/components/team-badge";
import { MetricHint } from "@/shared/components/metric-hint";
import { teamColor, teamName } from "@/shared/lib/teams";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { sortNumber, sortTableRows, type SortColumns } from "@/shared/lib/table-sort";
import type ApiError from "@/shared/lib/models/ApiError";
import { useSimulationList } from "@/shared/hooks/queries/useSimulationList";
import type { MetricInfo } from "@/shared/lib/metric-info";
import type { PlayerRef, TeamNaming } from "@/types";
import { displayMetric } from "../../lib/metrics";
import { playerKey, playerLabel } from "../../lib/player-label";
import { BotIdentity } from "./bot-identity";

export interface ReportProps {
  simulationIds: number[];
  currentPlayerName?: string;
  /** Mostra só as linhas deste jogador */
  onlyPlayer?: string;
}

/** Aba sem dados: esqueleto enquanto carrega; com erro, só ela falha e oferece tentar de novo. */
export function TabStatus({
  loading,
  title,
  error,
  onRetry,
  simulationIds,
}: {
  loading: boolean;
  title: string;
  error?: ApiError | null;
  onRetry?: () => void;
  /** Com a partida em equipes, o esqueleto tem o formato equipe → membros */
  simulationIds?: number[];
}) {
  const { data: simulations } = useSimulationList();
  const inTeams =
    simulationIds?.length === 1 && simulations?.find((s) => s.id === simulationIds[0])?.player_grouping === "TEAMS";

  if (loading && inTeams) return <TeamsSkeleton />;
  if (loading) {
    return (
      <div className="grid gap-5">
        <Skeleton className="h-32" />
        <Skeleton className="h-72" />
      </div>
    );
  }
  return (
    <Card>
      <CardContent>
        <ErrorState
          title={`Não deu pra carregar ${title}`}
          description="As outras abas continuam funcionando."
          error={error}
          onRetry={onRetry}
        />
      </CardContent>
    </Card>
  );
}

/** Esqueleto no formato do ranking por equipe: a linha da equipe e os membros abaixo dela. */
function TeamsSkeleton() {
  return (
    <Card aria-busy="true">
      <CardContent>
        <div className="grid gap-2">
          {[2, 3].map((members) => (
            <div key={members} className="grid gap-2">
              <Skeleton className="h-10" />
              {Array.from({ length: members }, (_, i) => (
                <Skeleton key={i} className="ml-7 h-8" />
              ))}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/** Card de gráfico com o nome da métrica, a dica e a descrição curta. */
export function ChartCard({
  metric,
  description,
  action,
  children,
}: {
  metric: MetricInfo;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1">
            {metric.label}
            <MetricHint metric={metric} />
          </span>
        </CardTitle>
        <CardDescription>{description ?? metric.description}</CardDescription>
        {action && <CardAction>{action}</CardAction>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

/**
 * Avatar do jogador, o nome e a marca de quem está vendo. Comparando simulações o
 * avatar fica neutro: a cor ali é da partida, e a sigla continua a do apelido.
 */
export function PlayerCell({
  player,
  label,
  simulationIds,
  isYou,
  teamNaming,
  delinquent = false,
  onOpenBotLog,
}: {
  player: PlayerRef;
  label: string;
  simulationIds: number[];
  isYou: boolean;
  /** Informado, o selo curto da equipe aparece ao lado do nome (partida em equipes) */
  teamNaming?: TeamNaming;
  /** Parcela de crédito em atraso: o selo "Negativado" aparece ao lado do nome */
  delinquent?: boolean;
  /** Abre o log das ordens do bot; sem ele, o cartão do bot só informa */
  onOpenBotLog?: (bot: PlayerRef) => void;
}) {
  if (player.is_bot) {
    return <BotIdentity player={player} label={label} simulationIds={simulationIds} onOpenLog={onOpenBotLog} />;
  }
  return (
    <span className="flex items-center gap-2">
      <PlayerAvatar
        nickname={player.player_nickname}
        color={simulationIds.length > 1 ? undefined : player.color}
        size="sm"
      />
      <span className="max-w-56 truncate" title={label}>
        {label}
      </span>
      {/* Entre partidas o nome já diz "Você · A" */}
      {isYou && !label.startsWith("Você") && (
        <Badge variant="info" size="sm">
          você
        </Badge>
      )}
      {teamNaming && player.team && <TeamBadge team={player.team} naming={teamNaming} size="sm" />}
      {delinquent && (
        <Badge variant="destructive" size="tag">
          Negativado
        </Badge>
      )}
    </span>
  );
}

/** Escolhe um jogador quando o card mostra um por vez; com um jogador só, some. */
export function PlayerToggle({
  labels,
  current,
  onSelect,
  colorOf,
}: {
  labels: string[];
  current: string | undefined;
  onSelect: (label: string) => void;
  colorOf: (label: string) => string;
}) {
  if (labels.length < 2) return null;
  return (
    <ToggleGroup
      variant="segmented"
      aria-label="Jogador"
      value={current ? [current] : []}
      onValueChange={(values) => values[0] && onSelect(values[0])}
    >
      {labels.map((label) => (
        <ToggleGroupItem key={label} value={label}>
          <span
            className="size-2 shrink-0 rounded-full"
            style={{ backgroundColor: colorOf(label) }}
            aria-hidden="true"
          />
          {label}
        </ToggleGroupItem>
      ))}
    </ToggleGroup>
  );
}

export interface MetricColumn<T, G = never> {
  metric: MetricInfo;
  value: (row: T) => string | number | null | undefined;
  /** Destaca o melhor da sala: o maior ou o menor valor da coluna */
  best?: "max" | "min";
  tone?: (row: T) => "positive" | "negative" | undefined;
  /** Célula própria no lugar do valor formatado (ex.: os meses em quadradinhos) */
  cell?: (row: T) => ReactNode;
  /** Valor da equipe nesta coluna, quando a tabela agrupa por equipe */
  teamValue?: (team: G) => string | number | null | undefined;
  /** Célula própria da equipe no lugar do valor formatado */
  teamCell?: (team: G, members: T[]) => ReactNode;
}

/** Equipes de uma tabela agrupada: uma linha por equipe com os membros logo abaixo. */
export interface TeamGroups<G> {
  naming: TeamNaming;
  teams: G[];
  /** O que a linha da equipe diz ao lado do nome, quando não é a média (ex.: "total da equipe") */
  note?: (team: G) => string;
}

interface MetricsTableProps<T extends PlayerRef, G extends { team: number } = never> {
  title: string;
  description?: string;
  rows: T[];
  columns: MetricColumn<T, G>[];
  simulationIds: number[];
  currentPlayerName?: string;
  extraColumn?: { header: ReactNode; cell: (row: T) => ReactNode; teamCell?: (team: G, members: T[]) => ReactNode };
  footer?: ReactNode;
  /** Partida em equipes: as linhas se agrupam por equipe, com a da equipe no topo de cada grupo */
  groups?: TeamGroups<G>;
}

/** Uma linha por jogador e uma coluna por métrica, cada uma com a sua dica; o melhor da sala em verde. */
export function MetricsTable<T extends PlayerRef, G extends { team: number } = never>({
  title,
  description,
  rows,
  columns,
  simulationIds,
  currentPlayerName,
  extraColumn,
  footer,
  groups,
}: MetricsTableProps<T, G>) {
  const playerColumns: SortColumns<T> = {
    player: r => playerLabel(r, simulationIds, currentPlayerName),
    ...Object.fromEntries(columns.map(c => [c.metric.label, (r: T) => sortNumber(c.value(r))])),
  };
  const sorting = useTableSort(rows, playerColumns);
  const teamColumns: SortColumns<G> = {
    player: t => groups ? teamName(t.team, groups.naming) : String(t.team),
    ...Object.fromEntries(columns.map(c => [c.metric.label, (t: G) => sortNumber(c.teamValue?.(t))])),
  };
  const teams = sortTableRows(groups?.teams ?? [], teamColumns, sorting.sort);
  const bestOf = columns.map((column) => {
    if (!column.best || rows.length < 2) return null;
    const values = rows
      .map((r) => column.value(r))
      .filter((v) => v !== null && v !== undefined)
      .map(Number);
    if (!values.length) return null;
    return column.best === "max" ? Math.max(...values) : Math.min(...values);
  });

  const renderRow = (row: T, member: boolean) => {
    const label = playerLabel(row, simulationIds, currentPlayerName);
    const isYou = row.player_nickname === currentPlayerName;
    return (
      <TableRow
        key={playerKey(row)}
        variant={member ? "member" : isYou ? "current" : "default"}
        style={member && row.team ? ({ "--team": teamColor(row.team) } as CSSProperties) : undefined}
      >
        <TableCell>
          {member ? (
            <span className="block pl-5">
              <PlayerCell player={row} label={label} simulationIds={simulationIds} isYou={isYou} />
            </span>
          ) : (
            <PlayerCell player={row} label={label} simulationIds={simulationIds} isYou={isYou} />
          )}
        </TableCell>
        {extraColumn && <TableCell>{extraColumn.cell(row)}</TableCell>}
        {columns.map((column, i) => {
          const value = column.value(row);
          const best = bestOf[i] !== null && value !== null && value !== undefined && Number(value) === bestOf[i];
          const tone = column.tone?.(row);
          return (
            <TableCell key={column.metric.label} numeric>
              {column.cell ? (
                column.cell(row)
              ) : best ? (
                <Badge variant="success">{displayMetric(column.metric, value)}</Badge>
              ) : (
                <span
                  className={tone === "negative" ? "text-destructive" : tone === "positive" ? "text-success" : undefined}
                >
                  {displayMetric(column.metric, value)}
                </span>
              )}
            </TableCell>
          );
        })}
      </TableRow>
    );
  };

  const renderTeam = (team: G, naming: TeamNaming, note: string | undefined) => {
    const members = sorting.rows.filter((r) => r.team === team.team);
    return (
      <Fragment key={`team-${team.team}`}>
        <TableRow variant="team" style={{ "--team": teamColor(team.team) } as CSSProperties}>
          <TableCell>
            <span className="flex items-center gap-2.5">
              <TeamBadge team={team.team} naming={naming} form="full" />
              <span className="flex -space-x-1.5">
                {members.map((m) => (
                  <PlayerAvatar key={m.player_nickname} nickname={m.player_nickname} color={m.color} bot={m.is_bot} size="sm" />
                ))}
              </span>
              {note && <span className="text-xs font-normal text-muted-foreground">{note}</span>}
            </span>
          </TableCell>
          {extraColumn && <TableCell>{extraColumn.teamCell?.(team, members)}</TableCell>}
          {columns.map((column) => (
            <TableCell key={column.metric.label} numeric>
              {column.teamCell ? (
                column.teamCell(team, members)
              ) : (
                <span className="font-semibold">{displayMetric(column.metric, column.teamValue?.(team))}</span>
              )}
            </TableCell>
          ))}
        </TableRow>
        {members.map((m) => renderRow(m, true))}
      </Fragment>
    );
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <SortableTableHead {...sorting.header("player")} label={groups ? "Equipe e membros" : "Jogador"} />
            {extraColumn && <TableHead>{extraColumn.header}</TableHead>}
            {columns.map((column) => (
              <SortableTableHead key={column.metric.label} {...sorting.header(column.metric.label)} label={column.metric.label}
                numeric hint={<MetricHint metric={column.metric} />} />
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.length === 0 && (
            <TableEmptyRow colSpan={columns.length + (extraColumn ? 2 : 1)}>
              <span className="text-[13px] text-muted-foreground">Sem jogadores com patrimônio ainda.</span>
            </TableEmptyRow>
          )}
          {groups
            ? teams.map((team) => renderTeam(team, groups.naming, groups.note?.(team)))
            : sorting.rows.map((row) => renderRow(row, false))}
          {footer}
        </TableBody>
      </Table>
    </Card>
  );
}
