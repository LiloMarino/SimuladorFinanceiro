import type { LegendProps } from "recharts";
import { PORTFOLIO_LINE_SERIES, type PortfolioSeriesKey } from "./line-series";

interface ChartLegendProps extends LegendProps {
  visible: Record<PortfolioSeriesKey, boolean>;
  toggle: (key: PortfolioSeriesKey) => void;
}

export function PortfolioLineLegend({ payload, visible, toggle }: ChartLegendProps) {
  if (!payload) return null;

  return (
    <div className="flex justify-center lg:justify-end gap-2 mb-3 flex-wrap">
      {PORTFOLIO_LINE_SERIES.map((series) => {
        const isActive = visible[series.key];

        return (
          <button
            key={series.key}
            onClick={() => toggle(series.key)}
            aria-pressed={isActive}
            aria-label={`${isActive ? "Ocultar" : "Mostrar"} ${series.label}`}
            className={`
              flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all
              ${isActive ? "bg-primary/10 border-primary/20" : "opacity-50"}
            `}
          >
            <span
              className="w-3 h-3 rounded-full transition-transform duration-200"
              style={{
                backgroundColor: isActive ? series.color : "#9CA3AF",
                transform: isActive ? "scale(1)" : "scale(0.85)",
              }}
            />
            <span className={`text-xs font-medium ${isActive ? "text-foreground" : "text-muted-foreground"}`}>
              {series.label}
            </span>
          </button>
        );
      })}
    </div>
  );
}
