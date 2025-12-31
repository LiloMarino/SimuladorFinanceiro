import type { PlayerSeries } from "./series";

interface Props {
  series: PlayerSeries[];
  visible: Record<string, boolean>;
  toggle: (key: string) => void;
}

export function PerformanceChartLegend({ series, visible, toggle }: Props) {
  return (
    <div className="flex justify-center gap-3 flex-wrap">
      {series.map((s) => {
        const isActive = visible[s.key];

        return (
          <button
            key={s.key}
            onClick={() => toggle(s.key)}
            className={`
              flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all
              ${isActive ? "bg-primary/10 border-primary/20" : "opacity-50"}
            `}
          >
            <span
              className="w-3 h-3 rounded-full"
              style={{
                backgroundColor: isActive ? s.color : "#9CA3AF",
                transform: isActive ? "scale(1)" : "scale(0.85)",
              }}
            />
            <span className={`text-xs font-medium ${isActive ? "text-foreground" : "text-muted-foreground"}`}>
              {s.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
