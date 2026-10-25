import { lazy, Suspense } from "react";
import { usePrefersReducedMotion } from "@/shared/hooks/usePrefersReducedMotion";
import type { CandlePatternCode } from "@/types";
import { PATTERN_INFO } from "../../lib/candle-patterns";
import { candleBoxes, candleColor, CANDLE_WIDTH, DRAWING_HEIGHT, DRAWING_WIDTH } from "../../lib/pattern-geometry";

// A biblioteca de animação carrega só quando um card pede o desenho
const AnimatedCandles = lazy(() => import("./pattern-drawing-animated"));

/** O desenho do padrão: as velas crescem uma a uma; com movimento reduzido, ele já nasce pronto. */
export function PatternDrawing({ code }: { code: CandlePatternCode }) {
  const reducedMotion = usePrefersReducedMotion();
  const boxes = candleBoxes(PATTERN_INFO[code].candles);
  const still = <StaticCandles boxes={boxes} />;

  return (
    <svg
      width={DRAWING_WIDTH}
      height={DRAWING_HEIGHT}
      viewBox={`0 0 ${DRAWING_WIDTH} ${DRAWING_HEIGHT}`}
      className="shrink-0 rounded-lg bg-subtle"
      role="img"
      aria-label={`Desenho do padrão ${PATTERN_INFO[code].name}`}
    >
      {reducedMotion ? (
        still
      ) : (
        <Suspense fallback={still}>
          <AnimatedCandles boxes={boxes} />
        </Suspense>
      )}
    </svg>
  );
}

function StaticCandles({ boxes }: { boxes: ReturnType<typeof candleBoxes> }) {
  return boxes.map((box, index) => (
    <g key={index} stroke={candleColor(box.bullish)} fill={candleColor(box.bullish)}>
      <line x1={box.x} x2={box.x} y1={box.wickTop} y2={box.wickBottom} strokeWidth={1.5} />
      <rect x={box.x - CANDLE_WIDTH / 2} y={box.bodyTop} width={CANDLE_WIDTH} height={box.bodyHeight} rx={1} />
    </g>
  ));
}
