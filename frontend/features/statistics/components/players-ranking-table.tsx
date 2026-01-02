import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";

export interface PlayerStat {
  position: number;
  name: string;
  totalNetWorth: number;
  returnValue: number;
  returnPercent: number;
}

interface Props {
  playersStats: PlayerStat[];
  currentPlayerName: string;
}

export function PlayersRankingTable({ playersStats, currentPlayerName }: Props) {
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
            </TableRow>
          </TableHeader>

          <TableBody>
            {playersStats.map((player) => {
              const isCurrentPlayer = player.name === currentPlayerName;

              return (
                <TableRow
                  key={player.position}
                  className={`
                    text-center [&>td]:py-4
                    ${isCurrentPlayer ? "bg-primary/5 font-semibold" : ""}
                  `}
                >
                  <TableCell>{player.position}</TableCell>

                  <TableCell>{player.name}</TableCell>

                  <TableCell>{displayMoney(player.totalNetWorth)}</TableCell>

                  <TableCell className={player.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                    {displayMoney(player.returnValue)}
                  </TableCell>

                  <TableCell className={player.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                    {displayPercent(player.returnPercent)}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
