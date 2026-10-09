import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayPercent, isLoss } from "@/shared/lib/utils/display";
import type { PlayerPerformance } from "@/types";
import { playerLabel } from "../lib/player-label";
import { RISK_METRICS, displayRiskMetric } from "../lib/risk-metrics";
import { RiskMetricHint } from "./risk-metric-hint";

interface Props {
  players: PlayerPerformance[];
  currentPlayerName: string;
  showSimulation?: boolean;
}

export function PlayersRankingTable({ players, currentPlayerName, showSimulation = false }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Ranking de Jogadores</CardTitle>
      </CardHeader>

      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {["Posição", "Jogador", "Patrimônio", "Retorno (R$)", "Retorno (%)"].map((h) => (
                <TableHead key={h} className="text-center">
                  {h}
                </TableHead>
              ))}
              {RISK_METRICS.map((metric) => (
                <TableHead key={metric.key} className="text-center">
                  <span className="inline-flex items-center gap-1">
                    {metric.label}
                    <RiskMetricHint metric={metric} />
                  </span>
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>

          <TableBody>
            {players.map((player) => {
              const isCurrentPlayer = player.player_nickname === currentPlayerName;
              const returnColor = isLoss(player.return_value) ? "text-destructive" : "text-success";

              return (
                <TableRow
                  key={player.position}
                  className={`
                    text-center [&>td]:py-4
                    ${isCurrentPlayer ? "bg-primary/5 font-semibold" : ""}
                  `}
                >
                  <TableCell>{player.position}</TableCell>

                  <TableCell>{playerLabel(player, showSimulation)}</TableCell>

                  <TableCell>{displayMoney(player.total_networth)}</TableCell>

                  <TableCell className={returnColor}>{displayMoney(player.return_value)}</TableCell>

                  <TableCell className={returnColor}>{displayPercent(player.return_percent)}</TableCell>

                  {RISK_METRICS.map((metric) => (
                    <TableCell key={metric.key}>{displayRiskMetric(metric, player.risk)}</TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
