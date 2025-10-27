import { useState, useEffect, useRef } from "react";
import clsx from "clsx";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import {
  AreaSeries,
  CandlestickSeries,
  createChart,
  CrosshairMode,
  LineStyle,
  type AreaData,
  type AreaSeriesOptions,
  type AreaStyleOptions,
  type CandlestickData,
  type CandlestickSeriesOptions,
  type CandlestickStyleOptions,
  type DeepPartial,
  type IChartApi,
  type ISeriesApi,
  type SeriesOptionsCommon,
  type Time,
  type WhitespaceData,
} from "lightweight-charts";
import { AreaChart, CandlestickChart } from "lucide-react";
import { formatPrice } from "@/lib/utils/formatting";
import { useRealtime } from "@/hooks/useRealtime";
import type { StockCandle } from "@/types";

const TIME_SCALES = ["1s", "1m", "3m", "1a", "3a", "5a", "MAX"] as const;
type TimeScale = (typeof TIME_SCALES)[number];
type ChartType = "line" | "candle";
type AreaSeriesRef = ISeriesApi<
  "Area",
  Time,
  AreaData<Time> | WhitespaceData<Time>,
  AreaSeriesOptions,
  DeepPartial<AreaStyleOptions & SeriesOptionsCommon>
>;
type CandlestickSeriesRef = ISeriesApi<
  "Candlestick",
  Time,
  WhitespaceData<Time> | CandlestickData<Time>,
  CandlestickSeriesOptions,
  DeepPartial<CandlestickStyleOptions & SeriesOptionsCommon>
>;

interface StockChartProps {
  ticker: string;
  initialData: StockCandle[];
}

export function StockChart({ ticker, initialData }: StockChartProps) {
  const [selectedScale, setSelectedScale] = useState<TimeScale>("1m");
  const [chartType, setChartType] = useState<ChartType>("line");
  const chartInstance = useRef<IChartApi>(null);
  const chartRef = useRef<HTMLDivElement>(null);
  const seriesRef = useRef<AreaSeriesRef | CandlestickSeriesRef | null>(null);
  const historyRef = useRef<StockCandle[]>([...initialData]);

  useRealtime(`stock_update:${ticker}`, ({ stock }) => {
    const newCandle: StockCandle = {
      date: stock.date,
      open: stock.open,
      close: stock.price,
      low: stock.low,
      high: stock.high,
      volume: stock.volume,
    };

    const lastCandle = historyRef.current[historyRef.current.length - 1];

    if (lastCandle?.date === newCandle.date) {
      // Atualiza o último candle
      historyRef.current[historyRef.current.length - 1] = newCandle;
    } else {
      // Adiciona novo candle
      historyRef.current.push(newCandle);
    }

    // Atualiza a série com tipagem correta
    if (chartType === "line") {
      (seriesRef.current as AreaSeriesRef)?.update({
        time: newCandle.date.split("T")[0],
        value: newCandle.close,
      });
    } else {
      (seriesRef.current as CandlestickSeriesRef)?.update({
        time: newCandle.date.split("T")[0],
        open: newCandle.open,
        high: newCandle.high,
        low: newCandle.low,
        close: newCandle.close,
      });
    }
  });

  // Filtra os dados conforme selectedScale usando datas reais
  function getFilteredData(scale: TimeScale) {
    const now = new Date(historyRef.current[historyRef.current.length - 1]?.date);
    let fromDate: Date | null = null;

    switch (scale) {
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

    return fromDate ? historyRef.current.filter((d) => new Date(d.date) >= fromDate) : historyRef.current;
  }

  useEffect(() => {
    if (!chartRef.current) return;

    chartInstance.current = createChart(chartRef.current, {
      localization: { priceFormatter: formatPrice },
      crosshair: {
        mode: CrosshairMode.MagnetOHLC,
        vertLine: { style: LineStyle.Solid },
      },
    });

    // Filtra os dados conforme selectedScale
    const filteredData = getFilteredData(selectedScale);

    // Adiciona série de acordo com o tipo
    if (chartType === "line") {
      const areaSeries = chartInstance.current.addSeries(AreaSeries, {
        lineColor: "#2563eb",
        topColor: "rgba(37, 99, 235, 0.3)",
        bottomColor: "rgba(37, 99, 235, 0.0)",
      });
      areaSeries.priceScale().applyOptions({
        autoScale: false, // Desativa a escala automática no preço para manter a visualização fixa
      });
      seriesRef.current = areaSeries;
      areaSeries.setData(filteredData.map((d) => ({ time: d.date.split("T")[0], value: d.close })));
    } else {
      const candleSeries = chartInstance.current.addSeries(CandlestickSeries);
      candleSeries.priceScale().applyOptions({
        autoScale: false, // Desativa a escala automática no preço para manter a visualização fixa
      });
      seriesRef.current = candleSeries;
      candleSeries.setData(
        filteredData.map((d) => ({
          time: d.date.split("T")[0],
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }))
      );
    }

    // Ajusta a visualização para caber todos os dados filtrados
    chartInstance.current.timeScale().fitContent();

    return () => chartInstance.current?.remove();
  }, [chartType, selectedScale]);

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
        {historyRef.current.length > 0 ? (
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
