import type { ReactNode } from "react";
import { MetricLabel } from "@/shared/components/metric-hint";
import { Slider } from "@/shared/components/ui/slider";
import { displayRatePercent } from "@/shared/lib/financial-independence";
import { displayDecimal, displayMoney, displayMoneyWhole } from "@/shared/lib/utils/display";
import { feeStep, feeToPoints, managementPerMonth, performanceExample } from "../lib/fund-fees";
import { MANAGEMENT_FEE, PERFORMANCE_FEE } from "../lib/fund-metrics";

type FeeControlsProps = {
  managementPoints: number;
  onManagementChange: (points: number) => void;
  performancePoints: number;
  onPerformanceChange: (points: number) => void;
  /** Os tetos da partida, em fração ("0.0200") */
  maxManagement: string;
  maxPerformance: string;
  /** O patrimônio em que o exemplo da administração é calculado */
  netWorth: number;
  /** O que acompanha a performance: a marca d'água de hoje */
  waterMark?: ReactNode;
};

type FeeRulerProps = {
  metric: typeof MANAGEMENT_FEE;
  suffix: string;
  points: number;
  onChange: (points: number) => void;
  cap: string;
  children: ReactNode;
};

/** Uma taxa numa régua que vai de 0 ao teto da partida, com o exemplo embaixo. */
function FeeRuler({ metric, suffix, points, onChange, cap, children }: FeeRulerProps) {
  const capPoints = feeToPoints(cap);

  return (
    <div className="grid gap-2">
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-sm font-medium">
          <MetricLabel metric={metric} />
        </span>
        <span className="font-mono text-[15px] font-semibold">
          {displayRatePercent(points / 100)} {suffix}
        </span>
      </div>
      <Slider
        aria-label={metric.label}
        min={0}
        max={capPoints}
        step={feeStep(capPoints)}
        value={points}
        onValueChange={onChange}
      />
      <div className="flex justify-between font-mono text-xs text-muted-foreground">
        <span>0%</span>
        <span>teto da partida {displayRatePercent(cap)}</span>
      </div>
      <p className="rounded-lg bg-subtle px-3 py-2 text-xs text-muted-foreground">{children}</p>
    </div>
  );
}

/** As duas taxas do gestor em réguas até o teto da partida, cada uma com um exemplo em reais. */
export function FeeControls({
  managementPoints,
  onManagementChange,
  performancePoints,
  onPerformanceChange,
  maxManagement,
  maxPerformance,
  netWorth,
  waterMark,
}: FeeControlsProps) {
  const example = performanceExample(performancePoints);

  return (
    <div className="grid gap-5">
      <FeeRuler
        metric={MANAGEMENT_FEE}
        suffix="ao ano"
        points={managementPoints}
        onChange={onManagementChange}
        cap={maxManagement}
      >
        Em {displayMoneyWhole(netWorth)} de patrimônio, são{" "}
        <b className="font-mono font-semibold text-foreground">
          {displayMoney(managementPerMonth(netWorth, managementPoints))}
        </b>{" "}
        por mês, cobrados em 12 parcelas.
      </FeeRuler>
      <FeeRuler
        metric={PERFORMANCE_FEE}
        suffix="do que passa do CDI"
        points={performancePoints}
        onChange={onPerformanceChange}
        cap={maxPerformance}
      >
        Se a cota rende 15% num CDI de 10%, os {displayDecimal(example.extraPoints)} pontos acima do CDI trazem{" "}
        <b className="font-mono font-semibold text-foreground">
          {displayDecimal(example.points)} {example.points === 1 ? "ponto" : "pontos"}
        </b>{" "}
        para você.
        {waterMark}
      </FeeRuler>
    </div>
  );
}
