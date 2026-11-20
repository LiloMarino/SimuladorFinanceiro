import { Badge } from "@/shared/components/ui/badge";
import { Card, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayDayMonth, displayIsoDate } from "@/shared/lib/utils/display";
import { isApproved, resultScore, resultTitle, type AssemblyResult } from "../lib/fund-assembly";
import { rejectionNote } from "../lib/fund-merge";

/** O período da votação: "27/10 a 02/11/2026". */
const period = (result: AssemblyResult) =>
  `${displayDayMonth(result.started_on)} a ${displayIsoDate(result.closed_on)}`;

type AssemblyHistoryCardProps = { history: AssemblyResult[] };

/** As votações concluídas, da mais recente para a mais antiga. */
export function AssemblyHistoryCard({ history }: AssemblyHistoryCardProps) {
  return (
    <Card size="flush">
      {/* Cabeçalho */}
      <div className="px-5 pt-4 pb-3">
        <CardTitle>Votações anteriores</CardTitle>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Pauta</TableHead>
            <TableHead>Convocada por</TableHead>
            <TableHead>Período</TableHead>
            <TableHead>Resultado</TableHead>
            <TableHead>Placar</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {history.map((result) => {
            const note = rejectionNote(result);
            return (
              <TableRow key={result.id}>
                <TableCell>{resultTitle(result)}</TableCell>
                <TableCell>{result.convener_nickname}</TableCell>
                <TableCell>{period(result)}</TableCell>
                <TableCell>
                  <Badge variant={isApproved(result) ? "success" : "destructive"} size="tag">
                    {isApproved(result) ? "aprovada" : "rejeitada"}
                  </Badge>
                  {note !== null && <p className="mt-1 text-xs text-muted-foreground">{note}</p>}
                </TableCell>
                <TableCell>{resultScore(result)}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}
