import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayPercent, isLoss } from "@/shared/lib/utils/display";
import type { OverviewReport } from "@/types";
import { playerLabel } from "../../lib/player-label";
import { SCORE, displayMetric } from "../../lib/metrics";
import { MetricLabel } from "./metric-hint";

interface Props {
  players: OverviewReport["players"];
  currentPlayerName: string;
  showSimulation: boolean;
}

export function PlayersRankingTable({ players, currentPlayerName, showSimulation }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Ranking de Jogadores</CardTitle>
      </CardHeader>

      <CardContent className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              {["Posição", "Jogador"].map((h) => (
                <TableHead key={h} className="text-center">
                  {h}
                </TableHead>
              ))}
              <TableHead className="text-center">
                <MetricLabel metric={SCORE} />
              </TableHead>
              {["Patrimônio", "Retorno (R$)", "Retorno (%)", "Dias simulados"].map((h) => (
                <TableHead key={h} className="text-center">
                  {h}
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
                  key={playerLabel(player, true)}
                  className={`
                    text-center [&>td]:py-4
                    ${isCurrentPlayer ? "bg-primary/5 font-semibold" : ""}
                  `}
                >
                  <TableCell>{player.position}</TableCell>
                  <TableCell>{playerLabel(player, showSimulation)}</TableCell>
                  <TableCell className="font-semibold">{displayMetric(SCORE, player.score?.total)}</TableCell>
                  <TableCell>{displayMoney(player.total_networth)}</TableCell>
                  <TableCell className={returnColor}>{displayMoney(player.return_value)}</TableCell>
                  <TableCell className={returnColor}>{displayPercent(player.return_percent)}</TableCell>
                  <TableCell>{player.days}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
