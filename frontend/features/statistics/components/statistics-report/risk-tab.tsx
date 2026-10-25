import { useState } from "react";
import {
  CartesianGrid,
  LabelList,
  ReferenceArea,
  ResponsiveContainer,
  ReferenceLine,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayList, displayNumber, displayPercent } from "@/shared/lib/utils/display";
import { teamColor, teamName, teamShortName } from "@/shared/lib/teams";
import type { RiskPlayer, RiskReport, TeamNaming } from "@/types";
import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";
import { playerLabel, youLabel, labelColors } from "../../lib/player-label";
import {
  ANNUAL_VOLATILITY,
  DRAWDOWN,
  MAX_DRAWDOWN,
  ROLLING_VOLATILITY,
  SAMPLE_DAYS,
  SHARPE_RATIO,
  SORTINO_RATIO,
  TIME_UNDERWATER,
  WORST_MONTH,
} from "../../lib/metrics";
import { DebtTable } from "./debt-table";
import { PlayerLineChart, type LineSeries } from "@/shared/components/player-line-chart";
import { ChartCard, MetricsTable, TabStatus, type ReportProps } from "./shared";

type TeamRisk = RiskReport["teams"][number];
type View = "DRAWDOWN" | "VOLATILITY";

// A dispersão precisa de alguns pregões para a oscilação existir
const MIN_SCATTER_DAYS = 3;

