import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { ISSUANCE_ESTIMATE } from "@/shared/lib/fund-metrics";
import type { FundIssuanceEstimate } from "@/types";
import { emptyEstimateReason, estimateNote, estimateRaisedText, isEmptyEstimate } from "../lib/fund-issuance-estimate";

type IssuanceEstimateProps = {
  estimate: FundIssuanceEstimate;
  /** Quando bots e Mercado decidem: "no último pregão da sobra" */
  decidesAt: string;
};

/** A captação que bots e Mercado devem trazer; a faixa vazia diz o que falta para eles comprarem. */
export function IssuanceEstimate({ estimate, decidesAt }: IssuanceEstimateProps) {
  const empty = isEmptyEstimate(estimate);

  return (
    <>
      <KeyValueRow
        label={<MetricLabel metric={ISSUANCE_ESTIMATE} />}
        note={
          empty
            ? `Bots e Mercado decidem ${decidesAt}`
            : `${estimateNote(estimate)}. Bots e Mercado decidem ${decidesAt}`
        }
        value={estimateRaisedText(estimate)}
        valueClassName="shrink-0 whitespace-nowrap"
      />
      {empty && <p className="py-1.5 text-xs text-muted-foreground">{emptyEstimateReason(estimate)}</p>}
    </>
  );
}
