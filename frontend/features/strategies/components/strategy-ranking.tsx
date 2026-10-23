import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMonthName, displaySignedPercent } from "@/shared/lib/utils/display";
import type { StrategyRanking } from "@/types";

type RankingBlockProps = {
  ranking: StrategyRanking;
};

/** As ações da lista da que mais subiu em 12 meses à que menos subiu, com as que a estratégia mantém. */
export function RankingBlock({ ranking }: RankingBlockProps) {
  const kept = ranking.rows.filter((row) => row.selected).length;
  const withoutHistory = ranking.rows.filter((row) => row.return_12m === null).length;

  return (
    <div className="grid gap-2.5">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-10">#</TableHead>
            <TableHead>Ação</TableHead>
            <TableHead numeric>
              <span className="inline-flex items-center gap-1.5">
                Retorno em 12 meses
                <InfoHint label="Como ler o retorno em 12 meses">
                  Quanto o preço subiu ou caiu nos últimos 252 pregões (um ano de mercado). Ex.: de R$ 20 para R$ 25 é
                  +25,0%. Acima de zero a ação subiu no ano e pode entrar; negativo, ela fica de fora.
                </InfoHint>
              </span>
            </TableHead>
            <TableHead />
          </TableRow>
        </TableHeader>
        <TableBody>
          {ranking.rows.map((row, index) => (
            <TableRow key={row.ticker} variant={row.selected ? "current" : "default"}>
              <TableCell>
                <span className="text-muted-foreground">{index + 1}</span>
              </TableCell>
              <TableCell>
                <span className="font-mono font-semibold">{row.ticker}</span>{" "}
                <span className="text-xs text-muted-foreground">{row.name}</span>
              </TableCell>
              <TableCell numeric>
                {row.return_12m === null ? (
                  "—"
                ) : (
                  <span className={Number(row.return_12m) > 0 ? "text-success" : "text-destructive"}>
                    {displaySignedPercent(Number(row.return_12m), 1)}
                  </span>
                )}
              </TableCell>
              <TableCell className="text-right">
                {row.selected && (
                  <Badge variant="success" size="tag">
                    Fica
                  </Badge>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {kept === 0 && (
        <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs text-muted-foreground">
          Nenhuma ação tem retorno positivo em 12 meses: ela fica em caixa até a próxima troca.
        </p>
      )}
      {withoutHistory > 0 && (
        <p className="text-xs text-warning">
          {withoutHistory === 1 ? "1 ação não tem" : `${withoutHistory} ações não têm`} {ranking.needed_days} pregões de
          histórico nesta partida e ficam fora do ranking.
        </p>
      )}
      <p className="text-xs text-muted-foreground">
        Próxima troca: no 1º pregão de {displayMonthName(ranking.next_switch)}.
      </p>
    </div>
  );
}
