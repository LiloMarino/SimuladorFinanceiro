import { Link } from "react-router-dom";
import { EffectSpark } from "@/shared/components/effect-spark";
import { SpendingIcon } from "@/shared/components/spending-icon";
import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { inflationTone, PHASE_SHORT, signedIpca } from "@/shared/lib/effects";
import { displayDayMonth, displayMoneyLarge } from "@/shared/lib/utils/display";
import type { GovernmentPanel, MeasureKind, SpendingRow } from "@/types";
import { shareLabel, signedShareLabel } from "../lib/budget";
import { SPENDING_INFLATION_NOW, SPENDING_COST } from "../lib/government-metrics";
import { monthYear } from "../lib/government";
import { isSpending, SPENDING_LABEL, type SpendingKind } from "@/shared/lib/spending-kinds";
import { pointsOf } from "../lib/spending";

const SUBTITLE: Record<SpendingKind, string> = {
  WELFARE_SPENDING: "Transferência para quem depende dele",
  SERVANT_RAISE: "Ganho acima da inflação, todo janeiro",
  RETIREE_RAISE: "Ganho acima da inflação, todo janeiro",
  PUBLIC_WORKS: "Também soma ao crescimento do PIB",
};

const TONE_CLASS = {
  destructive: "text-destructive",
  success: "text-success",
  default: "text-muted-foreground",
} as const;

type SpendingCardProps = {
  panel: GovernmentPanel;
  onPropose: (kind?: MeasureKind) => void;
};

/** O gasto público em vigor: as quatro medidas que o presidente muda, o resto do gasto e o quanto cada uma pesa na inflação. */
export function SpendingCard({ panel, onPropose }: SpendingCardProps) {
  const { spending } = panel;

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <div className="grid gap-0.5">
            <h2 className="text-[15px] font-semibold">Gasto público</h2>
            <span className="text-xs text-muted-foreground">
              Gasto mexe em preço: o dinheiro a mais vira consumo, a inflação sobe uns meses depois e o Banco Central
              responde com a SELIC.
            </span>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Medida</TableHead>
                <TableHead>Hoje</TableHead>
                <TableHead numeric>
                  <HeadWithHint metric={SPENDING_COST} />
                </TableHead>
                <TableHead numeric>
                  <HeadWithHint metric={SPENDING_INFLATION_NOW} />
                </TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {spending.rows.map((row) => (
                <SpendingRowView key={row.kind} row={row} isPresident={panel.is_president} onPropose={onPropose} />
              ))}

              {/* Resto do gasto do país */}
              <TableRow>
                <TableCell className="whitespace-normal">
                  <span className="grid gap-0.5 pl-11">
                    <span>Resto do gasto do país</span>
                    <span className="text-xs text-muted-foreground">
                      Saúde, educação, custeio. Não muda com as medidas.
                    </span>
                  </span>
                </TableCell>
                <TableCell variant="note">—</TableCell>
                <TableCell numeric>{shareLabel(spending.rest)}</TableCell>
                <TableCell numeric variant="note">
                  —
                </TableCell>
                <TableCell />
              </TableRow>

              {/* Gasto total */}
              <TableRow variant="current">
                <TableCell>Gasto total</TableCell>
                <TableCell>
                  {Number(spending.total_difference) !== 0 && (
                    <span className="text-xs font-normal text-muted-foreground">
                      {signedShareLabel(spending.total_difference)} desde o início
                    </span>
                  )}
                </TableCell>
                <TableCell numeric>{shareLabel(spending.total)}</TableCell>
                <TableCell numeric className={TONE_CLASS[inflationTone(spending.inflation)]}>
                  {signedIpca(spending.inflation)}
                </TableCell>
                <TableCell numeric>
                  <Link to="/economy" className="font-sans text-[13px] font-normal text-info hover:underline">
                    No painel da economia ›
                  </Link>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

function HeadWithHint({ metric }: { metric: typeof SPENDING_COST }) {
  return (
    <span className="inline-flex items-center gap-1">
      {metric.label}
      <MetricHint metric={metric} />
    </span>
  );
}

type SpendingRowViewProps = {
  row: SpendingRow;
  isPresident: boolean;
  onPropose: (kind?: MeasureKind) => void;
};

function SpendingRowView({ row, isPresident, onPropose }: SpendingRowViewProps) {
  const kind = row.kind;
  if (!isSpending(kind)) return null;
  const raise = kind === "SERVANT_RAISE" || kind === "RETIREE_RAISE";

  return (
    <TableRow>
      <TableCell className="whitespace-normal">
        <span className="flex items-center gap-3">
          <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-muted text-muted-foreground">
            <SpendingIcon kind={kind} className="size-4.5" />
          </span>
          <span className="grid gap-0.5">
            <span className="flex flex-wrap items-center gap-1.5 font-medium">
              {SPENDING_LABEL[kind]}
              {row.promised && (
                <Badge variant="info" size="sm">
                  prometido
                </Badge>
              )}
            </span>
            <span className="text-xs font-normal text-muted-foreground">{SUBTITLE[kind]}</span>
          </span>
        </span>
      </TableCell>
      <TableCell>
        <span className="grid gap-0.5">
          <span className="font-mono">
            {raise ? `${pointsOf(row.value)}% ao ano` : `${pointsOf(row.value)}% do PIB`}
          </span>
          <span className="text-xs text-muted-foreground">
            {raise ? "+ a inflação" : row.since ? `desde ${monthYear(row.since)}` : "desde o início"}
          </span>
        </span>
      </TableCell>
      <TableCell numeric>
        <span className="grid justify-items-end gap-0.5">
          <span className="font-mono">{shareLabel(row.cost)}</span>
          <span className="text-xs text-muted-foreground">
            {raise ? "a folha inteira" : `${displayMoneyLarge(row.cost_amount)}/ano`}
          </span>
        </span>
      </TableCell>
      <TableCell numeric>
        <InflationNow row={row} />
      </TableCell>
      <TableCell numeric>
        {row.pending ? (
          <Badge variant="warning" size="sm">
            {row.pending.status === "QUEUED" || !row.pending.effective
              ? "na fila"
              : `vale em ${displayDayMonth(row.pending.effective)}`}
          </Badge>
        ) : (
          isPresident && (
            <Button size="xs" variant="outline" onClick={() => onPropose(kind)}>
              Mudar
            </Button>
          )
        )}
      </TableCell>
    </TableRow>
  );
}

/** A curva do efeito da última mudança da medida, os pontos de IPCA de hoje e a fase; sem efeito, um traço. */
function InflationNow({ row }: { row: SpendingRow }) {
  if (!row.phase || row.phase === "FADED") return <span className="text-muted-foreground">—</span>;
  return (
    <span className="flex items-center justify-end gap-2.5">
      <EffectSpark curve={row.curve} elapsedMonths={row.elapsed_months} width={84} height={26} />
      <span className="grid min-w-16 justify-items-end gap-0.5">
        <span className={`font-mono font-semibold ${TONE_CLASS[inflationTone(row.inflation)]}`}>
          {signedIpca(row.inflation)}
        </span>
        <span className="text-xs text-muted-foreground">{PHASE_SHORT[row.phase]}</span>
      </span>
    </span>
  );
}
