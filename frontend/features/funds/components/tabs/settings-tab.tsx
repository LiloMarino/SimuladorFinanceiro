import { CalendarClock } from "lucide-react";
import { useState } from "react";
import { FundSection } from "@/shared/components/fund-section";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { MarkedSlider } from "@/shared/components/marked-slider";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Spinner } from "@/shared/components/ui/spinner";
import { DISTRIBUTION_RATE } from "@/shared/lib/fund-metrics";
import { displayMoney, displayMonthName, displayPercent } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";
import { useSetFundDistribution } from "../../hooks/mutations/useSetFundDistribution";
import { DISTRIBUTION_STEP, distributedOf, rateToBody, rateToPoints } from "../../lib/fund-distribution";
import type { FundTabActions } from "../../lib/fund-tabs";
import { FundFeesCard } from "../fund-fees-card";

const MARK_GAP = 12;

/** O card "Parte do lucro distribuída": a régua, o que ela muda por cota e o botão de salvar. */
function DistributionCard({ fund }: { fund: FundDetails }) {
  const plan = fund.distribution;
  const today = rateToPoints(fund.distribution_rate);
  const start = rateToPoints(fund.pending_distribution_rate ?? fund.distribution_rate);
  const [points, setPoints] = useState(start);
  const setDistribution = useSetFundDistribution(fund.id);

  // O rendimento só vai aos cotistas de fora: o Mercado não recebe
  const outside = fund.holders
    .filter((holder) => holder.kind !== "maker")
    .reduce((sum, holder) => sum + Number(holder.quotas), 0);
  const total = Number(fund.quotas);
  const profit = Number(plan.realized_profit);
  const perQuotaAt = (value: number) => (outside > 0 ? distributedOf(profit, value) / outside : 0);
  const stays = profit > 0 && total > 0 ? (profit - distributedOf(profit, points)) / total : 0;
  const nextMonth = displayMonthName(plan.data_com_on, 1);
  // A marca de hoje substitui a ponta da régua que ficaria a menos de MARK_GAP pontos dela
  const marks = [
    { value: 0, label: "0%" },
    { value: today, label: `hoje ${today}%` },
    { value: 100, label: "100%" },
  ].filter((mark) => mark.label.startsWith("hoje") || Math.abs(mark.value - today) >= MARK_GAP);

  return (
    <FundSection
      title={<MetricLabel metric={DISTRIBUTION_RATE} />}
      action={
        <Button
          size="xs"
          variant="fund"
          disabled={points === start || setDistribution.isPending}
          onClick={() => setDistribution.mutate({ distribution_rate: rateToBody(points) })}
        >
          {setDistribution.isPending && <Spinner />}
          Salvar {points}%
        </Button>
      }
    >
      <div className="grid gap-4">
        <div className="grid gap-2">
          <div className="flex items-baseline justify-between gap-3">
            <span className="text-sm font-medium">Parte do lucro realizado que vira rendimento</span>
            <span className="font-mono text-[15px] font-semibold">{points}%</span>
          </div>
          <MarkedSlider
            aria-label={DISTRIBUTION_RATE.label}
            min={0}
            max={100}
            step={DISTRIBUTION_STEP}
            value={points}
            onValueChange={setPoints}
            marks={marks}
          />
        </div>

        {/* Prévia por cota */}
        <div>
          <KeyValueRow
            label={`Com o lucro de ${displayMonthName(plan.data_com_on)} até hoje`}
            value={displayMoney(plan.realized_profit)}
          />
          <KeyValueRow label={`Hoje, com ${today}%`} value={`${displayMoney(perQuotaAt(today))} por cota`} />
          <KeyValueRow label={`Com ${points}%`} value={`${displayMoney(perQuotaAt(points))} por cota`} />
          <KeyValueRow label="Fica no caixa" value={`+${displayMoney(stays)} por cota`} total />
        </div>

        <Alert variant="info">
          <CalendarClock />
          <AlertDescription>
            Vale a partir do rendimento de {nextMonth}. O rendimento deste mês ainda sai pela parte de hoje (
            {displayPercent(plan.rate, 0)}).
          </AlertDescription>
        </Alert>
      </div>
    </FundSection>
  );
}

type SettingsTabProps = { fund: FundDetails; actions: Pick<FundTabActions, "open"> };

/** As configurações do gestor: as taxas e a parte do lucro distribuída. */
export function SettingsTab({ fund, actions }: SettingsTabProps) {
  return (
    <div className="grid items-start gap-5 pt-3 xl:grid-cols-2">
      <FundFeesCard fund={fund} onChange={() => actions.open("fees")} />
      <DistributionCard fund={fund} />
    </div>
  );
}
