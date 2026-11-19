import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { FEE_PAYABLE } from "@/shared/lib/fund-metrics";
import { displayMoney } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";

type FundPayableFeeProps = { payable: FundDetails["fees"]["payable"] };

/** A taxa que o caixa não cobriu, com o valor em aberto; some quando não há nada a pagar. */
export function FundPayableFee({ payable }: FundPayableFeeProps) {
  if (Number(payable) <= 0) return null;
  return <KeyValueRow label={<MetricLabel metric={FEE_PAYABLE} />} value={`−${displayMoney(payable)}`} />;
}
