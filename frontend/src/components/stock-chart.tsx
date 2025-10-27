import { useState, useMemo, useEffect, useRef } from "react";
import clsx from "clsx";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { AreaSeries, CandlestickSeries, createChart, CrosshairMode, LineStyle } from "lightweight-charts";
import type { StockCandle } from "@/types";
import { AreaChart, CandlestickChart } from "lucide-react";
import { formatPrice } from "@/lib/utils/formatting";

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

  // Filtra os dados conforme selectedScale usando datas reais
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const now = new Date(data[data.length - 1].date);
    let fromDate: Date | null = null;

    switch (selectedScale) {
      case "1s":
        fromDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); // 7 dias
        break;
      case "1m":
        fromDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000); // ~1 mês
        break;
      case "3m":
        fromDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000); // ~3 meses
        break;
      case "1a":
        fromDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000); // 1 ano
        break;
      case "3a":
        fromDate = new Date(now.getTime() - 3 * 365 * 24 * 60 * 60 * 1000); // 3 anos
        break;
      case "5a":
        fromDate = new Date(now.getTime() - 5 * 365 * 24 * 60 * 60 * 1000); // 5 anos
        break;
      case "MAX":
        fromDate = null;
        break;
    }

    if (!fromDate) return data;

    return data.filter((d) => {
      const candleDate = new Date(d.date);
      return candleDate >= fromDate!;
    });
  }, [data, selectedScale]);

  useEffect(() => {
    if (!chartRef.current || chartData.length === 0) return;

    const chart = createChart(chartRef.current, {
      localization: {
        priceFormatter: formatPrice,
      },
      crosshair: {
        mode: CrosshairMode.MagnetOHLC,
        vertLine: {
          style: LineStyle.Solid,
        },
      },
    });

    // Adiciona série de acordo com o tipo
    if (chartType === "line") {
      const areaSeries = chart.addSeries(AreaSeries, {
        lineColor: "#2563eb", // azul principal (Tailwind blue-600)
        topColor: "rgba(37, 99, 235, 0.3)", // azul claro com transparência
        bottomColor: "rgba(37, 99, 235, 0.0)", // gradiente que some
      });
      areaSeries.priceScale().applyOptions({
        autoScale: false, // Desativa a escala automática no preço para manter a visualização fixa
      });
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
      candleSeries.priceScale().applyOptions({
        autoScale: false, // Desativa a escala automática no preço para manter a visualização fixa
      });
    }

    // Ajusta a visualização para caber todos os dados filtrados
    chart.timeScale().fitContent();

    return () => chart.remove();
  }, [chartData, chartType]);

  return (
    <Card className="mb-8">
      <CardHeader className="flex flex-row justify-between items-center">
        <CardTitle className="text-base font-semibold">Histórico de Preços</CardTitle>

        <div className="flex items-center gap-2">
          {/* TimeScale */}
          <div className="flex divide-x divide-gray-300 rounded-md overflow-hidden">
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

      <CardContent className="h-100">
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
