import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { formatMoney, formatPercent } from "@/shared/lib/utils/formatting";

export interface PlayerStat {
  position: number;
  name: string;
  totalNetWorth: number;
  returnValue: number;
  returnPercent: number;
}

interface Props {
  playersStats: PlayerStat[];
}

export function PlayersRankingTable({ playersStats }: Props) {
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
            {playersStats.map((player) => (
              <TableRow key={player.position} className="text-center [&>td]:py-4">
                <TableCell>{player.position}</TableCell>
                <TableCell>{player.name}</TableCell>
                <TableCell>{formatMoney(player.totalNetWorth)}</TableCell>
                <TableCell className={player.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                  {formatMoney(player.returnValue)}
                </TableCell>
                <TableCell className={player.returnValue >= 0 ? "text-green-600" : "text-red-600"}>
                  {formatPercent(player.returnPercent)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
