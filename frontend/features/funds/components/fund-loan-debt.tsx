import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { LOAN_DEBT } from "@/shared/lib/fund-metrics";
import { displayMoney } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";

type FundLoanDebtProps = { debt: FundDetails["fees"]["loan_debt"] };

/** O saldo devedor dos empréstimos da gestora; some quando não há dívida. */
export function FundLoanDebt({ debt }: FundLoanDebtProps) {
  if (Number(debt) <= 0) return null;
  return <KeyValueRow label={<MetricLabel metric={LOAN_DEBT} />} value={`−${displayMoney(debt)}`} />;
}