export function RiskTab({ simulationIds, currentPlayerName, onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("risk", simulationIds, onlyPlayer);
  const { data: returns } = useStatisticsReport("returns", simulationIds);
  const [view, setView] = useState<View>("DRAWDOWN");
  if (!data)
    return (
      <TabStatus
        simulationIds={simulationIds}
        loading={isLoading}
        title="o Risco"
        error={error}
        onRetry={() => void refetch()}
      />
    );

  const labels = data.players.map((p) => playerLabel(p, simulationIds, currentPlayerName));
  const someoneIsYou = data.players.some((p) => p.player_nickname === currentPlayerName);
  const colorOf = labelColors(data.players, simulationIds, currentPlayerName);
  const cdiReturn = returns?.benchmarks.find((b) => b.series === "CDI")?.annual_return ?? null;

  // Distância do pico: a sua linha ganha área e as dos outros ficam de fundo
  const lines: LineSeries[] = data.players.map((p) => {
    const label = playerLabel(p, simulationIds, currentPlayerName);
    const you = p.player_nickname === currentPlayerName;
    return {
      key: label,
      label: youLabel(label, you),
      color: colorOf(label),
      points: view === "DRAWDOWN" ? p.drawdown : p.rolling_volatility,
      emphasis: you,
      area: view === "DRAWDOWN" && you,
      muted: view === "DRAWDOWN" && someoneIsYou && !you,
    };
  });

  return (
    <div className="grid gap-5">
      <RiskReturn
        players={data.players}
        teams={data.teams}
        naming={data.team_naming}
        cdiReturn={cdiReturn}
        currentPlayerName={currentPlayerName}
        simulationIds={simulationIds}
        colorOf={colorOf}
      />

      <ChartCard
        metric={view === "DRAWDOWN" ? DRAWDOWN : ROLLING_VOLATILITY}
        action={
          <ToggleGroup
            variant="segmented"
            aria-label="Série do gráfico"
            value={[view]}
            onValueChange={(values) => values[0] && setView(values[0] as View)}
          >
            <ToggleGroupItem value="DRAWDOWN">Distância do pico</ToggleGroupItem>
            <ToggleGroupItem value="VOLATILITY">Volatilidade · {data.rolling_window} pregões</ToggleGroupItem>
          </ToggleGroup>
        }
      >
        <PlayerLineChart
          key={`${view}|${labels.join("|")}`}
          series={lines}
          format={(v) => displayPercent(v)}
          axisFormat={(v) => displayPercent(v, 0)}
        />
      </ChartCard>

      <MetricsTable
        title={data.teams.length > 0 ? "Risco por equipe" : "Risco por jogador"}
        description={
          data.teams.length > 0
            ? "A linha da equipe é a média simples dos membros em cada métrica. Verde = melhor jogador da sala."
            : "Verde = melhor da sala em cada métrica. Com menos de ~63 pregões, leia com cautela."
        }
        groups={data.teams.length > 0 ? { naming: data.team_naming, teams: data.teams } : undefined}
        rows={data.players}
        simulationIds={simulationIds}
        currentPlayerName={currentPlayerName}
        columns={[
          { metric: MAX_DRAWDOWN, value: (r) => r.max_drawdown, teamValue: (t) => t.max_drawdown, best: "min" },
          {
            metric: ANNUAL_VOLATILITY,
            value: (r) => r.annual_volatility,
            teamValue: (t) => t.annual_volatility,
            best: "min",
          },
          { metric: SHARPE_RATIO, value: (r) => r.sharpe_ratio, teamValue: (t) => t.sharpe_ratio, best: "max" },
          { metric: SORTINO_RATIO, value: (r) => r.sortino_ratio, teamValue: (t) => t.sortino_ratio, best: "max" },
          {
            metric: TIME_UNDERWATER,
            value: (r) => r.time_underwater,
            teamValue: (t) => (t.time_underwater === null ? null : Math.round(Number(t.time_underwater))),
            best: "min",
          },
          { metric: WORST_MONTH, value: (r) => r.worst_month, teamValue: (t) => t.worst_month, best: "max" },
          { metric: SAMPLE_DAYS, value: (r) => r.days },
        ]}
      />

      {/* Dívida e nota de crédito de cada um */}
      {data.players.some((p) => Number(p.debt) > 0 || p.credit_grade !== "AAA") && (
        <DebtTable players={data.players} simulationIds={simulationIds} currentPlayerName={currentPlayerName} />
      )}
    </div>
  );
}

/** O Sharpe em palavras: quanto retorno veio para cada unidade de oscilação. */
function sharpeVerdict(sharpe: number) {
  if (sharpe < 0) return "o risco não compensou";
  if (sharpe < 0.5) return "o risco foi pago, mas pouco";
  if (sharpe < 1) return "o risco foi bem pago";
  return "o risco foi muito bem pago";
}

/** Um ponto por jogador: quanto oscilou × quanto rendeu, com o CDI como referência sem oscilar. */
function RiskReturn({
  players,
  teams,
  naming,
  cdiReturn,
  currentPlayerName,
  simulationIds,
  colorOf,
}: {
  players: RiskPlayer[];
  /** Partida em equipes: um losango por equipe, na média dos membros */
  teams: TeamRisk[];
  naming: TeamNaming;
  cdiReturn: string | null;
  currentPlayerName?: string;
  simulationIds: number[];
  colorOf: (label: string) => string;
}) {
  const measured = players.filter(
    (p) => p.annual_volatility !== null && p.annual_return !== null && p.days >= MIN_SCATTER_DAYS,
  );
  // Jogadores no mesmo ponto (ex.: todos parados em caixa) viram um ponto só com os nomes juntos
  const byPosition = new Map<string, { keys: string[]; names: string[]; x: number; y: number; you: boolean }>();
  for (const p of measured) {
    const x = Number(p.annual_volatility);
    const y = Number(p.annual_return);
    const key = `${x.toFixed(4)}|${y.toFixed(4)}`;
    const point = byPosition.get(key) ?? { keys: [], names: [], x, y, you: false };
    const isYou = p.player_nickname === currentPlayerName;
    const label = playerLabel(p, simulationIds, currentPlayerName);
    point.keys.push(label);
    point.names.push(youLabel(label, isYou));
    point.you = point.you || isYou;
    byPosition.set(key, point);
  }
  const points = [...byPosition.values()].map((p) => ({
    ...p,
    label: displayList(p.names),
    colorKey: p.keys[0],
  }));
  const cdi = cdiReturn !== null ? Number(cdiReturn) : null;
  // Losango da equipe: volatilidade média × retorno médio; o tracejado liga cada membro a ele
  const teamPoints = teams
    .filter((t) => t.annual_volatility !== null && t.annual_return !== null)
    .map((t) => ({
      team: t.team,
      x: Number(t.annual_volatility),
      y: Number(t.annual_return),
      sharpe: t.sharpe_ratio,
      label: teamShortName(t.team, naming),
    }));
  const maxX = Math.max(...points.map((p) => p.x), ...teamPoints.map((t) => t.x), 0.01) * 1.15;
  const ys = [...points.map((p) => p.y), ...teamPoints.map((t) => t.y), cdi ?? 0];
  const minY = Math.min(...ys, 0) * 1.15;
  const maxY = Math.max(...ys, 0.01) * 1.15;
  const medianX = points.length ? [...points].sort((a, b) => a.x - b.x)[Math.floor(points.length / 2)].x : maxX / 2;

  // "Melhor da sala" só faz sentido com pelo menos dois Sharpes medidos
  const withSharpe = measured.filter((p) => p.sharpe_ratio !== null);
  const bestSharpe =
    withSharpe.length >= 2
      ? [...withSharpe].sort((a, b) => Number(b.sharpe_ratio) - Number(a.sharpe_ratio))[0]
      : undefined;
  const belowCdi = cdi !== null ? measured.filter((p) => Number(p.annual_return) < cdi) : [];
  const you = measured.find((p) => p.player_nickname === currentPlayerName);
  const bestTeam = teamPoints.filter((t) => t.sharpe !== null).sort((a, b) => Number(b.sharpe) - Number(a.sharpe))[0];
  // A equipe que rendeu mais oscilando menos que a seguinte: o losango dela fica acima e à esquerda
  const byReturn = [...teamPoints].sort((a, b) => b.y - a.y);
  const dominant =
    byReturn.length > 1 && byReturn[0].x < byReturn[1].x ? { winner: byReturn[0], other: byReturn[1] } : undefined;
  // Em cada equipe com três ou mais, quem segura a média (o mais perto do losango) e quem puxa
  // para baixo e para a direita (menos retorno e mais oscilação que a média)
  const holders = teamPoints.flatMap((t) => {
    const members = measured.filter((p) => p.team === t.team);
    if (members.length < 3) return [];
    const distance = (p: RiskPlayer) => Math.hypot(Number(p.annual_volatility) - t.x, Number(p.annual_return) - t.y);
    const worse = (p: RiskPlayer) => Number(p.annual_volatility) - t.x - (Number(p.annual_return) - t.y);
    const holder = [...members].sort((a, b) => distance(a) - distance(b))[0];
    const dragger = [...members].sort((a, b) => worse(b) - worse(a))[0];
    return [{ team: t.team, holder, dragger: worse(dragger) > 0 && dragger !== holder ? dragger : undefined }];
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risco × retorno</CardTitle>
        <CardDescription>
          {teams.length > 0
            ? "Um ponto por jogador, na cor dele; um losango por equipe, na cor da equipe. Quanto mais pra cima e pra esquerda, melhor."
            : "Um ponto por jogador no período inteiro. Quanto mais pra cima e pra esquerda, melhor."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {points.length === 0 ? (
          <div className="flex h-72 flex-col items-center justify-center gap-1 rounded-[10px] border border-dashed border-input text-center">
            <span className="font-semibold">Aparece no {MIN_SCATTER_DAYS}º pregão</span>
            <span className="text-[13px] text-muted-foreground">Com menos de 3 dias não dá pra medir oscilação.</span>
          </div>
        ) : (
          <div className="grid gap-5 lg:grid-cols-[1.7fr_1fr]">
            <div className="relative h-90">
              {/* Quadrantes: o melhor é em cima e à esquerda, o pior embaixo e à direita */}
              <span className="pointer-events-none absolute top-5 left-18 text-[11px] font-medium text-success">
                Mais retorno, menos risco
              </span>
              <span className="pointer-events-none absolute right-8 bottom-14 text-[11px] font-medium text-destructive">
                Menos retorno, mais risco
              </span>
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 16, right: 24, left: 8, bottom: 16 }}>
                  <CartesianGrid stroke="var(--border)" />
                  {cdi !== null && (
                    <ReferenceArea
                      x1={0}
                      x2={medianX}
                      y1={cdi}
                      y2={maxY}
                      fill="var(--success)"
                      fillOpacity={0.07}
                      ifOverflow="hidden"
                    />
                  )}
                  <XAxis
                    type="number"
                    dataKey="x"
                    domain={[0, maxX]}
                    tickFormatter={(v: number) => displayPercent(v, 0)}
                    tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
                    name="Volatilidade anual"
                    label={{
                      value: "Volatilidade anual (risco) →",
                      position: "insideBottom",
                      offset: -8,
                      fontSize: 11,
                    }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    domain={[minY, maxY]}
                    tickFormatter={(v: number) => displayPercent(v, 0)}
                    tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
                    width={64}
                    name="Retorno anual"
                    label={{
                      value: "Retorno anual →",
                      angle: -90,
                      position: "insideLeft",
                      offset: 8,
                      fontSize: 11,
                      fill: "var(--muted-foreground)",
                      style: { textAnchor: "middle" },
                    }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    contentStyle={{ borderRadius: 10, borderColor: "var(--border)", fontSize: 12 }}
                    formatter={(v, name) => [displayPercent(Number(v)), name]}
                  />
                  {measured
                    .filter((p) => p.team !== null)
                    .map((p) => {
                      const target = teamPoints.find((t) => t.team === p.team);
                      return target ? (
                        <ReferenceLine
                          key={`${p.player_nickname}-link`}
                          segment={[
                            { x: Number(p.annual_volatility), y: Number(p.annual_return) },
                            { x: target.x, y: target.y },
                          ]}
                          stroke={teamColor(target.team)}
                          strokeDasharray="4 3"
                          strokeOpacity={0.6}
                          ifOverflow="hidden"
                        />
                      ) : null;
                    })}
                  <Scatter
                    data={points}
                    isAnimationActive={false}
                    shape={(props: { cx?: number; cy?: number; payload?: (typeof points)[number] }) => (
                      // Você em destaque: ponto maior com borda branca
                      <circle
                        cx={props.cx}
                        cy={props.cy}
                        r={props.payload?.you ? 8 : 6}
                        fill={colorOf(props.payload?.colorKey ?? "")}
                        stroke="var(--card)"
                        strokeWidth={props.payload?.you ? 2 : 0}
                      />
                    )}
                  >
                    <LabelList
                      dataKey="label"
                      content={({ x, y, width, height, value, index }) => {
                        // Na metade direita o nome vai à esquerda do ponto, para caber no gráfico
                        const point = index !== undefined ? points[index] : undefined;
                        const toLeft = point !== undefined && point.x > maxX / 2;
                        const cx = Number(x) + Number(width) / 2;
                        return (
                          <text
                            x={toLeft ? cx - 12 : cx + 12}
                            y={Number(y) + Number(height) / 2 + 4}
                            textAnchor={toLeft ? "end" : "start"}
                            fontSize={11}
                            fontWeight={point?.you ? 700 : 500}
                            fill={point ? colorOf(point.colorKey) : "var(--foreground)"}
                          >
                            {value}
                          </text>
                        );
                      }}
                    />
                  </Scatter>
                  {teamPoints.length > 0 && (
                    <Scatter
                      data={teamPoints}
                      isAnimationActive={false}
                      shape={(props: { cx?: number; cy?: number; payload?: (typeof teamPoints)[number] }) => (
                        <rect
                          x={(props.cx ?? 0) - 7}
                          y={(props.cy ?? 0) - 7}
                          width={14}
                          height={14}
                          transform={`rotate(45 ${props.cx ?? 0} ${props.cy ?? 0})`}
                          fill={teamColor(props.payload?.team ?? 1)}
                          stroke="var(--card)"
                          strokeWidth={2}
                        />
                      )}
                    >
                      <LabelList
                        dataKey="label"
                        position="top"
                        fontSize={11}
                        fontWeight={700}
                        fill="var(--foreground)"
                      />
                    </Scatter>
                  )}
                  {cdi !== null && (
                    <Scatter
                      data={[{ x: 0, y: cdi, label: `CDI · ${displayPercent(cdi)} sem oscilar` }]}
                      fill="var(--faint-foreground)"
                      shape="diamond"
                    >
                      <LabelList dataKey="label" position="right" fontSize={11} fill="var(--muted-foreground)" />
                    </Scatter>
                  )}
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <div className="grid content-start gap-3">
              <div className="grid gap-1 rounded-[10px] bg-subtle p-3.5 text-[13px]">
                <span className="font-semibold">Leitura rápida</span>
                {dominant && (
                  <span className="text-muted-foreground">
                    A <b className="text-foreground">{teamName(dominant.winner.team, naming)}</b> rendeu mais oscilando
                    menos: o losango dela fica acima e à esquerda do da {teamShortName(dominant.other.team, naming)}.
                  </span>
                )}
                {holders.map(({ team, holder, dragger }) => (
                  <span key={team} className="text-muted-foreground">
                    Na {teamShortName(team, naming)}, <b className="text-foreground">{holder.player_nickname}</b> segura
                    a média
                    {dragger && (
                      <>
                        ; <b className="text-foreground">{dragger.player_nickname}</b> puxa para baixo e para a direita
                      </>
                    )}
                    .
                  </span>
                ))}
                {bestTeam && teamPoints.length > 1 && !dominant && (
                  <span className="text-muted-foreground">
                    A <b className="text-foreground">{teamName(bestTeam.team, naming)}</b> rendeu mais por unidade de
                    oscilação: Sharpe médio{" "}
                    <b className="font-mono text-foreground">{displayNumber(bestTeam.sharpe ?? 0)}</b>, o melhor entre
                    as equipes.
                  </span>
                )}
                {bestSharpe && (
                  <span className="text-muted-foreground">
                    <b className="text-foreground">{bestSharpe.player_nickname}</b> rendeu mais por unidade de
                    oscilação: Sharpe{" "}
                    <b className="font-mono text-foreground">{displayNumber(bestSharpe.sharpe_ratio ?? 0)}</b>, o melhor
                    da sala.
                  </span>
                )}
                {belowCdi.length > 0 && (
                  <span className="text-muted-foreground">
                    {belowCdi.length === measured.length && belowCdi.length > 1
                      ? "Todos ficaram"
                      : `${displayList(belowCdi.map((p) => p.player_nickname))} ${belowCdi.length > 1 ? "ficaram" : "ficou"}`}{" "}
                    abaixo do CDI.
                  </span>
                )}
              </div>
              {teamPoints.length > 0 && (
                <div className="grid gap-1 rounded-[10px] bg-subtle p-3.5 text-[13px]">
                  <span className="font-semibold">Losango e tracejado</span>
                  <span className="text-muted-foreground">
                    O losango é a média da equipe (volatilidade média × retorno médio). O tracejado liga cada membro à
                    média da equipe dele.
                  </span>
                </div>
              )}
              {you && (
                <div className="grid gap-1 rounded-[10px] bg-warning-soft/60 p-3.5 text-[13px]">
                  <span className="font-semibold">Você</span>
                  <span className="text-muted-foreground">
                    Oscilou <b className="font-mono text-foreground">{displayPercent(you.annual_volatility ?? 0)}</b> ao
                    ano pra render <b className="font-mono text-foreground">{displayPercent(you.annual_return ?? 0)}</b>
                    {cdi !== null && (
                      <>
                        :{" "}
                        <b className="font-mono text-foreground">
                          {displayNumber(Math.abs(Number(you.annual_return ?? 0) - cdi) * 100)} p.p.{" "}
                          {Number(you.annual_return ?? 0) >= cdi ? "acima" : "abaixo"} do CDI
                        </b>
                      </>
                    )}
                    . Sharpe{" "}
                    <b className="font-mono text-foreground">
                      {you.sharpe_ratio ? displayNumber(you.sharpe_ratio) : "—"}
                    </b>
                    {you.sharpe_ratio !== null && (
                      <>
                        : <b className="text-foreground">{sharpeVerdict(Number(you.sharpe_ratio))}</b>
                      </>
                    )}
                    .
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
