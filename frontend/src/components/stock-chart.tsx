import { useState, useMemo, useEffect, useRef } from "react";
import clsx from "clsx";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { createChart } from "lightweight-charts";
import type { StockCandle } from "@/types";

const TIME_SCALES = ["1s", "1m", "3m", "1a", "3a", "5a", "MAX"] as const;
type TimeScale = (typeof TIME_SCALES)[number];
type ChartType = "line" | "candle";

interface StockChartProps {
  data: StockCandle[];
  title?: string;
}

export function StockChart({ data, title = "Histórico de Preços" }: StockChartProps) {
  const [selectedScale, setSelectedScale] = useState<TimeScale>("1s");
  const [chartType, setChartType] = useState<ChartType>("line");
  const chartRef = useRef<HTMLDivElement>(null);

  // Aqui você poderia filtrar `data` conforme selectedScale se quiser
  const chartData = useMemo(() => data, [data]);

  useEffect(() => {
    if (!chartRef.current || chartData.length === 0) return;

    const chart = createChart(chartRef.current, {
      layout: { background: { color: "#ffffff" }, textColor: "#000000" },
      grid: { vertLines: { color: "#eee" }, horzLines: { color: "#eee" } },
      rightPriceScale: { borderColor: "#ccc" },
      timeScale: { borderColor: "#ccc" },
    });

    if (chartType === "line") {
      const lineSeries = chart.addSeries({
        type: "Line",
        color: "#3b82f6",
      });
      lineSeries.setData(chartData.map((d) => ({ time: d.date, value: d.close })));
    } else {
      const candleSeries = chart.addSeries({
        type: "Candlestick",
      });
      candleSeries.setData(
        chartData.map((d) => ({
          time: d.date,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }))
      );
    }

    return () => chart.remove();
  }, [chartData, chartType]);

  return (
    <Card className="mb-8">
      <CardHeader className="flex flex-row justify-between items-center">
        <CardTitle className="text-base font-semibold">{title}</CardTitle>

        <div className="flex items-center gap-2">
          {/* TimeScale */}
          <div className="flex divide-x divide-blue-700 rounded-md overflow-hidden border border-blue-700/30">
            {TIME_SCALES.map((scale) => (
              <button
                key={scale}
                onClick={() => setSelectedScale(scale)}
                className={clsx(
                  "px-3 py-1 text-sm font-medium transition-colors duration-200",
                  selectedScale === scale ? "bg-blue-700 text-white" : "text-blue-700 hover:bg-blue-700/20"
                )}
              >
                {scale.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Switch Chart */}
          <div className="flex items-center gap-1 ml-2">
            <button
              onClick={() => setChartType("line")}
              className={clsx(
                "p-1 rounded transition-colors",
                chartType === "line" ? "bg-blue-700 text-white" : "bg-gray-200 hover:bg-gray-300"
              )}
              title="Gráfico de Linha"
            >
              📈
            </button>
            <button
              onClick={() => setChartType("candle")}
              className={clsx(
                "p-1 rounded transition-colors",
                chartType === "candle" ? "bg-blue-700 text-white" : "bg-gray-200 hover:bg-gray-300"
              )}
              title="Gráfico de Velas"
            >
              🕯️
            </button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="h-64">
        {chartData.length > 0 ? (
          <div ref={chartRef} className="w-full h-full" />
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            Nenhum dado de histórico disponível.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
