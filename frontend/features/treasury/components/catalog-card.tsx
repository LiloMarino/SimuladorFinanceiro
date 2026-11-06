import { cn } from "@/shared/lib/utils";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { MetricLabel } from "@/shared/components/metric-hint";
import { EQUIVALENT_TODAY, SOLD_UNTIL, TODAY_RATE } from "@/shared/lib/treasury-metrics";
import { displayPercent } from "@/shared/lib/utils/display";
import type { RateIndex, TreasuryCatalog, TreasuryTitle } from "@/types";
import {
  baseRateCaption,
  displayDay,
  displayMonthYear,
  indexDotClass,
  pointsOf,
  shortTitleName,
  termLabel,
  treasuryRateLabel,
} from "../lib/treasury";
import { RateBar } from "./rate-bar";

const GROUPS: { rateIndex: RateIndex; label: string; hint: string }[] = [
  {
    rateIndex: "SELIC",
    label: "Selic",
    hint: "Rende a SELIC do dia, mais a taxa. O preço quase não oscila: serve para a reserva.",
  },
  {
    rateIndex: "Prefixado",
    label: "Prefixado",
    hint: "Taxa fechada na compra: você sabe quanto recebe no vencimento.",
  },
  {
    rateIndex: "IPCA",
    label: "IPCA+",
    hint: "A inflação mais uma taxa fixa. Protege do IPCA no prazo longo.",
  },
];

type CatalogCardProps = {
  catalog: TreasuryCatalog;
  today: string;
  onInvest: (title: TreasuryTitle) => void;
};

/** Os seis títulos à venda, agrupados por indexador, com a taxa aberta em base e prêmio. */
export function CatalogCard({ catalog, today, onInvest }: CatalogCardProps) {
  const withGovernment = catalog.thermometer !== null;
  // Com a taxa equivalente escondida a tabela perde a coluna "Equivale hoje"
  const showEquivalent = catalog.titles.some((title) => title.effective_annual_rate !== null);
  const columns = showEquivalent ? 5 : 4;

  return (
    <Card className="overflow-hidden">
      {/* Cabeçalho */}
      <CardHeader>
        <CardTitle>Títulos à venda</CardTitle>
        <CardDescription>
          Seis títulos, sempre os mesmos por anos. A taxa de todos é revista no fechamento do mês; quem compra trava a
          taxa da compra.
        </CardDescription>
        {withGovernment && (
          <div className="mt-0.5 flex items-center gap-3 text-xs text-secondary-foreground">
            <span className="flex items-center gap-1.5">
              <span aria-hidden className="h-1.5 w-3.5 rounded-full bg-risk-base" />
              taxa base
            </span>
            <span className="flex items-center gap-1.5">
              <span aria-hidden className="h-1.5 w-3.5 rounded-full bg-risk-premium" />
              prêmio de risco do país
            </span>
          </div>
        )}
      </CardHeader>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Título</TableHead>
            <TableHead>
              <MetricLabel metric={TODAY_RATE} />
            </TableHead>
            {showEquivalent && (
              <TableHead numeric>
                <MetricLabel metric={EQUIVALENT_TODAY} />
              </TableHead>
            )}
            <TableHead>
              <MetricLabel metric={SOLD_UNTIL} />
            </TableHead>
            <TableHead>
              <span className="sr-only">Investir</span>
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {GROUPS.map((group) => {
            const titles = catalog.titles.filter((title) => title.rate_index === group.rateIndex);
            if (titles.length === 0) return null;
            return (
              <GroupRows key={group.rateIndex} group={group} columns={columns}>
                {titles.map((title) => (
                  <TableRow key={title.asset_uuid}>
                    <TableCell>
                      <div className="grid gap-1">
                        <b className="font-semibold">{title.name}</b>
                        <span className="text-xs text-muted-foreground">
                          vence {displayDay(title.maturity_date)} · {termLabel(title.maturity_date, today)}
                        </span>
                        {title.replacement_name && (
                          <Badge variant="warning" size="sm" className="w-fit">
                            sai no fechamento de dezembro · entra o {shortTitleName(title.replacement_name)}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="grid gap-1">
                        <b className="font-mono font-semibold">{treasuryRateLabel(title.rate_index, title.rate)}</b>
                        <RateBar base={title.base_rate} rate={title.rate} />
                        <span className="text-xs text-muted-foreground">
                          {Number(title.premium) === 0 ? (
                            "0 de prêmio"
                          ) : (
                            <>
                              {baseRateCaption(title.rate_index, title.base_rate)}{" "}
                              <b className="font-semibold text-warning">{pointsOf(title.premium)} prêmio</b>
                            </>
                          )}
                        </span>
                      </div>
                    </TableCell>
                    {showEquivalent && (
                      <TableCell numeric>
                        <div className="grid gap-0.5">
                          <span>
                            {title.effective_annual_rate === null ? "—" : displayPercent(title.effective_annual_rate)}
                          </span>
                          <span className="text-xs font-normal text-muted-foreground">ao ano</span>
                        </div>
                      </TableCell>
                    )}
                    <TableCell>
                      <span className="font-mono">{displayMonthYear(title.sold_until)}</span>
                    </TableCell>
                    <TableCell>
                      <Button size="sm" onClick={() => onInvest(title)}>
                        Investir
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </GroupRows>
            );
          })}
        </TableBody>
      </Table>
    </Card>
  );
}

type GroupRowsProps = {
  group: (typeof GROUPS)[number];
  columns: number;
  children: React.ReactNode;
};

/** A linha-título de um indexador seguida das linhas dos seus títulos. */
function GroupRows({ group, columns, children }: GroupRowsProps) {
  return (
    <>
      <TableRow variant="group">
        <TableCell variant="group" colSpan={columns}>
          <span className="flex items-center gap-2">
            <span aria-hidden className={cn("size-2.5 rounded-full", indexDotClass(group.rateIndex))} />
            {group.label}
            <span className="text-xs font-normal text-muted-foreground">{group.hint}</span>
          </span>
        </TableCell>
      </TableRow>
      {children}
    </>
  );
}
