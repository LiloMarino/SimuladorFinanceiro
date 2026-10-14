import { useState, useEffect, useRef } from "react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardAction, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
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
import { displayMoney } from "@/shared/lib/utils/display";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { StockCandle } from "@/types";

const TIME_SCALES = ["1s", "1m", "3m", "1a", "3a", "5a", "MAX"] as const;
const SCALE_LABELS: Record<TimeScale, string> = {
  "1s": "1S",
  "1m": "1M",
  "3m": "3M",
  "1a": "1A",
  "3a": "3A",
  "5a": "5A",
  MAX: "Tudo",
};
const SCALE_DAYS: Record<TimeScale, number | null> = {
  "1s": 7, // 7 dias
  "1m": 30, // 1 mês
  "3m": 90, // 3 meses
  "1a": 365, // 1 ano
  "3a": 3 * 365,
  "5a": 5 * 365,
  MAX: null, // Tudo
} as const;

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
      price_date: stock.price_date,
      open: stock.open,
      close: stock.close,
      low: stock.low,
      high: stock.high,
      volume: stock.volume,
    };

    const lastCandle = historyRef.current[historyRef.current.length - 1];

    if (lastCandle?.price_date === newCandle.price_date) {
      // Atualiza o último candle
      historyRef.current[historyRef.current.length - 1] = newCandle;
    } else {
      // Adiciona novo candle
      historyRef.current.push(newCandle);
    }

    // Atualiza a série com tipagem correta
    if (chartType === "line") {
      (seriesRef.current as AreaSeriesRef)?.update({
        time: newCandle.price_date.split("T")[0],
        value: newCandle.close,
      });
    } else {
      (seriesRef.current as CandlestickSeriesRef)?.update({
        time: newCandle.price_date.split("T")[0],
        open: newCandle.open,
        high: newCandle.high,
        low: newCandle.low,
        close: newCandle.close,
      });
    }
  });

  // Filtra os dados conforme selectedScale usando datas reais
  function getFilteredData(scale: TimeScale) {
    const now = new Date(historyRef.current[historyRef.current.length - 1]?.price_date);
    const days = SCALE_DAYS[scale];

    if (days === null) return historyRef.current;

    const fromDate = new Date(now);
    fromDate.setDate(now.getDate() - days);

    return historyRef.current.filter((d) => new Date(d.price_date) >= fromDate);
  }

  useEffect(() => {
    if (!chartRef.current) return;

    chartInstance.current = createChart(chartRef.current, {
      localization: { priceFormatter: displayMoney },
      crosshair: {
        mode: CrosshairMode.MagnetOHLC,
        vertLine: { style: LineStyle.Solid },
      },
    });

    // Filtra os dados conforme selectedScale
    const filteredData = getFilteredData(selectedScale);

    // Adiciona série de acordo com o tipo
    const lineColor = getComputedStyle(document.documentElement).getPropertyValue("--chart-1-canvas").trim();
    const topColor = `${lineColor}4d`; // 30% de opacidade em hex8 (0x4D ≈ 0.3 * 255)

    if (chartType === "line") {
      const areaSeries = chartInstance.current.addSeries(AreaSeries, {
        lineColor,
        topColor,
        bottomColor: `${lineColor}00`,
      });
      areaSeries.priceScale().applyOptions({
        autoScale: false, // Desativa a escala automática no preço para manter a visualização fixa
      });
      seriesRef.current = areaSeries;
      areaSeries.setData(filteredData.map((d) => ({ time: d.price_date.split("T")[0], value: d.close })));
    } else {
      const styles = getComputedStyle(document.documentElement);
      const upColor = styles.getPropertyValue("--candle-up").trim();
      const downColor = styles.getPropertyValue("--candle-down").trim();
      const candleSeries = chartInstance.current.addSeries(CandlestickSeries, {
        upColor,
        downColor,
        wickUpColor: upColor,
        wickDownColor: downColor,
        borderVisible: false,
      });
      candleSeries.priceScale().applyOptions({
        autoScale: false, // Desativa a escala automática no preço para manter a visualização fixa
      });
      seriesRef.current = candleSeries;
      candleSeries.setData(
        filteredData.map((d) => ({
          time: d.price_date.split("T")[0],
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        })),
      );
    }

    // Ajusta a visualização para caber todos os dados filtrados
    chartInstance.current.timeScale().fitContent();

    return () => chartInstance.current?.remove();
  }, [chartType, selectedScale]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Histórico de preços</CardTitle>
        <CardAction>
          <div className="flex flex-wrap items-center gap-2">
            <ToggleGroup
              variant="segmented"
              aria-label="Período"
              value={[selectedScale]}
              onValueChange={(values) => values[0] && setSelectedScale(values[0] as TimeScale)}
            >
              {TIME_SCALES.map((scale) => (
                <ToggleGroupItem key={scale} value={scale}>
                  {SCALE_LABELS[scale]}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
            <ToggleGroup
              variant="segmented"
              aria-label="Tipo de gráfico"
              value={[chartType]}
              onValueChange={(values) => values[0] && setChartType(values[0] as ChartType)}
            >
              <ToggleGroupItem value="line">Linha</ToggleGroupItem>
              <ToggleGroupItem value="candle">Velas</ToggleGroupItem>
            </ToggleGroup>
            <Button variant="ghost" size="sm" onClick={() => chartInstance.current?.timeScale().scrollToRealTime()}>
              Ir pro dia de hoje
            </Button>
          </div>
        </CardAction>
      </CardHeader>

      <CardContent>
        {initialData.length > 0 ? (
          <div ref={chartRef} className="h-90 w-full" />
        ) : (
          <div className="flex h-90 items-center justify-center text-muted-foreground">
            Nenhum dado de histórico disponível.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
