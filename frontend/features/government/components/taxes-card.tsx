import { Plus } from "lucide-react";
import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import type { Budget, GovernmentPanel, MeasureKind } from "@/types";
import { useToday } from "../hooks/useToday";
import { shareLabel, signedShareLabel } from "../lib/budget";
import { generalLabel, generalToday, isGeneral, measureTarget, monthYear, sectorEffect } from "../lib/government";
import { REVENUE, TAX_PRICE, type TaxPrice } from "../lib/government-metrics";
import { MeasureAction } from "./measure-action";

type TaxRow = GovernmentPanel["taxes"][number];

type TaxesCardProps = {
  panel: GovernmentPanel;
  budget: Budget;
  onPropose: (kind?: MeasureKind) => void;
};

/** A diferença contra a política padrão: mais receita em verde, menos em vermelho. */
function differenceTone(difference: string) {
  const value = Number(difference);
  if (value > 0) return "text-success";
  return value < 0 ? "text-destructive" : "text-muted-foreground";
}

/** Receita de um imposto; sem arrecadação, traço. */
function revenueLabel(revenue: string | null) {
  return revenue === null || Number(revenue) === 0 ? "—" : shareLabel(revenue);
}

/** Os impostos do jogo: a alíquota de hoje, a padrão e o que arrecada, mais as medidas por setor; o presidente propõe a mudança de cada linha. */
export function TaxesCard({ panel, budget, onPropose }: TaxesCardProps) {
  const today = useToday(panel);
  const baseRate = panel.taxes.find((row) => row.kind === "STOCK_PROFIT_RATE")?.value ?? "0";
  const exemption = panel.taxes.find((row) => row.kind === "STOCK_EXEMPTION");
  const rates = panel.taxes.filter((row) => row.kind !== "STOCK_EXEMPTION");

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          {/* Cabeçalho */}
          <div className="flex items-start justify-between gap-3">
            <div className="grid gap-1">
              <span className="text-xs font-semibold tracking-[.06em] text-faint-foreground uppercase">Entra</span>
              <div className="flex items-center gap-1.5">
                <h2 className="text-[15px] font-semibold">Impostos e receita</h2>
                <InfoHint label="Como ler a receita">
                  <div className="space-y-1 text-left">
                    <p>{REVENUE.definition}</p>
                    <p>{REVENUE.example}</p>
                    <p>{REVENUE.reading}</p>
                  </div>
                </InfoHint>
              </div>
              <span className="text-[13px] text-muted-foreground">
                Cada imposto tem uma base no PIB. Mudar a alíquota muda a receita dele, mas menos que proporcionalmente:
                quem paga menos passa a operar mais. Os do investimento só mudam o que cada um paga ao vender com lucro;
                consumo, IR das empresas e folha cobram também da economia.
              </span>
            </div>
            {panel.is_president && (
              <Button size="sm" onClick={() => onPropose()}>
                <Plus />
                Nova medida
              </Button>
            )}
          </div>

          {/* Listagem de impostos */}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Imposto</TableHead>
                <TableHead numeric>Hoje</TableHead>
                <TableHead numeric>Padrão</TableHead>
                <TableHead numeric>Arrecada</TableHead>
                <TableHead numeric>vs. padrão</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {rates.map((row) => (
                <TaxRateRow
                  key={row.kind}
                  row={row}
                  exemption={row.kind === "STOCK_PROFIT_RATE" ? exemption : undefined}
                  isPresident={panel.is_president}
                  onPropose={onPropose}
                />
              ))}

              {/* O ajuste ao primário real e o total */}
              {Number(budget.fixed_revenue) !== 0 && (
                <TableRow>
                  <TableCell className="whitespace-normal">
                    <span className="flex items-center gap-1.5">
                      Ajuste ao primário real do país
                      <InfoHint label="O que é o ajuste ao primário">
                        <p className="text-left">
                          Os impostos acima fecham o gasto-base do país. Esta linha soma (ou tira) o que faltou ou
                          sobrou no resultado primário real na posse, para a conta partir do primário que o país tinha.
                          Não muda com as medidas.
                        </p>
                      </InfoHint>
                    </span>
                  </TableCell>
                  <TableCell colSpan={2} />
                  <TableCell numeric>{shareLabel(budget.fixed_revenue)}</TableCell>
                  <TableCell numeric variant="note">
                    fixo
                  </TableCell>
                  <TableCell />
                </TableRow>
              )}
              <TableRow variant="current">
                <TableCell>Receita total, por ano</TableCell>
                <TableCell colSpan={2} />
                <TableCell numeric>{shareLabel(budget.total_revenue)}</TableCell>
                <TableCell numeric className={differenceTone(budget.total_difference)}>
                  {signedShareLabel(budget.total_difference)}
                </TableCell>
                <TableCell />
              </TableRow>

              {/* Medidas por setor */}
              <TableRow variant="group">
                <TableCell colSpan={6} variant="group">
                  Medidas por setor
                </TableCell>
              </TableRow>
              {panel.sector_measures.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} variant="note">
                    Nenhum setor com regra própria. O presidente pode taxar ou isentar um setor ou segmento.
                  </TableCell>
                </TableRow>
              )}
              {panel.sector_measures.map(({ measure, assets }) => {
                const waiting = measure.effective !== null && measure.effective > today;
                return (
                  <TableRow key={measure.id}>
                    <TableCell className="whitespace-normal">
                      {measureTarget(measure)}
                      <span className="text-xs text-muted-foreground"> · {assets} ativos</span>
                    </TableCell>
                    <TableCell
                      numeric
                      tone={waiting ? "warning" : measure.kind === "SECTOR_EXEMPT" ? "success" : undefined}
                    >
                      {sectorEffect(measure, baseRate, today)}
                    </TableCell>
                    <TableCell colSpan={4} numeric variant="note">
                      {waiting
                        ? "aprovada, esperando"
                        : measure.effective
                          ? `desde ${monthYear(measure.effective)}`
                          : ""}
                    </TableCell>
                  </TableRow>
                );
              })}
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

