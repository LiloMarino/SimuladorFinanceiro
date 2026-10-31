import { cn } from "@/shared/lib/utils";
import type { ChallengeBar } from "@/types";
import {
  axisTicks,
  chartPadding,
  chartScale,
  displayTick,
  HIDDEN_CANDLES,
  SHOWN_CANDLES,
  type ChartBox,
} from "../lib/chart-geometry";

/** Cada vela que entra na revelação demora isto depois da anterior. */
const ENTRY_STEP_MS = 400;

interface CandleChartProps {
  bars: ChallengeBar[];
  /** As 5 velas que entram na revelação, uma a uma; antes dela, a faixa fica reservada e tracejada. */
  after?: ChallengeBar[] | undefined;
  box: ChartBox;
  className?: string | undefined;
}

/** O recorte em velas, com o eixo em % desde a abertura da primeira: o preço em si não aparece. */
export function CandleChart({ bars, after, box, className }: CandleChartProps) {
  const scale = chartScale([...bars, ...(after ?? [])], box);
  const ticks = axisTicks(scale.min, scale.max);
  const slotsLeft = scale.x(SHOWN_CANDLES) - scale.step / 2;
  const slotsWidth = scale.step * HIDDEN_CANDLES;

  return (
    <svg
      viewBox={`0 0 ${box.width} ${box.height}`}
      className={cn("block h-auto max-h-[calc(100svh-29rem)] min-h-60 w-full", className)}
      role="img"
      aria-label={
        after
          ? "Gráfico de velas com as 5 velas seguintes reveladas"
          : "Gráfico de velas do recorte, com espaço reservado para os próximos 5 pregões"
      }
    >
      {ticks.map((tick) => (
        <g key={tick} className="text-muted-foreground">
          <line
            x1={chartPadding.left}
            x2={box.width - chartPadding.right}
            y1={scale.y(tick)}
            y2={scale.y(tick)}
            stroke="currentColor"
            strokeOpacity={tick === 0 ? 0.5 : 0.15}
            strokeDasharray={tick === 0 ? "4 4" : undefined}
          />
          <text
            x={chartPadding.left - 8}
            y={scale.y(tick)}
            textAnchor="end"
            dominantBaseline="middle"
            fontSize={11}
            fill="currentColor"
            className="font-mono"
          >
            {displayTick(tick)}
          </text>
        </g>
      ))}

      <rect
        x={slotsLeft}
        y={chartPadding.top}
        width={slotsWidth}
        height={box.height - chartPadding.top - chartPadding.bottom}
        rx={6}
        className={cn("text-muted-foreground", after ? "fill-subtle" : "fill-none")}
        stroke="currentColor"
        strokeOpacity={after ? 0.15 : 0.5}
        strokeDasharray="5 4"
      />
      {!after && (
        <text
          x={slotsLeft + slotsWidth / 2}
          y={chartPadding.top + 16}
          textAnchor="middle"
          fontSize={12}
          fill="currentColor"
          className="text-muted-foreground"
        >
          próximos 5
        </text>
      )}

      {bars.map((bar, index) => (
        <Candle key={index} bar={bar} x={scale.x(index)} width={scale.step * 0.62} y={scale.y} />
      ))}
      {after?.map((bar, index) => (
        <g
          key={index}
          className="animate-in fill-mode-backwards duration-300 fade-in-0 slide-in-from-left-2 motion-reduce:animate-none"
          style={{ animationDelay: `${index * ENTRY_STEP_MS}ms` }}
        >
          <Candle bar={bar} x={scale.x(SHOWN_CANDLES + index)} width={scale.step * 0.62} y={scale.y} />
        </g>
      ))}
    </svg>
  );
}

function Candle({ bar, x, width, y }: { bar: ChallengeBar; x: number; width: number; y: (value: number) => number }) {
  const color = bar.close >= bar.open ? "var(--candle-up)" : "var(--candle-down)";
  const top = y(Math.max(bar.open, bar.close));
  const bottom = y(Math.min(bar.open, bar.close));
  return (
    <g stroke={color} fill={color}>
      <line x1={x} x2={x} y1={y(bar.high)} y2={y(bar.low)} strokeWidth={1.5} />
      <rect x={x - width / 2} y={top} width={width} height={Math.max(1.5, bottom - top)} rx={1} />
    </g>
  );
}
