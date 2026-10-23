import { MetricHint } from "@/shared/components/metric-hint";
import { Kpi } from "@/shared/components/kpi";
import { Card, CardContent } from "@/shared/components/ui/card";
import { LEVERAGE } from "@/shared/lib/credit-metrics";
import { displayDayMonth, displayMoney, displayMonthName, displaySignedMoney } from "@/shared/lib/utils/display";
import type { CreditOverview } from "@/types";

type CreditSummaryProps = { overview: CreditOverview };

const pluralLoans = (count: number) => `${count} ${count === 1 ? "empréstimo" : "empréstimos"}`;

// O mês aparece uma vez só quando as duas datas caem nele: "entre 05 e 10 abr"
const displayRange = (first: string, last: string) => {
  const [firstDay, firstMonth] = displayDayMonth(first).split(" ");
  const [lastDay, lastMonth] = displayDayMonth(last).split(" ");
  return firstMonth === lastMonth
    ? `entre ${firstDay} e ${lastDay} ${lastMonth}`
    : `entre ${firstDay} ${firstMonth} e ${lastDay} ${lastMonth}`;
};

/** Faixa de números do topo: dívida, patrimônio líquido, alavancagem e as parcelas do próximo mês. */
export function CreditSummary({ overview }: CreditSummaryProps) {
  const hasDebt = Number(overview.debt) > 0;
  const monthName = overview.next_installments_month ? displayMonthName(overview.next_installments_month) : null;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {/* Dívida */}
          <Kpi
            label="Dívida"
            value={hasDebt ? displaySignedMoney(-Number(overview.debt)) : displayMoney(0)}
            tone={hasDebt ? "destructive" : "default"}
            note={hasDebt ? pluralLoans(overview.open_loans) : "Nenhum empréstimo"}
          />

          {/* Patrimônio líquido */}
          <Kpi
            label="Patrimônio"
            value={displaySignedMoney(overview.networth)}
            tone={Number(overview.networth) < 0 ? "destructive" : "default"}
            note={`${displayMoney(overview.assets)} em ativos menos a dívida`}
          />

          {/* Alavancagem */}
          <Kpi
            label={
              <>
                Alavancagem
                <MetricHint metric={LEVERAGE} />
              </>
            }
            value={overview.leverage === null ? "—" : LEVERAGE.format(overview.leverage)}
            note="Entra na nota de risco"
          />

          {/* Parcelas do próximo mês */}
          <Kpi
            label={monthName ? `Parcelas de ${monthName}` : "Próximas parcelas"}
            value={displayMoney(overview.next_installments_total)}
            note={
              overview.next_installments_first && overview.next_installments_last
                ? `${displayRange(overview.next_installments_first, overview.next_installments_last)} · ${
                    overview.cash_covers_next ? "o caixa cobre" : "o caixa não cobre"
                  }`
                : hasDebt
                  ? "Nada a vencer"
                  : "Sem parcelas"
            }
          />
        </div>
      </CardContent>
    </Card>
  );
}
