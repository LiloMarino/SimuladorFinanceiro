import { CalendarClock, TriangleAlert } from "lucide-react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { PageControls } from "@/shared/components/page-controls";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { usePagedRows } from "@/shared/hooks/usePagedRows";
import { displayIsoDate, displayMoney, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { isLosingMonth } from "@/shared/lib/fund-view";
import { DISTRIBUTION_RATE, REALIZED_PROFIT, YIELD_PER_QUOTA } from "@/shared/lib/fund-metrics";
import { FundSection } from "@/shared/components/fund-section";

type Distribution = FundDetails["distributions"][number];

const PAGE_SIZE = 6;

/** A linha do histórico: o lucro do mês, o que foi pago, por cota e quando; mês de prejuízo não paga. */
function DistributionRow({ row }: { row: Distribution }) {
  const losing = isLosingMonth(row);
  const paid = row.paid_on !== null;

  return (
    <TableRow>
      <TableCell variant="note">{displayShortDate(row.data_com)}</TableCell>
      <TableCell numeric>{displayMoney(row.realized_profit)}</TableCell>
      <TableCell numeric>
        {losing ? "Mês de prejuízo" : paid && row.paid !== null ? displayMoney(row.paid) : "A pagar"}
      </TableCell>
      <TableCell numeric>{paid && row.paid_per_quota !== null ? displayMoney(row.paid_per_quota) : "—"}</TableCell>
      <TableCell numeric variant="note">
        {row.paid_on ? displayShortDate(row.paid_on) : displayIsoDate(row.data_com)}
      </TableCell>
    </TableRow>
  );
}

/** Os rendimentos da gestora: a parte distribuída, o mês em curso e o histórico do que foi pago. */
export function FundDistributionsCard({ fund, onChange }: { fund: FundDetails; onChange?: () => void }) {
  const plan = fund.distribution;
  const paging = usePagedRows(fund.distributions, PAGE_SIZE);

  return (
    <FundSection
      title="Rendimentos"
      action={
        onChange && (
          <Button size="xs" variant="outline" onClick={onChange}>
            Mudar a parte distribuída
          </Button>
        )
      }
    >
      <div className="grid gap-3">
        <div>
          <KeyValueRow
            label={<MetricLabel metric={DISTRIBUTION_RATE} />}
            value={`${displayPercent(plan.rate, 0)} do lucro realizado`}
          />
          <KeyValueRow label={<MetricLabel metric={REALIZED_PROFIT} />} value={displayMoney(plan.realized_profit)} />
          <KeyValueRow
            label={<MetricLabel metric={YIELD_PER_QUOTA} />}
            value={`${displayMoney(plan.projected_per_quota)} por cota, se fechasse hoje`}
          />
          <KeyValueRow label="Rende neste mês, se fechasse hoje" value={displayMoney(plan.projected)} />
          <KeyValueRow label="Apuração (data-com)" value={displayIsoDate(plan.data_com_on)} />
          <KeyValueRow label="Pagamento aos cotistas" value={displayIsoDate(plan.pay_on)} total />
        </div>
        {!plan.cash_enough && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertDescription>
              O caixa de {displayMoney(plan.cash)} não cobre os {displayMoney(plan.projected)} do mês: cada cota
              receberia só o que o caixa dividido pelas cotas der.
            </AlertDescription>
          </Alert>
        )}
        {plan.pending_rate !== null && plan.pending_from && (
          <Alert variant="info">
            <CalendarClock />
            <AlertDescription>
              A parte nova de {displayPercent(plan.pending_rate, 0)} vale a partir de{" "}
              {displayIsoDate(plan.pending_from)}.
            </AlertDescription>
          </Alert>
        )}
        {fund.distributions.length === 0 ? (
          <p className="text-[13px] text-muted-foreground">
            Nenhum rendimento apurado ainda: o primeiro sai no último pregão do mês.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Mês</TableHead>
                <TableHead numeric>Lucro realizado</TableHead>
                <TableHead numeric>Distribuído</TableHead>
                <TableHead numeric>Por cota</TableHead>
                <TableHead numeric>Pago em</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paging.shown.map((row) => (
                <DistributionRow key={row.data_com} row={row} />
              ))}
            </TableBody>
          </Table>
        )}
        <div className="flex justify-end">
          <PageControls paging={paging} unit="meses" />
        </div>
      </div>
    </FundSection>
  );
}