type TaxRateRowProps = {
  row: TaxRow;
  /** A linha do teto da isenção, que vira nota embaixo das vendas de ações com lucro */
  exemption: TaxRow | undefined;
  isPresident: boolean;
  onPropose: (kind?: MeasureKind) => void;
};

function TaxRateRow({ row, exemption, isPresident, onPropose }: TaxRateRowProps) {
  const kind = row.kind;
  if (!isGeneral(kind)) return null;

  return (
    <TableRow>
      <TableCell className="whitespace-normal">
        <span className="grid gap-1">
          <span className="flex flex-wrap items-center gap-1.5">
            {generalLabel(kind, row.value)}
            {TAX_PRICE[kind] && <TaxPriceHint label={generalLabel(kind, row.value)} price={TAX_PRICE[kind]} />}
            {row.promised && (
              <Badge variant="info" size="sm">
                prometido
              </Badge>
            )}
          </span>
          {exemption && isGeneral(exemption.kind) && (
            <span className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
              {generalLabel(exemption.kind, exemption.value)}:
              <b className="font-semibold text-foreground">
                {generalToday(exemption.kind, exemption.value, null).toLowerCase()}
              </b>
              {exemption.promised && (
                <Badge variant="info" size="sm">
                  prometido
                </Badge>
              )}
              <MeasureAction
                pending={exemption.pending}
                isPresident={isPresident}
                onPropose={() => onPropose(exemption.kind)}
              />
            </span>
          )}
        </span>
      </TableCell>
      <TableCell numeric>{generalToday(kind, row.value, row.top_value)}</TableCell>
      <TableCell numeric>
        <span className="text-muted-foreground">{generalToday(kind, row.default_value, row.default_top_value)}</span>
      </TableCell>
      <TableCell numeric>{revenueLabel(row.revenue)}</TableCell>
      <TableCell numeric>
        {row.difference === null ? (
          <span className="text-muted-foreground">—</span>
        ) : (
          <span className={differenceTone(row.difference)}>{signedShareLabel(row.difference)}</span>
        )}
      </TableCell>
      <TableCell numeric>
        <MeasureAction pending={row.pending} isPresident={isPresident} onPropose={() => onPropose(kind)} />
      </TableCell>
    </TableRow>
  );
}

type TaxPriceHintProps = { label: string; price: TaxPrice };

function TaxPriceHint({ label, price }: TaxPriceHintProps) {
  return (
    <InfoHint label={`O que ${label} cobra`}>
      <div className="space-y-1 text-left">
        <p>{price.definition}</p>
        <p>{price.example}</p>
        <p>{price.reading}</p>
      </div>
    </InfoHint>
  );
}
