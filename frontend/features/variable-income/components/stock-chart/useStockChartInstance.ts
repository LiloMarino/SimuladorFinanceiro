import { useCallback, useEffect, useRef } from "react";
import {
  AreaSeries,
  CandlestickSeries,
  createChart,
  CrosshairMode,
  HistogramSeries,
  LineSeries,
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
  type LineWidth,
  type SeriesOptionsCommon,
  type Time,
  type WhitespaceData,
} from "lightweight-charts";
import type { IndicatorPoint, IndicatorSettings, StockCandle, TechnicalIndicators } from "@/types";
import { averageColor, type PANEL_KEYS } from "../../lib/indicators";
import {
  MONEY_FORMAT,
  NO_SERIES,
  NUMBER_FORMAT,
  PRICE_HEIGHT,
  VOLUME_FORMAT,
  ZERO_TO_HUNDRED,
  type ChartType,
  type CrosshairHover,
  type Series,
  type TimeScale,
} from "./chart-config";
import { dayOf, fromDay } from "./chart-helpers";

type AreaSeriesRef = ISeriesApi<
  "Area",
  Time,
  AreaData | WhitespaceData,
  AreaSeriesOptions,
  DeepPartial<AreaStyleOptions & SeriesOptionsCommon>
>;
type CandlestickSeriesRef = ISeriesApi<
  "Candlestick",
  Time,
  WhitespaceData | CandlestickData,
  CandlestickSeriesOptions,
  DeepPartial<CandlestickStyleOptions & SeriesOptionsCommon>
>;
type LineSeriesRef = ISeriesApi<"Line">;
type HistogramSeriesRef = ISeriesApi<"Histogram">;

type StockChartInstanceParams = {
  ticker: string;
  /** O histórico do ativo: o mesmo cache do detalhe, atualizado por WS e pela conferência da pausa */
  history: StockCandle[];
  indicators: TechnicalIndicators | undefined;
  chartType: ChartType;
  selectedScale: TimeScale;
  hasHistory: boolean;
  /** Os painéis ligados, na ordem em que aparecem embaixo do preço */
  panels: (typeof PANEL_KEYS)[number][];
  averages: IndicatorSettings["params"]["averages"];
  showBollinger: boolean;
  rsiOverbought: number;
  rsiOversold: number;
  panelHeight: number;
  height: number;
  /** Resume painéis, médias, Bollinger e níveis do RSI: o gráfico é recriado quando ele muda */
  layout: string;
  onHover: (hover: CrosshairHover | null) => void;
};

/** O dia ISO de um ponto do eixo de tempo, venha ele como texto ou como dia útil. */
function isoDay(time: Time): string {
  if (typeof time === "string") return time;
  if (typeof time === "number") return new Date(time * 1000).toISOString().slice(0, 10);
  return `${time.year}-${String(time.month).padStart(2, "0")}-${String(time.day).padStart(2, "0")}`;
}

/**
 * Cria o gráfico no `chartRef` e o mantém preenchido: o preço, uma série por indicador e a mira.
 * O gráfico nasce antes dos efeitos de quem consome as refs devolvidas, que se ligam a ele já no ar.
 */
