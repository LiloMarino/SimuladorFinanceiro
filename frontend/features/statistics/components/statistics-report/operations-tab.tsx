import { Info } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { MetricLabel } from "@/shared/components/metric-hint";
import { displayMoney, displayMoneyCompact, displayMonthSlashYear, displayNumber } from "@/shared/lib/utils/display";
import type { OperationsReport } from "@/types";
import { useStatisticsReport } from "../../hooks/queries/useStatisticsReport";
import { IMPACT_COST, INCOME_TAX_PAID, MONTHLY_VOLUME, TRADED_VOLUME, TURNOVER } from "../../lib/metrics";
import { playerColors } from "../../lib/player-colors";
import { playerKey, playerLabel } from "../../lib/player-label";
import { PlayerCell, TabStatus, type ReportProps } from "./shared";

type Player = OperationsReport["players"][number];

export function OperationsTab({ simulationIds, currentPlayerName, onlyPlayer }: ReportProps) {
  const { data, isLoading, error, refetch } = useStatisticsReport("operations", simulationIds, onlyPlayer);
  if (!data) return <TabStatus loading={isLoading} title="as Operações" error={error} onRetry={() => void refetch()} />;

  const labels = data.players.map((p) => playerLabel(p, simulationIds));
  const colorOf = playerColors(labels);
  const impactOn = data.players.some((p) => p.impact_cost !== null);

  return (
    <div className="grid gap-5">
      <VolumeHeatmap players={data.players} simulationIds={simulationIds} />

      <Card className="overflow-hidden">
        <CardHeader>
          <CardTitle>Como cada um operou</CardTitle>
          <CardDescription>Giro = volume ÷ patrimônio médio. Não é bom nem ruim: mostra o estilo.</CardDescription>
        </CardHeader>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Jogador</TableHead>
              <TableHead>Negócios</TableHead>
              <TableHead numeric>
                <MetricLabel metric={TRADED_VOLUME} />
              </TableHead>
              <TableHead>
                <MetricLabel metric={TURNOVER} />
              </TableHead>
              <TableHead numeric>
                <MetricLabel metric={INCOME_TAX_PAID} />
              </TableHead>
              <TableHead numeric>
                <MetricLabel metric={IMPACT_COST} />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.players.map((p: Player) => {
              const label = playerLabel(p, simulationIds);
              const isYou = p.player_nickname === currentPlayerName;
              const trades = p.buy_trades + p.sell_trades;
              const impact = p.impact_cost !== null ? Number(p.impact_cost) : null;
              return (
                <TableRow key={playerKey(p)} variant={isYou ? "current" : "default"}>
                  <TableCell>
                    <PlayerCell label={label} color={colorOf(label)} isYou={isYou} />
                  </TableCell>
                  <TableCell>
                    <div className="grid w-40 gap-1">
                      <span className="flex h-2 gap-0.5 overflow-hidden rounded-full bg-muted">
                        {trades > 0 && (
                          <>
                            <span className="bg-success" style={{ width: `${(p.buy_trades / trades) * 100}%` }} />
                            <span className="bg-destructive" style={{ width: `${(p.sell_trades / trades) * 100}%` }} />
                          </>
                        )}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {p.buy_trades} compras · {p.sell_trades} vendas
                      </span>
                    </div>
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
                    {impact === null || impact === 0 ? (
                      <span className="text-faint-foreground">{impact === 0 ? displayMoney(0) : "—"}</span>
                    ) : (
                      <span className={impact > 0 ? "text-destructive" : "text-success"}>
                        {impact > 0 ? "+" : ""}
                        {displayMoney(impact)}
                      </span>
                    )}
                  </TableCell>
                </TableRow>
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

/** Jogador × mês: mais escuro, mais dinheiro girando; cinza, mês só segurando. */
function VolumeHeatmap({ players, simulationIds }: { players: Player[]; simulationIds: number[] }) {
  const months = [...new Set(players.flatMap((p) => p.monthly_volume.map((m) => m.month)))].sort();
  const volumeOf = (m: Player["monthly_volume"][number]) => Number(m.bought) + Number(m.sold);
  const max = Math.max(...players.flatMap((p) => p.monthly_volume.map(volumeOf)), 1);

  return (
    <Card className="overflow-hidden">
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1">
            <MetricLabel metric={MONTHLY_VOLUME} />
          </span>
        </CardTitle>
        <CardDescription>
          Volume de compras + vendas de ações por mês. Mais escuro, mais dinheiro girando; cinza, mês só segurando.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {months.length === 0 ? (
          <p className="py-6 text-center text-[13px] text-muted-foreground">Ninguém negociou ações ainda.</p>
        ) : (
          <div className="overflow-x-auto">
            <div
              className="grid gap-1"
              style={{ gridTemplateColumns: `140px repeat(${months.length}, minmax(16px, 56px))` }}
            >
              <span />
              {months.map((m, i) => (
                <span key={m} className="text-center font-mono text-[10px] whitespace-nowrap text-faint-foreground">
                  {months.length <= 12 || i % 3 === 0 ? displayMonthSlashYear(m) : ""}
                </span>
              ))}
              {players.map((p) => {
                const byMonth = new Map(p.monthly_volume.map((m) => [m.month, m]));
                return (
                  <div key={playerKey(p)} className="contents">
                    <span className="truncate text-[13px]">{playerLabel(p, simulationIds)}</span>
                    {months.map((month) => {
                      const entry = byMonth.get(month);
                      const volume = entry ? volumeOf(entry) : 0;
                      return (
                        <Tooltip key={month}>
                          <TooltipTrigger render={<span />}>
                            <span
                              className="block h-7 rounded"
                              style={{
                                backgroundColor: volume
                                  ? `color-mix(in oklab, var(--primary) ${Math.round(15 + (volume / max) * 85)}%, transparent)`
                                  : "var(--muted)",
                              }}
                            />
                          </TooltipTrigger>
                          <TooltipContent>
                            {playerLabel(p, simulationIds)} · {displayMonthSlashYear(month)}
                            <br />
                            {entry && volume
                              ? `${displayMoney(volume)} · ${entry.buy_count} compras, ${entry.sell_count} vendas`
                              : "Sem negócios"}
                          </TooltipContent>
                        </Tooltip>
                      );
                    })}
                  </div>
                );
              })}
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
