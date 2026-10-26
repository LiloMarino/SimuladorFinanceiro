import type { ReactNode } from "react";
import { InfoHint } from "@/shared/components/info-hint";
import type { MetricInfo } from "@/shared/lib/metric-info";
import { LearnMoreLink } from "@/shared/components/learn-more-link";

interface Props {
  metric: MetricInfo;
  /** Bloco depois do texto da dica, como a régua com o valor de hoje */
  extra?: ReactNode;
}

export function MetricHint({ metric, extra }: Props) {
  return (
    <InfoHint label={`O que é ${metric.label}`} interactive={metric.topic !== undefined}>
      <div className="space-y-1 text-left">
        <p>{metric.definition}</p>
        <p>{metric.example}</p>
        <p>{metric.reading}</p>
        {extra}
        {metric.topic && <LearnMoreLink topic={metric.topic} />}
      </div>
    </InfoHint>
  );
}

/** Rótulo de coluna ou de card com a dica ao lado. */
export function MetricLabel({ metric }: Props) {
  return (
    <span className="inline-flex items-center gap-1">
      {metric.label}
      <MetricHint metric={metric} />
    </span>
  );
}
