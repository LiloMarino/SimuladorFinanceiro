import { InfoHint } from "@/shared/components/info-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import type { Budget } from "@/types";
import { defaultRateLabel, shareLabel, signedShareLabel, taxRevenueLabel, todayRateLabel } from "../lib/budget";
import { REVENUE } from "../lib/government-metrics";

type RevenueCardProps = { budget: Budget };

/** A diferença contra a política padrão: mais receita em verde, menos em vermelho. */
function differenceTone(difference: string) {
  const value = Number(difference);
  if (value > 0) return "text-success";
  return value < 0 ? "text-destructive" : "text-muted-foreground";
}

/** De onde vem a receita: cada imposto do jogo com a alíquota de hoje, a padrão e o que arrecada em % do PIB por ano. */
export function RevenueCard({ budget }: RevenueCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3">
          <div className="flex items-center gap-1.5">
            <h2 className="text-[15px] font-semibold">De onde vem a receita</h2>
            <InfoHint label="Como ler a receita">
              <div className="space-y-1 text-left">
                <p>{REVENUE.definition}</p>
                <p>{REVENUE.example}</p>
                <p>{REVENUE.reading}</p>
              </div>
            </InfoHint>
          </div>
          <span className="text-[13px] text-muted-foreground">
            Cada imposto do jogo tem uma base no PIB. Mudar a alíquota muda a receita dele, mas um pouco menos que
            proporcionalmente: quem paga menos passa a operar mais.
          </span>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Imposto</TableHead>
                <TableHead numeric>Hoje</TableHead>
                <TableHead numeric>Padrão</TableHead>
                <TableHead numeric>Arrecada</TableHead>
                <TableHead numeric>vs. padrão</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {budget.taxes.map((tax) => (
                <TableRow key={`${tax.key}-${tax.name}`}>
                  <TableCell className="whitespace-normal">{tax.name}</TableCell>
                  <TableCell numeric>{todayRateLabel(tax)}</TableCell>
                  <TableCell numeric>
                    <span className="text-muted-foreground">{defaultRateLabel(tax)}</span>
                  </TableCell>
                  <TableCell numeric>{taxRevenueLabel(tax)}</TableCell>
                  <TableCell numeric>
                    <span className={differenceTone(tax.difference)}>{signedShareLabel(tax.difference)}</span>
                  </TableCell>
                </TableRow>
              ))}
              <TableRow>
                <TableCell className="whitespace-normal">
                  <span className="font-medium">Resto da arrecadação do país</span>
                </TableCell>
                <TableCell />
                <TableCell />
                <TableCell numeric>{shareLabel(budget.fixed_revenue)}</TableCell>
                <TableCell numeric variant="note">
                  fixo
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="whitespace-normal">
                  <b>Receita total, por ano</b>
                </TableCell>
                <TableCell />
                <TableCell />
                <TableCell numeric>
                  <b>{shareLabel(budget.total_revenue)}</b>
                </TableCell>
                <TableCell numeric>
                  <span className={differenceTone(budget.total_difference)}>
                    {signedShareLabel(budget.total_difference)}
                  </span>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <span className="text-xs text-muted-foreground">
            Padrão: a política de impostos de antes da expansão. Em % do PIB por ano.
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
