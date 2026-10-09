import { InfoHint } from "@/shared/components/info-hint";
import type { RiskMetric } from "../lib/risk-metrics";

interface Props {
  metric: RiskMetric;
}

export function RiskMetricHint({ metric }: Props) {
  return (
    <InfoHint label={`O que é ${metric.label}`}>
      <div className="space-y-1 text-left">
        <p>{metric.definition}</p>
        <p>{metric.example}</p>
        <p>{metric.reading}</p>
        <p className="opacity-70">{metric.unavailable}</p>
      </div>
    </InfoHint>
  );
}
