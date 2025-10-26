import { useState, useMemo, useEffect, useRef } from "react";
import clsx from "clsx";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { AreaSeries, CandlestickSeries, createChart } from "lightweight-charts";
import type { StockCandle } from "@/types";
import { AreaChart, CandlestickChart } from "lucide-react";

const TIME_SCALES = ["1s", "1m", "3m", "1a", "3a", "5a", "MAX"] as const;
type TimeScale = (typeof TIME_SCALES)[number];
type ChartType = "line" | "candle";

interface StockChartProps {
  data: StockCandle[];
}

export function StockChart({ data }: StockChartProps) {
  const [selectedScale, setSelectedScale] = useState<TimeScale>("1s");
  const [chartType, setChartType] = useState<ChartType>("line");
  const chartRef = useRef<HTMLDivElement>(null);

  // Aqui você poderia filtrar `data` conforme selectedScale se quiser
  const chartData = useMemo(() => data, [data]);

  useEffect(() => {
    if (!chartRef.current || chartData.length === 0) return;

    const chart = createChart(chartRef.current);

    if (chartType === "line") {
      const areaSeries = chart.addSeries(AreaSeries);
      areaSeries.setData(chartData.map((d) => ({ time: d.date.split("T")[0], value: d.close })));
    } else {
      const candleSeries = chart.addSeries(CandlestickSeries);
      candleSeries.setData(
        chartData.map((d) => ({
          time: d.date.split("T")[0],
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
        <CardTitle className="text-base font-semibold">Histórico de Preços</CardTitle>

        <div className="flex items-center gap-2">
          {/* TimeScale */}
          <div className="flex  divide-x divide-gray-300 rounded-md overflow-hidden">
            {TIME_SCALES.map((scale) => (
              <button
                key={scale}
                onClick={() => setSelectedScale(scale)}
                className={clsx(
                  "px-3 py-1 text-sm transition-colors duration-200",
                  selectedScale === scale ? "bg-blue-700 text-white" : "bg-gray-200 text-gray-800 hover:bg-gray-300"
                )}
              >
                {scale.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Switch Chart */}
          <div className="flex divide-x divide-gray-300 rounded-md overflow-hidden border border-gray-300 ml-2">
            <button
              onClick={() => setChartType("line")}
              className={clsx(
                "px-3 py-1 flex items-center justify-center gap-1 text-sm transition-colors duration-200",
                chartType === "line" ? "bg-blue-700 text-white" : "bg-gray-200 text-gray-800 hover:bg-gray-300"
              )}
              title="Gráfico de Área"
            >
              <AreaChart className="w-5 h-5" />
            </button>
            <button
              onClick={() => setChartType("candle")}
              className={clsx(
                "px-3 py-1 flex items-center justify-center gap-1 text-sm transition-colors duration-200",
                chartType === "candle" ? "bg-blue-700 text-white" : "bg-gray-200 text-gray-800 hover:bg-gray-300"
              )}
              title="Gráfico de Velas"
            >
              <CandlestickChart className="w-5 h-5" />
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
