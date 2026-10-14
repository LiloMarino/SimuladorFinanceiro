import { useState } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { MetricHint } from "@/shared/components/metric-hint";
import {
  displayMoney,
  displayMoneyCompact,
  displayMonthSlashYear,
  displayNumber,
  displayPercent,
} from "@/shared/lib/utils/display";
import type { CompositionReport } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { EFFECTIVE_SECTORS, SECTOR_PROFIT } from "../../lib/metrics";
import { playerColors } from "../../lib/player-colors";
import { playerLabel } from "../../lib/player-label";
import { PlayerCell, TabStatus, type ReportProps } from "./shared";

type Player = CompositionReport["players"][number];
type Unit = "PCT" | "MONEY";

const SERIES = [
  { key: "total_cash", label: "Caixa", color: "var(--input)" },
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

export function CompositionTab({ simulationIds, showSimulation, currentPlayerName }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("composition", simulationIds);
  const [unit, setUnit] = useState<Unit>("PCT");
  if (!data) return <TabStatus loading={isLoading} title="a Composição" error={error} onRetry={() => void refetch()} />;

  const labels = data.players.map((p) => playerLabel(p, showSimulation));
  const colorOf = playerColors(labels);

  return (
    <div className="grid gap-5">
      {/* Como cada um dividiu o dinheiro */}
      <Card>
        <CardHeader>
          <CardTitle>Como cada um dividiu o dinheiro</CardTitle>
          <CardDescription>
            Fatia do patrimônio em caixa, ações e renda fixa, dia a dia. Todos lado a lado.
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
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {data.players.map((p) => (
                <SmallMultiple
                  key={playerLabel(p, true)}
                  player={p}
                  label={playerLabel(p, showSimulation)}
                  unit={unit}
                />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <SectorExposure
        players={data.players}
        showSimulation={showSimulation}
        currentPlayerName={currentPlayerName}
        colorOf={colorOf}
      />
      <SectorProfit players={data.players} showSimulation={showSimulation} />
    </div>
  );
}

function SmallMultiple({ player, label, unit }: { player: Player; label: string; unit: Unit }) {
  const rows = player.history.map((h) => ({
    date: h.snapshot_date,
    total_cash: Number(h.total_cash),
    total_equity: Number(h.total_equity),
    total_fixed: Number(h.total_fixed),
  }));

  return (
    <div className="grid gap-1.5">
      <span className="text-[13px] font-semibold">{label}</span>
      {rows.length < 2 ? (
        <div className="flex h-36 items-center justify-center rounded-lg border border-dashed border-input text-xs text-muted-foreground">
          Sem histórico ainda
        </div>
      ) : (
        <div className="h-36">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={rows}
              stackOffset={unit === "PCT" ? "expand" : "none"}
              margin={{ top: 4, right: 4, left: 0, bottom: 0 }}
            >
              <XAxis dataKey="date" hide />
              <YAxis
                width={44}
                tick={{ fontSize: 10, fill: "var(--faint-foreground)" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v: number) => (unit === "PCT" ? displayPercent(v, 0) : displayMoneyCompact(v))}
              />
              <Tooltip
                contentStyle={{ borderRadius: 10, borderColor: "var(--border)", fontSize: 11 }}
                labelFormatter={(d) => displayMonthSlashYear(String(d))}
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
      )}
    </div>
  );
}

/** Jogador × setor: quanto mais escuro, maior a aposta; a diversificação em número e em palavras. */
function SectorExposure({
  players,
  showSimulation,
  currentPlayerName,
  colorOf,
}: {
  players: Player[];
  showSimulation: boolean;
  currentPlayerName?: string;
  colorOf: (label: string) => string;
}) {
  const sectors = [...new Set(players.flatMap((p) => p.sectors.map((s) => s.sector ?? NO_SECTOR)))].sort((a, b) =>
    a === NO_SECTOR ? 1 : b === NO_SECTOR ? -1 : a.localeCompare(b),
  );

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
              <TableHead>Jogador</TableHead>
              {sectors.map((s) => (
                <TableHead key={s} numeric>
                  {s}
                </TableHead>
              ))}
              <TableHead>
                <span className="flex items-center gap-1">
                  Diversificação
                  <MetricHint metric={EFFECTIVE_SECTORS} />
                </span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {players.map((p) => {
              const label = playerLabel(p, showSimulation);
              const isYou = p.player_nickname === currentPlayerName;
              const bySector = new Map(p.sectors.map((s) => [s.sector ?? NO_SECTOR, Number(s.fraction)]));
              const effective = p.effective_sectors !== null ? Number(p.effective_sectors) : null;
              return (
                <TableRow key={playerLabel(p, true)} variant={isYou ? "current" : "default"}>
                  <TableCell>
                    <PlayerCell label={label} color={colorOf(label)} isYou={isYou} />
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
                        <b className="font-mono">{displayNumber(effective, 2)}</b> · {diversificationWord(effective)}
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}
    </Card>
  );
}

/** Lucro ou prejuízo por setor, em barras para os dois lados e com a mesma escala pra todos. */
function SectorProfit({ players, showSimulation }: { players: Player[]; showSimulation: boolean }) {
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
        <div className="grid gap-4 md:grid-cols-2">
          {players.map((p) => {
            const total = p.sector_profit.reduce((sum, s) => sum + Number(s.profit), 0);
            return (
              <div
                key={playerLabel(p, true)}
                className="grid content-start gap-2 rounded-[10px] border border-border p-4"
              >
                <div className="flex justify-between">
                  <span className="font-semibold">{playerLabel(p, showSimulation)}</span>
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
                            value >= 0 ? "text-right font-mono text-success" : "text-right font-mono text-destructive"
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
      </CardContent>
    </Card>
  );
}
