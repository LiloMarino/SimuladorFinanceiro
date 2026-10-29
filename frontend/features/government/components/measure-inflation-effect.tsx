import type { ReactNode } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { MetricHint } from "@/shared/components/metric-hint";
import { cn } from "@/shared/lib/utils";
import { displayPercent } from "@/shared/lib/utils/display";
import type { InflationEffect } from "@/types";
import { INFLATION_EXPECTED } from "../lib/government-metrics";
import { curvePath, inflationTone, signedIpca, signedStocks } from "@/shared/lib/effects";

const TONE_CLASS = { success: "text-success", destructive: "text-destructive", default: "text-foreground" } as const;
const CURVE_WIDTH = 600;
const CURVE_HEIGHT = 104;

function Line({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-mono font-semibold">{children}</dd>
    </div>
  );
}

type MeasureInflationEffectProps = { effect: InflationEffect };

/** O que a medida de gasto faz com a inflação, a SELIC e a bolsa: a curva do efeito mês a mês e os números do pico. */
export function MeasureInflationEffect({ effect }: MeasureInflationEffectProps) {
  const peak = Number(effect.peak);
  const raising = peak > 0;
  const tone = inflationTone(effect.peak);
  const curve = curvePath(
    effect.curve.map((point) => Number(point.points)),
    CURVE_WIDTH,
    CURVE_HEIGHT,
  );
  const growth = Number(effect.growth);

  return (
    <div
      className={cn(
        "grid gap-2.5 rounded-lg border p-3.5",
        raising ? "border-warning/30 bg-warning-soft/40" : "border-success/30 bg-success-soft/40",
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <span className="inline-flex items-center gap-1 text-sm font-medium">
          {INFLATION_EXPECTED.label}
          <MetricHint metric={INFLATION_EXPECTED} />
        </span>
        <Badge variant="secondary" size="sm">
          a sala vê na fila
        </Badge>
      </div>

      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className={cn("font-mono text-[26px] leading-none font-semibold", TONE_CLASS[tone])}>
          {signedIpca(effect.peak)} ponto
        </span>
        <span className="text-[13px]">no IPCA de 12 meses, no pico</span>
      </div>

      {curve && (
        <svg
          viewBox={`0 0 ${CURVE_WIDTH} ${CURVE_HEIGHT}`}
          role="img"
          aria-label="Pontos de IPCA que a medida soma mês a mês"
          className="block h-auto w-full"
        >
          <line
            x1={0}
            x2={CURVE_WIDTH}
            y1={curve.zero}
            y2={curve.zero}
            className="stroke-border"
            strokeDasharray="4 4"
          />
          <path
            d={curve.line}
            fill="none"
            strokeWidth={2.5}
            strokeLinejoin="round"
            className={raising ? "stroke-warning" : "stroke-success"}
          />
        </svg>
      )}

      <dl className="grid gap-1 text-[12.5px]">
        <Line label="IPCA 12 meses no pico, se nada mais mudar">
          {displayPercent(effect.ipca_before)} → {displayPercent(effect.ipca_after)}
        </Line>
        <Line label={`SELIC, que o Banco Central ${raising ? "sobe" : "corta"} 1,5 vez o tanto`}>
          {displayPercent(effect.selic_before)} → {displayPercent(effect.selic_after)}
        </Line>
        <Line label={`Bolsa no trimestre ${raising ? "da alta" : "do corte"} da SELIC`}>
          {signedStocks(effect.stocks)}
          <span className="font-normal text-muted-foreground">, mais nas ações de beta alto</span>
        </Line>
        {growth !== 0 && (
          <Line label="Crescimento do PIB, no pico">
            {growth > 0 ? "+" : "−"}
            {Math.abs(growth).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} ponto
          </Line>
        )}
      </dl>

      <p className="text-xs leading-normal text-muted-foreground">
        {raising
          ? "Com mais gasto, as famílias consomem mais e os preços sobem meses depois. O Banco Central responde subindo a SELIC, e a bolsa tende a cair no trimestre da alta."
          : "Com menos gasto, as famílias consomem menos e os preços sobem mais devagar meses depois. O Banco Central responde cortando a SELIC, e a bolsa tende a subir no trimestre do corte."}{" "}
        O efeito enche em 6 meses e cai pela metade a cada 12.
      </p>
    </div>
  );
}