export function useStockChartInstance({
  ticker,
  history,
  indicators,
  chartType,
  selectedScale,
  hasHistory,
  panels,
  averages,
  showBollinger,
  rsiOverbought,
  rsiOversold,
  panelHeight,
  height,
  layout,
  onHover,
}: StockChartInstanceParams) {
  const chartInstance = useRef<IChartApi>(null);
  const chartRef = useRef<HTMLDivElement>(null);
  const seriesRef = useRef<AreaSeriesRef | CandlestickSeriesRef | null>(null);
  const linesRef = useRef(new Map<string, LineSeriesRef>());
  const barsRef = useRef(new Map<string, HistogramSeriesRef>());
  const historyRef = useRef<StockCandle[]>([...history]);

  // Preenche o preço e cada indicador com os pontos do período escolhido
  const fill = useCallback(() => {
    const candles = historyRef.current;
    const from = fromDay(candles, selectedScale);
    const data = from === null ? candles : candles.filter((d) => dayOf(d) >= from);
    if (chartType === "line") {
      (seriesRef.current as AreaSeriesRef | null)?.setData(data.map((d) => ({ time: dayOf(d), value: d.close })));
    } else {
      (seriesRef.current as CandlestickSeriesRef | null)?.setData(data.map((d) => ({ ...d, time: dayOf(d) })));
    }

    const toData = (points: IndicatorPoint[] | null | undefined) =>
      (points ?? [])
        .filter((point) => from === null || point.date >= from)
        .map((point) => ({
          time: point.date,
          value: point.value,
        }));
    const series: Series = indicators?.series ?? NO_SERIES;
    const styles = getComputedStyle(document.documentElement);
    const up = styles.getPropertyValue("--candle-up").trim();
    const down = styles.getPropertyValue("--candle-down").trim();
    const lines = linesRef.current;
    const bars = barsRef.current;

    series.averages?.forEach((average, index) => lines.get(`average:${index}`)?.setData(toData(average.points)));
    lines.get("bollinger:upper")?.setData(toData(series.bollinger?.upper));
    lines.get("bollinger:middle")?.setData(toData(series.bollinger?.middle));
    lines.get("bollinger:lower")?.setData(toData(series.bollinger?.lower));
    lines.get("rsi")?.setData(toData(series.rsi));
    lines.get("macd:line")?.setData(toData(series.macd?.line));
    lines.get("macd:signal")?.setData(toData(series.macd?.signal));
    bars.get("macd:histogram")?.setData(
      toData(series.macd?.histogram).map((point) => ({
        ...point,
        color: `${point.value >= 0 ? up : down}99`,
      })),
    );
    lines.get("stochastic:k")?.setData(toData(series.stochastic?.k));
    lines.get("stochastic:d")?.setData(toData(series.stochastic?.d));
    lines.get("atr")?.setData(toData(series.atr));
    lines.get("obv")?.setData(toData(series.obv));
    bars.get("volume")?.setData(
      data.map((d) => ({
        time: dayOf(d),
        value: d.volume,
        color: `${d.close >= d.open ? up : down}80`,
      })),
    );
  }, [selectedScale, chartType, indicators]);

  useEffect(() => {
    historyRef.current = [...history];
    fill();
  }, [history, ticker, fill]);

  useEffect(() => {
    if (!chartRef.current) return;

    const styles = getComputedStyle(document.documentElement);
    const color = (token: string) => styles.getPropertyValue(token).trim();
    const chart = createChart(chartRef.current, {
      height,
      crosshair: {
        mode: CrosshairMode.MagnetOHLC,
        vertLine: { style: LineStyle.Solid },
      },
    });
    chartInstance.current = chart;

    // Adiciona série de acordo com o tipo
    const lineColor = color("--chart-1-canvas");
    const topColor = `${lineColor}4d`; // 30% de opacidade em hex8 (0x4D ≈ 0.3 * 255)

    if (chartType === "line") {
      const areaSeries = chart.addSeries(AreaSeries, {
        lineColor,
        topColor,
        bottomColor: `${lineColor}00`,
        priceFormat: MONEY_FORMAT,
      });
      areaSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.05, bottom: 0.05 },
      });
      seriesRef.current = areaSeries;
    } else {
      const upColor = color("--candle-up");
      const downColor = color("--candle-down");
      const candleSeries = chart.addSeries(CandlestickSeries, {
        upColor,
        downColor,
        wickUpColor: upColor,
        wickDownColor: downColor,
        borderVisible: false,
        priceFormat: MONEY_FORMAT,
      });
      candleSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.05, bottom: 0.05 },
      });
      seriesRef.current = candleSeries;
    }

    // Linhas sobre o preço e uma série por painel embaixo
    const lines = new Map<string, LineSeriesRef>();
    const bars = new Map<string, HistogramSeriesRef>();
    const addLine = (
      key: string,
      token: string,
      pane: number,
      options: Parameters<typeof chart.addSeries<"Line">>[1] = {},
    ) =>
      lines.set(
        key,
        chart.addSeries(
          LineSeries,
          {
            color: color(token),
            lineWidth: 2 as LineWidth,
            priceLineVisible: false,
            lastValueVisible: false,
            priceFormat: MONEY_FORMAT,
            ...options,
          },
          pane,
        ),
      );
    const level = (key: string, price: number) =>
      lines.get(key)?.createPriceLine({
        price,
        color: color("--faint-foreground"),
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: "",
      });

    averages.forEach((_, index) => addLine(`average:${index}`, averageColor(index), 0));
    if (showBollinger) {
      addLine("bollinger:upper", "--chart-2", 0, { lineWidth: 1 });
      addLine("bollinger:middle", "--chart-2", 0, {
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
      });
      addLine("bollinger:lower", "--chart-2", 0, { lineWidth: 1 });
    }

    panels.forEach((key, index) => {
      const pane = index + 1;
      if (key === "volume") {
        bars.set(
          "volume",
          chart.addSeries(
            HistogramSeries,
            {
              priceFormat: VOLUME_FORMAT,
              priceLineVisible: false,
              lastValueVisible: false,
            },
            pane,
          ),
        );
      } else if (key === "rsi") {
        addLine("rsi", "--chart-6", pane, {
          priceFormat: NUMBER_FORMAT,
          autoscaleInfoProvider: ZERO_TO_HUNDRED,
        });
        level("rsi", rsiOverbought);
        level("rsi", rsiOversold);
      } else if (key === "macd") {
        bars.set(
          "macd:histogram",
          chart.addSeries(
            HistogramSeries,
            {
              priceFormat: NUMBER_FORMAT,
              priceLineVisible: false,
              lastValueVisible: false,
            },
            pane,
          ),
        );
        addLine("macd:line", "--chart-1-canvas", pane, {
          priceFormat: NUMBER_FORMAT,
          lineWidth: 1,
        });
        addLine("macd:signal", "--chart-5", pane, {
          priceFormat: NUMBER_FORMAT,
          lineWidth: 1,
        });
      } else if (key === "stochastic") {
        addLine("stochastic:k", "--chart-7", pane, {
          priceFormat: NUMBER_FORMAT,
          lineWidth: 1,
          autoscaleInfoProvider: ZERO_TO_HUNDRED,
        });
        addLine("stochastic:d", "--chart-5", pane, {
          priceFormat: NUMBER_FORMAT,
          lineWidth: 1,
          autoscaleInfoProvider: ZERO_TO_HUNDRED,
        });
        level("stochastic:k", 80);
        level("stochastic:k", 20);
      } else if (key === "atr") {
        addLine("atr", "--chart-9", pane, { lineWidth: 1 });
      } else {
        addLine("obv", "--chart-8", pane, {
          priceFormat: VOLUME_FORMAT,
          lineWidth: 1,
        });
      }
    });
    linesRef.current = lines;
    barsRef.current = bars;

    const [pricePane, ...panes] = chart.panes();
    pricePane?.setStretchFactor(PRICE_HEIGHT);
    for (const pane of panes) pane.setStretchFactor(panelHeight);

    // A mira leva a legenda e os rótulos dos painéis para o dia apontado
    chart.subscribeCrosshairMove((param) => {
      if (param.time === undefined || !param.point) return onHover(null);
      onHover({ day: isoDay(param.time), x: param.point.x, width: chartRef.current?.clientWidth ?? 0 });
    });

    fill();
    // Ajusta a visualização para caber todos os dados filtrados
    chart.timeScale().fitContent();

    return () => {
      chart.remove();
      chartInstance.current = null;
      seriesRef.current = null;
      linesRef.current = new Map();
      barsRef.current = new Map();
    };
    // O gráfico é recriado quando `chartType`, `selectedScale`, `ticker`, `hasHistory`, `layout` ou `height` mudam.
    // `layout` resume painéis, médias, Bollinger e níveis do RSI, e `height` acompanha a quantidade de painéis:
    // `panels`, `averages`, `showBollinger`, `rsiOverbought`, `rsiOversold` e `panelHeight` lidos aqui coincidem
    // com o `layout` da criação. O `fill` troca a cada dado novo de indicador, e quem repreenche as séries
    // é o efeito do histórico, sem recriar o gráfico.
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [chartType, selectedScale, ticker, hasHistory, layout, height]);

  return { chartRef, chartInstance, seriesRef, linesRef };
}
