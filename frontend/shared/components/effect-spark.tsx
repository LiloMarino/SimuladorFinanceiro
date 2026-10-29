import { curvePath } from "@/shared/lib/effects";
import { cn } from "@/shared/lib/utils";

type EffectSparkProps = {
  /** Pontos de IPCA mês a mês desde que a medida passou a valer */
  curve: readonly (string | number)[];
  /** Quantos meses já correram: o ponto marca o mês de hoje na curva */
  elapsedMonths: number | null;
  width: number;
  height: number;
  className?: string;
};

/** A curva do efeito de uma medida em miniatura, com a linha do zero e o ponto do mês de hoje. */
export function EffectSpark({ curve, elapsedMonths, width, height, className }: EffectSparkProps) {
  const values = curve.map(Number);
  const path = curvePath(values, width, height);
  if (!path) return null;
  const raising = Math.max(...values) >= Math.abs(Math.min(...values));
  const index = elapsedMonths === null ? null : Math.min(Math.max(elapsedMonths, 0), values.length - 1);
  const high = Math.max(0, ...values);
  const low = Math.min(0, ...values);
  const y = (value: number) => 3 + ((high - value) / (high - low || 1)) * (height - 6);

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
      aria-hidden
      className={cn("block", className)}
    >
      <line x1={0} x2={width} y1={path.zero} y2={path.zero} className="stroke-border" strokeDasharray="3 3" />
      <path
        d={path.line}
        fill="none"
        strokeWidth={2}
        strokeLinejoin="round"
        className={raising ? "stroke-warning" : "stroke-success"}
      />
      {index !== null && (
        <circle
          cx={(index / (values.length - 1)) * width}
          cy={y(values[index] ?? 0)}
          r={3}
          className={raising ? "fill-warning" : "fill-success"}
        />
      )}
    </svg>
  );
}
