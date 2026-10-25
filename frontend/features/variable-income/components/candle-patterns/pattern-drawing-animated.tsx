import { motion } from "motion/react";
import { candleColor, CANDLE_WIDTH, type CandleBox } from "../../lib/pattern-geometry";

const GROW_SECONDS = 0.35;
const STAGGER_SECONDS = 0.25;

/** As velas surgem da base, uma depois da outra. */
export default function AnimatedCandles({ boxes }: { boxes: CandleBox[] }) {
  return boxes.map((box, index) => (
    <motion.g
      key={index}
      stroke={candleColor(box.bullish)}
      fill={candleColor(box.bullish)}
      initial={{ scaleY: 0, opacity: 0 }}
      animate={{ scaleY: 1, opacity: 1 }}
      transition={{ duration: GROW_SECONDS, delay: index * STAGGER_SECONDS, ease: "easeOut" }}
      style={{ transformBox: "fill-box", transformOrigin: "center" }}
    >
      <line x1={box.x} x2={box.x} y1={box.wickTop} y2={box.wickBottom} strokeWidth={1.5} />
      <rect x={box.x - CANDLE_WIDTH / 2} y={box.bodyTop} width={CANDLE_WIDTH} height={box.bodyHeight} rx={1} />
    </motion.g>
  ));
}
