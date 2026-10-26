import { Info, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { MetricHint } from "@/shared/components/metric-hint";
import { ParamPills } from "@/shared/components/param-pills";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { PlayerLineChart, type LineSeries } from "@/shared/components/player-line-chart";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useBacktestResult } from "@/shared/hooks/queries/useBacktestResult";
import { useBotStrategies } from "@/shared/hooks/queries/useBotStrategies";
import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";
import { referenceSeries } from "@/shared/lib/backtest-chart-series";
import { playerColorStyle } from "@/shared/lib/player-colors";
import { cn } from "@/shared/lib/utils";
import {
  displayDate,
  displayMoney,
  displayMoneyCompact,
  displayNumber,
  displayPercent,
  displayPercentagePoints,
  displaySignedMoney,
  displaySignedPercent,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { BacktestResult, StrategyInfo } from "@/types";
import {
  backtestRows,
  defaultMeasure,
  finalReferences,
  rankRows,
  type BacktestMeasure,
  type BacktestReferences,
  type BacktestRow,
} from "../../lib/backtest-result";
import { BACKTEST_OVER_CDI, BACKTEST_RETURN, SCORE } from "../../lib/metrics";
import { TabStatus, type ReportProps } from "../statistics-report/shared";

const tone = (value: number) => (value > 0 ? "text-success" : value < 0 ? "text-destructive" : undefined);

/** O Geral de um backtest: quem venceu, o patrimônio de cada estratégia contra o CDI e o Ibovespa, e a tabela com os parâmetros. */
export function BacktestOverviewTab({ simulationIds }: ReportProps) {
  const simulationId = simulationIds[0];
  const { data: overview, isLoading, error, refetch } = useStatisticsReport("overview", simulationIds);
  const { data: result, error: resultError, refetch: refetchResult } = useBacktestResult(simulationId);
  const {
    data: strategies,
    error: strategiesError,
    refetch: refetchStrategies,
  } = useBotStrategies(result?.config.start_date);

  if (!overview || !result || !strategies) {
    const failure = error ?? resultError ?? strategiesError;
    return (
      <TabStatus
        simulationIds={simulationIds}
        loading={isLoading || !failure}
        title="o Geral"
        error={failure}
        onRetry={() => void Promise.all([refetch(), refetchResult(), refetchStrategies()])}
      />
    );
  }

  const references = finalReferences(result);
  if (!references) {
    return (
      <Alert variant="info">
        <Info />
        <AlertTitle>Esse backtest parou antes do primeiro pregão</AlertTitle>
        <AlertDescription>Não há números para mostrar. Rode de novo para gerar um resultado.</AlertDescription>
      </Alert>
    );
  }

  const rows = backtestRows(overview.players, result, references);
  return (
    <Loaded simulationIds={simulationIds} result={result} references={references} rows={rows} strategies={strategies} />
  );
}

type LoadedProps = {
  simulationIds: number[];
  result: BacktestResult;
  references: BacktestReferences;
  rows: BacktestRow[];
  strategies: StrategyInfo[];
};

function Loaded({ simulationIds, result, references, rows, strategies }: LoadedProps) {
  const [measure, setMeasure] = useState<BacktestMeasure>(() => defaultMeasure(rows));
  const ranked = rankRows(rows, measure);
  const leader = rankRows(rows, defaultMeasure(rows))[0];
  const beatCdi = rows.filter((row) => row.overCdi > 0).length;
  const lastDay = result.stopped_on ?? result.config.end_date;

  return (
    <div className="grid gap-5">
      {!result.finished && (
        <Alert variant="info">
          <Info />
          <AlertTitle>Os números valem até {displayDate(parseLocalDate(lastDay))}</AlertTitle>
          <AlertDescription>
            Rodar de novo começa do início, com a mesma configuração. Para ver o resto, mude o fim ou deixe rodar até o
            final.
          </AlertDescription>
        </Alert>
      )}
      {beatCdi === 0 && (
        <Alert variant="muted">
          <Info />
          <AlertTitle>Nenhuma estratégia bateu o CDI</AlertTitle>
          <AlertDescription>
            Comum no Brasil: com juro alto, deixar o dinheiro no CDI é difícil de vencer. Tente outro período ou outras
            estratégias.
          </AlertDescription>
        </Alert>
      )}

      {leader && (
        <Summary rows={rows} leader={leader} references={references} beatCdi={beatCdi} strategies={strategies} />
      )}
      <EquityChart simulationIds={simulationIds} result={result} rows={rows} />
      <RankingTable
        rows={ranked}
        references={references}
        strategies={strategies}
        measure={measure}
        onMeasureChange={setMeasure}
        contributed={references.contributed}
      />
    </div>
  );
}

type SummaryProps = {
  rows: BacktestRow[];
  leader: BacktestRow;
  references: BacktestReferences;
  beatCdi: number;
  strategies: StrategyInfo[];
};

/** O topo: quem venceu e quanto terminou a frente do CDI e do Ibovespa. */
function Summary({ rows, leader, references, beatCdi, strategies }: SummaryProps) {
  const single = rows.length === 1;
  const strategyName = strategies.find((s) => s.key === leader.participant.strategy_key)?.name;
  const byScore = leader.score !== null;
  const overCdi = leader.networth - references.cdi.networth;
  const overIbov = references.ibov ? leader.networth - references.ibov.networth : null;
  const overIbovPoints = references.ibov ? leader.returnOnContributed - references.ibov.returnOnContributed : null;

  const kpis = [
    {
      label: "Patrimônio final",
      value: displayMoney(leader.networth),
      detail: `${displayMoney(references.contributed)} aportados`,
      toneValue: 0,
    },
    {
      label: "Contra o CDI",
      value: displaySignedMoney(overCdi),
      detail: `${displayPercentagePoints(leader.overCdi, 1)} de retorno`,
      toneValue: overCdi,
    },
    ...(overIbov !== null && overIbovPoints !== null
      ? [
          {
            label: "Contra o Ibovespa",
            value: displaySignedMoney(overIbov),
            detail: `${displayPercentagePoints(overIbovPoints, 1)} de retorno`,
            toneValue: overIbov,
          },
        ]
      : []),
    ...(single
      ? []
      : [
          {
            label: "Bateram o CDI",
            value: `${beatCdi} de ${rows.length} · ${displayPercent(beatCdi / rows.length, 0)}`,
            detail: beatCdi === 1 ? "só a vencedora" : beatCdi === 0 ? "nenhuma" : "quem terminou à frente",
            toneValue: 0,
          },
        ]),
  ];

  return (
    <Card>
      <CardContent>
        <div className="grid items-center gap-5 lg:grid-cols-[minmax(0,1.3fr)_repeat(4,minmax(0,1fr))]">
          {/* Vencedora */}
          <div className="flex items-center gap-4">
            <PlayerAvatar nickname={leader.participant.nickname} color={leader.participant.color} bot size="lg" />
            <div className="grid min-w-0 gap-1">
              <span className="text-xs font-semibold text-muted-foreground">
                {single ? "Contra as referências" : byScore ? "Venceu pela Nota geral" : "Na frente pelo patrimônio"}
              </span>
              <span className="truncate text-xl font-bold" title={leader.participant.nickname}>
                {leader.participant.nickname}
              </span>
              <span className="truncate text-[13px] text-muted-foreground">
                {strategyName}
                {byScore && (
                  <>
                    {" "}
                    · nota <b className="font-mono text-foreground">{displayNumber(leader.score ?? 0, 0)}</b>
                  </>
                )}
              </span>
            </div>
          </div>

          {/* Números */}
          {kpis.map((kpi) => (
            <div key={kpi.label} className="grid gap-0.5 border-l border-border pl-4">
              <span className="text-xs text-muted-foreground">{kpi.label}</span>
              <span className={cn("font-mono text-xl font-semibold", tone(kpi.toneValue))}>{kpi.value}</span>
              <span className="text-xs text-muted-foreground">{kpi.detail}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

type EquityChartProps = {
  simulationIds: number[];
  result: BacktestResult;
  rows: BacktestRow[];
};

/** O patrimônio de cada estratégia pregão a pregão, com o CDI, o Ibovespa e o total aportado. */
function EquityChart({ simulationIds, result, rows }: EquityChartProps) {
  const { data: returns, isLoading } = useStatisticsReport("returns", simulationIds);

  const strategies: LineSeries[] = rows.map((row) => ({
    key: row.participant.nickname,
    label: row.participant.nickname,
    color: playerColorStyle(row.participant.color).background,
    emphasis: true,
    points: returns?.players.find((p) => p.player_nickname === row.participant.nickname)?.networth ?? [],
  }));
  const series = [...strategies, ...referenceSeries(result.references)];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Patrimônio de cada estratégia</CardTitle>
        <CardDescription>
          Acima da linha cinza, a estratégia ganhou dinheiro; acima da tracejada, ganhou do CDI.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading || !returns ? (
          <Skeleton className="h-85" />
        ) : (
          <PlayerLineChart
            key={series.map((s) => s.key).join("|")}
            series={series}
            format={displayMoney}
            axisFormat={displayMoneyCompact}
          />
        )}
      </CardContent>
    </Card>
  );
}

const MEASURES: { value: BacktestMeasure; label: string }[] = [
  { value: "SCORE", label: "Nota" },
  { value: "RETURN", label: "Retorno" },
  { value: "NETWORTH", label: "Patrimônio" },
];

type RankingTableProps = {
  rows: BacktestRow[];
  references: BacktestReferences;
  strategies: StrategyInfo[];
  measure: BacktestMeasure;
  onMeasureChange: (measure: BacktestMeasure) => void;
  contributed: number;
};

/** A tabela: uma linha por estratégia, com os parâmetros usados, e as referências no fim, sem posição. */
function RankingTable({ rows, references, strategies, measure, onMeasureChange, contributed }: RankingTableProps) {
  const single = rows.length === 1;
  const strategyOf = (key: string) => strategies.find((s) => s.key === key);
  const ibovOverCdi = references.ibov ? references.ibov.returnOnContributed - references.cdi.returnOnContributed : null;

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>{single ? "A estratégia e as referências" : "Ranking das estratégias"}</CardTitle>
        <CardDescription>
          Retorno sobre o que foi aportado ({displayMoney(contributed)}). “Contra o CDI” é a diferença de retorno, em
          pontos percentuais.
        </CardDescription>
        {!single && (
          <CardAction>
            <ToggleGroup
              variant="segmented"
              aria-label="Ordenar por"
              value={[measure]}
              onValueChange={(values) => values[0] && onMeasureChange(values[0] as BacktestMeasure)}
            >
              {MEASURES.map((m) => (
                <ToggleGroupItem key={m.value} value={m.value}>
                  {m.label}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
          </CardAction>
        )}
      </CardHeader>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>#</TableHead>
            <TableHead>Estratégia</TableHead>
            <TableHead>Parâmetros</TableHead>
            <TableHead numeric>
              <span className="inline-flex items-center gap-1">
                Nota
                <MetricHint metric={SCORE} />
              </span>
            </TableHead>
            <TableHead numeric>Patrimônio</TableHead>
            <TableHead numeric>
              <span className="inline-flex items-center gap-1">
                Retorno
                <MetricHint metric={BACKTEST_RETURN} />
              </span>
            </TableHead>
            <TableHead numeric>
              <span className="inline-flex items-center gap-1">
                Contra o CDI
                <MetricHint metric={BACKTEST_OVER_CDI} />
              </span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, index) => {
            const strategy = strategyOf(row.participant.strategy_key);
            return (
              <TableRow key={row.participant.nickname} variant={index === 0 && !single ? "current" : "default"}>
                <TableCell>
                  <span className="font-mono text-muted-foreground">{single ? "" : index + 1}</span>
                </TableCell>
                <TableCell>
                  <span className="flex items-center gap-2.5">
                    <PlayerAvatar nickname={row.participant.nickname} color={row.participant.color} bot size="sm" />
                    <span className="grid min-w-0">
                      <span className="flex items-center gap-1.5">
                        <span className="max-w-56 truncate font-semibold" title={row.participant.nickname}>
                          {row.participant.nickname}
                        </span>
                        {row.failedOn && (
                          <Badge variant="destructive" size="tag">
                            <TriangleAlert />
                            parou em {displayDate(parseLocalDate(row.failedOn))}
                          </Badge>
                        )}
                      </span>
                      <span className="truncate text-xs text-muted-foreground">
                        {strategy?.name ?? row.participant.strategy_key}
                      </span>
                    </span>
                  </span>
                </TableCell>
                <TableCell className="whitespace-normal">
                  {strategy && <ParamPills strategy={strategy} values={row.participant.params ?? {}} />}
                </TableCell>
                <TableCell numeric>{row.score === null ? "—" : displayNumber(row.score, 0)}</TableCell>
                <TableCell numeric>{displayMoney(row.networth)}</TableCell>
                <TableCell numeric>
                  <span className={tone(row.returnOnContributed)}>
                    {displaySignedPercent(row.returnOnContributed, 1)}
                  </span>
                </TableCell>
                <TableCell numeric>
                  <span className={tone(row.overCdi)}>{displayPercentagePoints(row.overCdi, 1)}</span>
                </TableCell>
              </TableRow>
            );
          })}

          {/* Referências, sem posição */}
          <ReferenceRow name="CDI" dash="dashed" reference={references.cdi} overCdi={null} />
          {references.ibov && ibovOverCdi !== null && (
            <ReferenceRow name="Ibovespa" dash="dotted" reference={references.ibov} overCdi={ibovOverCdi} />
          )}
        </TableBody>
      </Table>
    </Card>
  );
}

type ReferenceRowProps = {
  name: string;
  dash: "dashed" | "dotted";
  reference: BacktestReferences["cdi"];
  overCdi: number | null;
};

function ReferenceRow({ name, dash, reference, overCdi }: ReferenceRowProps) {
  return (
    <TableRow variant="subtle">
      <TableCell />
      <TableCell>
        <span className="flex items-center gap-2.5">
          <span className="flex w-8 justify-center" aria-hidden="true">
            <span
              className={cn(
                "w-[18px] border-t-2",
                dash === "dashed" ? "border-dashed border-foreground" : "border-dotted border-faint-foreground",
              )}
            />
          </span>
          <span className="grid">
            <span className="font-medium">{name}</span>
            <span className="text-xs text-muted-foreground">referência, com os mesmos aportes</span>
          </span>
        </span>
      </TableCell>
      <TableCell>
        <span className="text-xs text-muted-foreground">—</span>
      </TableCell>
      <TableCell numeric>
        <span className="text-muted-foreground">—</span>
      </TableCell>
      <TableCell numeric>{displayMoney(reference.networth)}</TableCell>
      <TableCell numeric>
        <span className={tone(reference.returnOnContributed)}>
          {displaySignedPercent(reference.returnOnContributed, 1)}
        </span>
      </TableCell>
      <TableCell numeric>
        <span className={overCdi === null ? "text-muted-foreground" : tone(overCdi)}>
          {overCdi === null ? "—" : displayPercentagePoints(overCdi, 1)}
        </span>
      </TableCell>
    </TableRow>
  );
}
