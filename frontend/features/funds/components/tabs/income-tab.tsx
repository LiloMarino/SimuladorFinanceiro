import { CalendarClock, TriangleAlert } from "lucide-react";
import { FundSection } from "@/shared/components/fund-section";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { PageControls } from "@/shared/components/page-controls";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { usePagedRows } from "@/shared/hooks/usePagedRows";
import { DIVIDEND_YIELD, DISTRIBUTION_RATE, REALIZED_PROFIT, YIELD_PER_QUOTA } from "@/shared/lib/fund-metrics";
import { isLosingMonth } from "@/shared/lib/fund-view";
import {
  displayIsoDate,
  displayMoney,
  displayMonthName,
  displayPercent,
  displayShortDate,
  displayShortMonthYear,
} from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import type { FundTabActions } from "../../lib/fund-tabs";
import { fundYield } from "../../lib/fund-yield";

type Distribution = FundDetails["distributions"][number];

const PAGE_SIZE = 6;

type IncomeTabProps = { fund: FundDetails; actions: Pick<FundTabActions, "goTo">; manager: boolean };

/** O card do mês em curso: o lucro realizado até hoje, a parte distribuída e o que cada cota receberia. */
function CurrentMonthCard({ fund, actions, manager }: IncomeTabProps) {
  const plan = fund.distribution;

  return (
    <FundSection
      title={`Rendimento de ${displayMonthName(plan.data_com_on)}`}
      action={
        manager && (
          <Button size="xs" variant="outline" onClick={() => actions.goTo("settings")}>
            Mudar a parte distribuída
          </Button>
        )
      }
    >
      <div className="grid gap-3">
        <div>
          <KeyValueRow label={<MetricLabel metric={REALIZED_PROFIT} />} value={displayMoney(plan.realized_profit)} />
          <KeyValueRow
            label={<MetricLabel metric={DISTRIBUTION_RATE} />}
            value={`${displayPercent(plan.rate, 0)} do lucro realizado`}
          />
          <KeyValueRow
            label={<MetricLabel metric={YIELD_PER_QUOTA} />}
            value={displayMoney(plan.projected_per_quota)}
            note={`Previsto para os cotistas, se o mês fechasse hoje (${displayMoney(plan.projected)} no total)`}
          />
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
      </div>
    </FundSection>
  );
}

/** O card "Quanto a cota paga": o dividend yield e o que já foi pago por cota. */
function YieldCard({ fund }: { fund: FundDetails }) {
  const result = fundYield(fund);
  const paidSoFar = fund.distributions.reduce((sum, row) => sum + Number(row.paid_per_quota ?? 0), 0);

  return (
    <FundSection title="Quanto a cota paga">
      <div>
        <KeyValueRow
          label={<MetricLabel metric={DIVIDEND_YIELD} />}
          value={result.rate === null ? "—" : `${displayPercent(result.rate, 1)} ao ano`}
          note={
            result.rate === null
              ? "Ainda sem rendimento pago"
              : `${displayMoney(result.perQuota)} pagos por cota em 12 meses ÷ ${displayMoney(result.base)} de preço`
          }
        />
        <KeyValueRow label="Pago até agora" value={`${displayMoney(paidSoFar)} por cota`} />
        <KeyValueRow
          label="Último pago"
          value={result.lastPerQuota === null ? "—" : `${displayMoney(result.lastPerQuota)} por cota`}
          note={result.lastPaidOn ? `Em ${displayIsoDate(result.lastPaidOn)}` : undefined}
        />
      </div>
    </FundSection>
  );
}

/** A linha do histórico: o mês, o lucro, a parte distribuída, o que foi pago e quando. */
function HistoryRow({ row }: { row: Distribution }) {
  const losing = isLosingMonth(row);
  const paid = row.paid_on !== null;

  return (
    <TableRow>
      <TableCell>
        <span className="flex items-center gap-2">
          {displayShortMonthYear(row.data_com)}
          {!paid && !losing && (
            <Badge variant="warning" size="tag">
              a pagar
            </Badge>
          )}
        </span>
      </TableCell>
      <TableCell numeric>{displayMoney(row.realized_profit)}</TableCell>
      <TableCell numeric>{displayPercent(row.rate, 0)}</TableCell>
      <TableCell numeric>
        {losing ? "Mês de prejuízo" : paid && row.paid !== null ? displayMoney(row.paid) : "—"}
      </TableCell>
      <TableCell numeric>{paid && row.paid_per_quota !== null ? displayMoney(row.paid_per_quota) : "—"}</TableCell>
      <TableCell numeric variant="note">
        {displayShortDate(row.data_com)}
      </TableCell>
      <TableCell numeric variant="note">
        {row.paid_on ? displayShortDate(row.paid_on) : "—"}
      </TableCell>
    </TableRow>
  );
}

/** O histórico de rendimentos, do mais novo ao mais antigo, de 6 em 6 meses. */
function HistoryCard({ fund }: { fund: FundDetails }) {
  const rows = [...fund.distributions].sort((a, b) => b.data_com.localeCompare(a.data_com));
  const paging = usePagedRows(rows, PAGE_SIZE);

  return (
    <FundSection title="Histórico" action={<PageControls paging={paging} unit="meses" />}>
      {rows.length === 0 ? (
        <p className="text-[13px] text-muted-foreground">
          Nenhum rendimento apurado ainda: o primeiro sai no último pregão do mês.
        </p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Mês</TableHead>
              <TableHead numeric>Lucro realizado</TableHead>
              <TableHead numeric>Parte distribuída</TableHead>
              <TableHead numeric>Distribuído</TableHead>
              <TableHead numeric>Por cota</TableHead>
              <TableHead numeric>Data-com</TableHead>
              <TableHead numeric>Pago em</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paging.shown.map((row) => (
              <HistoryRow key={row.data_com} row={row} />
            ))}
          </TableBody>
        </Table>
      )}
    </FundSection>
  );
}

/** Os rendimentos: o mês em curso, o quanto a cota paga e o histórico do que foi pago. */
export function IncomeTab({ fund, actions, manager }: IncomeTabProps) {
  return (
    <div className="grid gap-5 pt-3">
      <div className="grid items-start gap-5 xl:grid-cols-2">
        <CurrentMonthCard fund={fund} actions={actions} manager={manager} />
        <YieldCard fund={fund} />
      </div>
      <HistoryCard fund={fund} />
    </div>
  );
}
