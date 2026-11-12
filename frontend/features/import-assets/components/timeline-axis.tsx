import { cn } from "@/shared/lib/utils";
import { timelineTicks, type TimelineRange, type TimelineTick } from "../lib/timeline";

const ALIGN: Record<TimelineTick["align"], string> = {
  start: "",
  center: "-translate-x-1/2",
  end: "-translate-x-full",
};

/** A régua do eixo comum, no cabeçalho da coluna das barras. */
export function TimelineAxis({ range }: { range: TimelineRange }) {
  return (
    <div className="relative h-4 font-mono">
      {timelineTicks(range).map((tick) => (
        <span key={tick.label} className={cn("absolute", ALIGN[tick.align])} style={{ left: `${tick.position}%` }}>
          {tick.label}
        </span>
      ))}
    </div>
  );
}
