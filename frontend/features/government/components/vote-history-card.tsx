import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { GovernmentPanel } from "@/types";

type VoteHistoryCardProps = { history: GovernmentPanel["congress"]["history"] };

/** As votações que a casa já fez, da mais recente para a mais antiga. */
export function VoteHistoryCard({ history }: VoteHistoryCardProps) {
  if (history.length === 0) return null;

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <h2 className="text-[15px] font-semibold">Votações da casa</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Dia</TableHead>
                <TableHead>Votação</TableHead>
                <TableHead>Resultado</TableHead>
                <TableHead numeric>Sim</TableHead>
                <TableHead numeric>Não</TableHead>
                <TableHead numeric>Contra a orientação</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.map((vote, index) => (
                <TableRow key={`${vote.day}-${index}`}>
                  <TableCell>{displayDayMonth(vote.day)}</TableCell>
                  <TableCell className="whitespace-normal">
                    <b className="font-medium">{vote.title}</b>
                  </TableCell>
                  <TableCell>
                    <Badge variant={vote.approved ? "success" : "destructive"} size="sm">
                      {vote.approved ? "Aprovada" : "Rejeitada"}
                    </Badge>
                  </TableCell>
                  <TableCell numeric>{vote.yes}</TableCell>
                  <TableCell numeric>{vote.no}</TableCell>
                  <TableCell numeric>{vote.defected}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
