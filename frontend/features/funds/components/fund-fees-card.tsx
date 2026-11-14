import { CalendarClock } from "lucide-react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { displayIsoDate, displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { HIGH_WATER_MARK, MANAGEMENT_FEE, PERFORMANCE_FEE } from "../lib/fund-metrics";
import { FundSection } from "./fund-section";

/** As taxas que o gestor recebe: o que vale hoje, a estimativa em reais, o que já recebeu e a mudança marcada. */
export function FundFeesCard({ fund, onChange }: { fund: FundDetails; onChange: () => void }) {
  const { fees } = fund;

  return (
    <FundSection
      title="Taxas que você recebe"
      action={
        <Button size="xs" variant="outline" onClick={onChange}>
          Mudar
        </Button>
      }
    >
      <div className="grid gap-3">
        <div>
          <KeyValueRow
            label={<MetricLabel metric={MANAGEMENT_FEE} />}
            value={`${displayPercent(fees.management_fee, 1, { trim: true })} ao ano`}
          />
          <KeyValueRow label="Rende por mês, em média" value={displayMoney(fees.management_monthly_estimate)} />
          <KeyValueRow
            label={<MetricLabel metric={PERFORMANCE_FEE} />}
            value={`${displayPercent(fees.performance_fee, 1, { trim: true })} do que passa do CDI`}
          />
          <KeyValueRow
            label="Performance, se fechasse hoje"
            value={fees.performance_estimate === null ? "—" : displayMoney(fees.performance_estimate)}
          />
          {fees.next_performance_on && (
            <KeyValueRow label="Próxima cobrança de performance" value={displayIsoDate(fees.next_performance_on)} />
          )}
          <KeyValueRow
            label={<MetricLabel metric={HIGH_WATER_MARK} />}
            value={fees.high_water_mark === null ? "—" : displayMoney(fees.high_water_mark)}
          />
          <KeyValueRow label="Recebido em 12 meses" value={displayMoney(fees.received_12m)} total />
        </div>
        {fund.pending_from && (
          <Alert variant="info">
            <CalendarClock />
            <AlertDescription>
              Taxas novas ({displayPercent(fund.pending_management_fee ?? fees.management_fee, 1, { trim: true })} ao
              ano e {displayPercent(fund.pending_performance_fee ?? fees.performance_fee, 1, { trim: true })} de
              performance) valem a partir de {displayIsoDate(fund.pending_from)}.
            </AlertDescription>
          </Alert>
        )}
      </div>
    </FundSection>
  );
}
