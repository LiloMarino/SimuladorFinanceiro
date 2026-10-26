import { useState, useEffect, useMemo, useRef, useCallback } from "react";
import { AlertCircle, Settings, Sparkles, X } from "lucide-react";
import { Alert, AlertAction, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
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
import { cn } from "@/shared/lib/utils";
import { displayCompactNumber, displayMoney, displayNumber, parseLocalDate } from "@/shared/lib/utils/display";
import type {
  CandleChallenge,
  CandlePattern,
  CandlePatterns,
  ChallengeDirection,
  IndicatorKey,
  IndicatorPoint,
  IndicatorSettings,
  StockCandle,
  TechnicalIndicators,
} from "@/types";
import { IndicatorSelector, Swatch } from "./indicator-selector";
import { ChallengeStrip } from "./candle-patterns/challenge-strip";
import { PatternCard } from "./candle-patterns/pattern-card";
import { PatternNotice, PatternSwitch, type PatternNoticeProps } from "./candle-patterns/pattern-controls";
import { PatternList } from "./candle-patterns/pattern-list";
import { useChartAnnotations, type Annotations } from "../hooks/useChartAnnotations";
import {
  AVERAGE_PHRASES,
  MACD_PHRASES,
  crossoverShapes,
  patternMarkers,
  patternShapes,
  rsiShapes,
  type AnnotationColors,
} from "../lib/chart-annotations";
import { isAnswerFresh, nextScaleWithPatterns, patternOn, patternsSince, statsOf } from "../lib/pattern-view";
import {
  AVERAGE_COLORS,
  INDICATOR_BY_KEY,
  PANEL_KEYS,
  averageLabel,
  displaySignedCompact,
  isShown,
  toggled,
  withParams,
} from "../lib/indicators";

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

const PRICE_HEIGHT = 360;
const POP_WIDTH = 200;
const CARD_WIDTH = 320;
// O eixo de tempo fica fora dos painéis: somado à altura, cada painel recebe exatamente a sua
const TIME_AXIS_HEIGHT = 28;
// Com muitos painéis, cada um encolhe para o preço seguir legível
const paneHeight = (panels: number) => (panels <= 3 ? 90 : 60);

// O preço sai em reais; volume e OBV, em número curto
const MONEY_FORMAT = {
  type: "custom",
  minMove: 0.01,
  formatter: displayMoney,
} as const;
const VOLUME_FORMAT = {
  type: "custom",
  minMove: 1,
  formatter: displayCompactNumber,
} as const;
const NUMBER_FORMAT = {
  type: "custom",
  minMove: 0.01,
  formatter: (value: number) => displayNumber(value),
} as const;
const ZERO_TO_HUNDRED = () => ({ priceRange: { minValue: 0, maxValue: 100 } });

type TimeScale = (typeof TIME_SCALES)[number];
type ChartType = "line" | "candle";
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
type Series = TechnicalIndicators["series"];

/** As dicas de análise técnica do gráfico; `null` quando a partida as desliga. */
interface ChartHints {
  patterns: CandlePatterns | undefined;
  patternsStatus: "pending" | "error" | "success";
  onRetryPatterns: () => void;
  challenge: CandleChallenge | undefined;
  answering: boolean;
  onAnswer: (direction: ChallengeDirection) => void;
}

interface StockChartProps {
  ticker: string;
  initialData: StockCandle[];
  settings: IndicatorSettings;
  indicators: TechnicalIndicators | undefined;
  indicatorsStatus: "pending" | "error" | "success";
  onRetryIndicators: () => void;
  onSettingsChange: (next: IndicatorSettings) => void;
  hints: ChartHints | null;
}

const dayOf = (candle: StockCandle) => candle.price_date.split("T")[0];

/** O dia ISO de um ponto do eixo de tempo, venha ele como texto ou como dia útil. */
function isoDay(time: Time): string {
  if (typeof time === "string") return time;
  if (typeof time === "number") return new Date(time * 1000).toISOString().slice(0, 10);
  return `${time.year}-${String(time.month).padStart(2, "0")}-${String(time.day).padStart(2, "0")}`;
}

/** O primeiro dia do período escolhido, contado a partir do último candle do histórico. */
function fromDay(history: StockCandle[], scale: TimeScale) {
  const last = history[history.length - 1];
  const days = SCALE_DAYS[scale];
  if (!last || days === null) return null;
  const from = new Date(last.price_date);
  from.setDate(from.getDate() - days);
  return from.toISOString().slice(0, 10);
}

/** As cores do tema que as anotações do gráfico usam. */
function readAnnotationColors(): AnnotationColors {
  const styles = getComputedStyle(document.documentElement);
  const color = (token: string) => styles.getPropertyValue(token).trim();
  return {
    up: color("--candle-up"),
    down: color("--candle-down"),
    neutral: color("--faint-foreground"),
    band: color("--chart-1-canvas"),
  };
}

function valueOn(points: IndicatorPoint[] | null | undefined, day: string | null) {
  if (!points?.length) return null;
  if (day === null) return points[points.length - 1].value;
  return points.find((point) => point.date === day)?.value ?? null;
}

export function StockChart({
  ticker,
  initialData,
  settings,
  indicators,
  indicatorsStatus,
  onRetryIndicators,
  onSettingsChange,
  hints,
}: StockChartProps) {
  const [selectedScale, setSelectedScale] = useState<TimeScale>("1m");
  const [chartType, setChartType] = useState<ChartType>("line");
  const [selectorOpen, setSelectorOpen] = useState(false);
  const [hover, setHover] = useState<{ day: string; x: number; width: number } | null>(null);
  const [expanded, setExpanded] = useState<IndicatorKey | null>(null);
  const chartInstance = useRef<IChartApi>(null);
  const chartRef = useRef<HTMLDivElement>(null);
  const seriesRef = useRef<AreaSeriesRef | CandlestickSeriesRef | null>(null);
  const linesRef = useRef(new Map<string, LineSeriesRef>());
  const barsRef = useRef(new Map<string, HistogramSeriesRef>());
  const historyRef = useRef<StockCandle[]>([...initialData]);
  const hasHistory = initialData.length > 0;

  // No erro os painéis dão lugar ao aviso, e o preço fica
  const failed = indicatorsStatus === "error" && !indicators;
  const panels = PANEL_KEYS.filter((key) => isShown(settings, key) && !failed);
  const averages = isShown(settings, "averages") && !failed ? settings.params.averages : [];
  const showBollinger = isShown(settings, "bollinger") && !failed;
  const panelHeight = paneHeight(panels.length);
  const height = PRICE_HEIGHT + panels.length * panelHeight + TIME_AXIS_HEIGHT;
  // O gráfico é recriado quando muda o que ele desenha; os dados novos só trocam os pontos
  const { rsi_overbought, rsi_oversold } = settings.params;
  const layout = [panels.join(","), averages.length, showBollinger, rsi_overbought, rsi_oversold].join("|");

  const closeByDay = useMemo(() => new Map(initialData.map((candle) => [dayOf(candle), candle.close])), [initialData]);

  // Preenche o preço e cada indicador com os pontos do período escolhido
  const fill = useCallback(() => {
    const history = historyRef.current;
    const from = fromDay(history, selectedScale);
    const data = from === null ? history : history.filter((d) => dayOf(d) >= from);
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
    const series: Series = indicators?.series ?? {};
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

  // O histórico é o mesmo cache do detalhe, atualizado por WS e pela conferência da pausa.
  useEffect(() => {
    historyRef.current = [...initialData];
    fill();
  }, [initialData, ticker, fill]);

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

    averages.forEach((_, index) => addLine(`average:${index}`, AVERAGE_COLORS[index], 0));
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
        level("rsi", rsi_overbought);
        level("rsi", rsi_oversold);
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
      if (param.time === undefined || !param.point) return setHover(null);
      setHover({ day: isoDay(param.time), x: param.point.x, width: chartRef.current?.clientWidth ?? 0 });
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
    // `layout` resume painéis, médias, Bollinger e RSI, e a altura segue os painéis. O `fill` troca a cada
    // dado novo de indicador, e quem repreenche as séries é o efeito do histórico, sem recriar o gráfico.
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [chartType, selectedScale, ticker, hasHistory, layout, height]);

  // Dicas de análise técnica: padrões de vela e legendas dos indicadores sobre o gráfico
  const candleMode = chartType === "candle";
  const hintsOn = hints !== null;
  const showPatterns = hintsOn && settings.patterns;
  const days = useMemo(() => initialData.map(dayOf), [initialData]);
  const lastDay = days[days.length - 1] as string | undefined;
  const periodStart = fromDay(initialData, selectedScale);
  const allPatterns = hints?.patterns?.patterns;
  const periodPatterns = useMemo(() => patternsSince(allPatterns ?? [], periodStart), [allPatterns, periodStart]);
  const hoverDay = hover?.day ?? null;
  const activePattern =
    hoverDay !== null && candleMode && showPatterns ? patternOn(periodPatterns, hoverDay) : undefined;
  const chartKey = [chartType, selectedScale, ticker, hasHistory, layout, height].join("|");
  const shortAverage = averages.length >= 2 && averages[0].period > averages[1].period ? 1 : 0;

  const annotations = useMemo<Annotations>(() => {
    if (!hintsOn) return { markers: [], shapes: {} };
    const colors = readAnnotationColors();
    const series = indicators?.series ?? {};
    const shapes: Annotations["shapes"] = {};
    let markers: Annotations["markers"] = [];

    if (candleMode && settings.patterns) {
      markers = patternMarkers(periodPatterns, colors);
      shapes.price = patternShapes(periodPatterns, activePattern, days, colors);
    }
    if (panels.includes("rsi")) shapes.rsi = rsiShapes(rsi_overbought, rsi_oversold, colors);
    if (panels.includes("macd") && series.macd) {
      shapes.macd = crossoverShapes(series.macd.line, series.macd.signal, periodStart, MACD_PHRASES, colors);
    }
    if (averages.length >= 2 && series.averages?.length) {
      const short = series.averages[shortAverage]?.points;
      const long = series.averages[1 - shortAverage]?.points;
      if (short && long) shapes.average = crossoverShapes(short, long, periodStart, AVERAGE_PHRASES, colors);
    }
    return { markers, shapes };
    // `panels` e `averages` mudam junto com `layout`, que já está nas dependências
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [
    hintsOn,
    candleMode,
    settings.patterns,
    periodPatterns,
    activePattern,
    days,
    indicators,
    periodStart,
    layout,
    shortAverage,
  ]);

  useChartAnnotations(
    {
      chart: chartInstance,
      series: {
        price: () => seriesRef.current,
        rsi: () => linesRef.current.get("rsi"),
        macd: () => linesRef.current.get("macd:line"),
        average: () => linesRef.current.get(`average:${shortAverage}`),
      },
    },
    chartKey,
    annotations,
  );

  // Leva o gráfico até o padrão da lista e abre o card dele
  function focusPattern(pattern: CandlePattern) {
    const chart = chartInstance.current;
    if (!chart) return;
    const index = days.indexOf(pattern.end);
    const timeScale = chart.timeScale();
    timeScale.setVisibleRange({
      from: days[Math.max(0, index - 15)],
      to: days[Math.min(days.length - 1, index + 10)],
    });
    setHover({
      day: pattern.end,
      x: timeScale.timeToCoordinate(pattern.end) ?? 0,
      width: chartRef.current?.clientWidth ?? 0,
    });
  }

  function goToToday() {
    seriesRef.current?.priceScale().applyOptions({ autoScale: true });
    chartInstance.current?.timeScale().scrollToRealTime();
  }

  const loadingIndicators = indicatorsStatus === "pending" && !indicators;
  const priceClose = hoverDay === null ? initialData[initialData.length - 1]?.close : closeByDay.get(hoverDay);
  const series: Series = indicators?.series ?? {};
  const bollingerLabel = `Bollinger ${settings.params.bollinger_period} ${displayNumber(settings.params.bollinger_deviations, 0)}`;
  const removeAverage = (index: number) =>
    onSettingsChange(
      averages.length === 1
        ? toggled(settings, "averages", false)
        : withParams(settings, { averages: averages.filter((_, i) => i !== index) }),
    );
  const editIndicator = (key: IndicatorKey) => {
    setExpanded(key);
    setSelectorOpen(true);
  };
  const todayPattern = [...periodPatterns].reverse().find((pattern) => pattern.end === lastDay);
  const freshAnswer =
    hints?.challenge?.last && lastDay && isAnswerFresh(hints.challenge.last, lastDay) ? hints.challenge.last : null;
  const notice = patternNotice();
  const turnOnFirstAverage = () =>
    onSettingsChange(toggled(withParams(settings, { averages: [{ kind: "sma", period: 20 }] }), "averages", true));

  /** O aviso de padrões acima do gráfico, quando há o que dizer. */
  function patternNotice(): PatternNoticeProps | null {
    if (!hints || !showPatterns || !hasHistory) return null;
    if (!hints.patterns) {
      return hints.patternsStatus === "error" && candleMode ? { kind: "error", onRetry: hints.onRetryPatterns } : null;
    }
    if (!candleMode) {
      if (periodPatterns.length === 0) return null;
      return {
        kind: "line",
        count: periodPatterns.length,
        todayCode: todayPattern?.code ?? null,
        onSeeCandles: () => setChartType("candle"),
      };
    }
    if (periodPatterns.length > 0 || !lastDay) return null;
    const all = hints.patterns.patterns;
    const bigger = nextScaleWithPatterns(
      TIME_SCALES,
      selectedScale,
      (scale) => patternsSince(all, fromDay(initialData, scale)).length,
    );
    return {
      kind: "empty",
      from: periodStart,
      to: lastDay,
      suggestion: bigger && { label: SCALE_LABELS[bigger.scale], count: bigger.count },
      onSuggest: () => bigger && setSelectedScale(bigger.scale),
    };
  }

  return (
    <Card>
      {/* Controles: período e tipo à esquerda, volta ao dia de hoje à direita */}
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
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
          </div>
          <Button variant="outline" size="sm" onClick={goToToday}>
            Ir pro dia de hoje
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid gap-2.5">
          {/* Primeiro uso */}
          {settings.visible.length === 0 && hasHistory && (
            <Alert variant="info">
              <Sparkles />
              <AlertDescription>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="flex-1 text-foreground">
                    <b>Novo: indicadores técnicos.</b> Linhas e painéis que resumem a tendência e a força do preço.
                  </span>
                  <Button size="sm" onClick={turnOnFirstAverage}>
                    Ligar a média de 20
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setSelectorOpen(true)}>
                    Ver todos
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Legenda do que está sobre o preço e o seletor */}
          <div className="flex items-start justify-between gap-2.5">
            <div className="flex flex-wrap gap-1.5">
              <LegendItem
                token="--chart-1-canvas"
                name={ticker}
                value={priceClose === undefined ? "—" : displayMoney(priceClose)}
              />
              {loadingIndicators ? (
                [...averages, ...(showBollinger ? [null] : [])].map((_, i) => (
                  <Skeleton key={i} className="h-6.5 w-25" />
                ))
              ) : (
                <>
                  {averages.map((average, index) => {
                    const points = series.averages?.[index]?.points;
                    return (
                      <LegendItem
                        key={index}
                        token={AVERAGE_COLORS[index]}
                        name={averageLabel(average)}
                        value={formatOrMissing(
                          valueOn(points, hoverDay),
                          average.period,
                          initialData.length,
                          displayMoney,
                        )}
                        onRemove={() => removeAverage(index)}
                      />
                    );
                  })}
                  {showBollinger && (
                    <LegendItem
                      token="--chart-2"
                      name={bollingerLabel}
                      value={bandsValue(series, hoverDay, settings.params.bollinger_period, initialData.length)}
                      onRemove={() => onSettingsChange(toggled(settings, "bollinger", false))}
                    />
                  )}
                </>
              )}
            </div>
            <div className="flex items-center gap-2">
              {hintsOn && (
                <PatternSwitch
                  checked={settings.patterns}
                  onCheckedChange={(patterns) => onSettingsChange({ ...settings, patterns })}
                />
              )}
              <IndicatorSelector
                settings={settings}
                summary={indicators?.summary}
                onChange={onSettingsChange}
                open={selectorOpen}
                onOpenChange={setSelectorOpen}
                expanded={expanded}
                onExpandedChange={setExpanded}
              />
            </div>
          </div>

          {/* Desafio da vela e avisos dos padrões */}
          {hints?.challenge && (hints.challenge.open || freshAnswer) && (
            <ChallengeStrip
              challenge={hints.challenge}
              answer={freshAnswer}
              pending={hints.answering}
              onAnswer={hints.onAnswer}
            />
          )}
          {notice && <PatternNotice {...notice} />}

          {/* Gráfico, com o nome e o valor de cada painel no canto */}
          {hasHistory ? (
            <div className="relative">
              <div ref={chartRef} className="w-full" style={{ height }} />
              {panels.map((key, index) => (
                <div
                  key={key}
                  className="group absolute left-2 z-10 flex items-center gap-1 text-xs"
                  style={{ top: PRICE_HEIGHT + index * panelHeight + 4 }}
                >
                  {key !== "volume" && loadingIndicators ? (
                    <Skeleton className="h-4 w-24" />
                  ) : (
                    <span className="rounded-sm bg-card/85 px-1">
                      <PaneLabel
                        indicator={key}
                        settings={settings}
                        series={series}
                        day={hoverDay}
                        candles={initialData}
                      />
                    </span>
                  )}
                  {/* Ações do painel: editar os parâmetros e desligar */}
                  <div className="hidden gap-0.5 rounded-md bg-card p-0.5 ring-1 ring-input group-focus-within:flex group-hover:flex">
                    {INDICATOR_BY_KEY[key].summary && (
                      <Button
                        variant="ghost"
                        size="icon-xs"
                        aria-label={`Editar ${INDICATOR_BY_KEY[key].name}`}
                        onClick={() => editIndicator(key)}
                      >
                        <Settings />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon-xs"
                      aria-label={`Desligar ${INDICATOR_BY_KEY[key].name}`}
                      onClick={() => onSettingsChange(toggled(settings, key, false))}
                    >
                      <X />
                    </Button>
                  </div>
                </div>
              ))}
              {/* Card do padrão sob a mira */}
              {hover && activePattern && hints && (
                <PatternCard
                  className="pointer-events-none absolute top-3 z-20"
                  style={{ left: popLeft(hover, CARD_WIDTH), width: CARD_WIDTH }}
                  ticker={ticker}
                  pattern={activePattern}
                  stats={statsOf(hints.patterns, activePattern.code)}
                  today={activePattern.end === lastDay}
                  challengeOpen={hints.challenge?.open?.pattern_date === activePattern.end}
                />
              )}
              {/* Quadro do dia apontado pela mira */}
              {hover && !activePattern && (
                <div
                  className="pointer-events-none absolute top-3 z-20 grid gap-0.5 rounded-xl border bg-popover px-3 py-2.5 text-xs shadow-lg"
                  style={{ left: popLeft(hover, POP_WIDTH), width: POP_WIDTH }}
                >
                  <b>{displayCrosshairDay(hover.day)}</b>
                  <PopRow
                    token="--chart-1-canvas"
                    name="Fechamento"
                    value={priceClose === undefined ? "—" : displayMoney(priceClose)}
                  />
                  {!loadingIndicators &&
                    averages.map((average, index) => (
                      <PopRow
                        key={index}
                        token={AVERAGE_COLORS[index]}
                        name={averageLabel(average)}
                        value={displayOrDash(valueOn(series.averages?.[index]?.points, hover.day), displayMoney)}
                      />
                    ))}
                  {!loadingIndicators && showBollinger && (
                    <PopRow
                      token="--chart-2"
                      name="Bollinger"
                      value={bandsValue(series, hover.day, settings.params.bollinger_period, Infinity)}
                    />
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="flex h-90 items-center justify-center text-muted-foreground">
              Nenhum dado de histórico disponível.
            </div>
          )}

          {/* Lista dos padrões do período */}
          {hasHistory && candleMode && showPatterns && periodPatterns.length > 0 && (
            <PatternList
              patterns={periodPatterns}
              openDay={hints?.challenge?.open?.pattern_date ?? null}
              activeDay={activePattern?.end ?? null}
              onSelect={focusPattern}
            />
          )}

          {/* Erro dos indicadores: o preço segue atualizado */}
          {failed && settings.visible.length > 0 && (
            <Alert variant="destructive">
              <AlertCircle />
              <AlertDescription>
                Não deu para calcular os indicadores agora. O preço continua atualizado.
              </AlertDescription>
              <AlertAction>
                <Button variant="outline" size="sm" onClick={onRetryIndicators}>
                  Tentar de novo
                </Button>
              </AlertAction>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/** O quadro fica à direita da mira e passa para a esquerda perto da borda. */
function popLeft({ x, width }: { x: number; width: number }, popWidth: number) {
  return x + 16 + popWidth > width ? x - 16 - popWidth : x + 16;
}

/** O valor do dia, ou quando o indicador aparece se o histórico ainda é curto. */
function formatOrMissing(value: number | null, needed: number, sessions: number, format: (value: number) => string) {
  if (value !== null) return format(value);
  if (sessions < needed) return `aparece com ${needed} pregões · faltam ${needed - sessions}`;
  return "—";
}

function bandsValue(series: Series, day: string | null, period: number, sessions: number) {
  const lower = valueOn(series.bollinger?.lower, day);
  const upper = valueOn(series.bollinger?.upper, day);
  if (lower === null || upper === null) return formatOrMissing(null, period, sessions, String);
  return `${displayNumber(lower)} a ${displayNumber(upper)}`;
}

const displayOrDash = (value: number | null, format: (value: number) => string) =>
  value === null ? "—" : format(value);

/** "2023-02-15" → "qua 15 fev 23", o dia que a mira aponta. */
function displayCrosshairDay(isoDate: string) {
  const parts = new Intl.DateTimeFormat("pt-BR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    year: "2-digit",
  }).formatToParts(parseLocalDate(isoDate));
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find((p) => p.type === type)?.value.replace(".", "") ?? "";
  return `${part("weekday")} ${part("day")} ${part("month")} ${part("year")}`;
}

function PopRow({ token, name, value }: { token: string; name: string; value: string }) {
  return (
    <div className="flex justify-between gap-2">
      <span className="flex items-center gap-1.5">
        <Swatch token={token} shape="line" />
        {name}
      </span>
      <span className="font-mono tabular-nums">{value}</span>
    </div>
  );
}

interface LegendItemProps {
  token: string;
  name: string;
  value: string;
  onRemove?: () => void;
}

function LegendItem({ token, name, value, onRemove }: LegendItemProps) {
  const missing = value.startsWith("aparece");
  return (
    <span
      className={cn(
        "group inline-flex h-6.5 items-center gap-1.5 rounded-md bg-subtle px-2 text-xs",
        onRemove && "hover:bg-card hover:ring-1 hover:ring-input hover:ring-inset",
      )}
    >
      <Swatch token={token} shape="line" />
      <span className="font-medium">{name}</span>
      <span
        className={cn("font-mono tabular-nums", missing && "font-sans text-muted-foreground")}
        style={missing ? undefined : { color: `var(${token})` }}
      >
        {value}
      </span>
      {onRemove && (
        <Button
          variant="ghost"
          size="icon-xs"
          className="hidden group-focus-within:inline-flex group-hover:inline-flex"
          aria-label={`Desligar ${name}`}
          onClick={onRemove}
        >
          <X />
        </Button>
      )}
    </span>
  );
}

interface PaneLabelProps {
  indicator: IndicatorKey;
  settings: IndicatorSettings;
  series: Series;
  day: string | null;
  candles: StockCandle[];
}

/** Nome, parâmetros e valor do dia de um painel. */
function PaneLabel({ indicator, settings, series, day, candles }: PaneLabelProps) {
  const { params } = settings;
  const sessions = candles.length;
  const info = INDICATOR_BY_KEY[indicator];
  const number = (value: number) => displayNumber(value, 1);
  let text: string;
  switch (indicator) {
    case "volume": {
      const candle = day === null ? candles[candles.length - 1] : candles.find((c) => c.price_date.startsWith(day));
      text = `Volume · ${candle ? displayCompactNumber(candle.volume) : "—"}`;
      break;
    }
    case "rsi":
      text = `IFR ${params.rsi_period} · ${formatOrMissing(valueOn(series.rsi, day), params.rsi_period + 1, sessions, number)}`;
      break;
    case "macd": {
      const needed = params.macd_slow + params.macd_signal - 1;
      const line = valueOn(series.macd?.line, day);
      const signal = valueOn(series.macd?.signal, day);
      text = `MACD ${params.macd_fast}, ${params.macd_slow}, ${params.macd_signal} · ${
        line !== null && signal !== null
          ? `${displayNumber(line)} · sinal ${displayNumber(signal)}`
          : formatOrMissing(null, needed, sessions, number)
      }`;
      break;
    }
    case "stochastic":
      text = `Estocástico ${params.stochastic_k}, ${params.stochastic_d} · ${formatOrMissing(
        valueOn(series.stochastic?.k, day),
        params.stochastic_k,
        sessions,
        number,
      )}`;
      break;
    case "atr":
      text = `ATR ${params.atr_period} · ${formatOrMissing(valueOn(series.atr, day), params.atr_period, sessions, displayMoney)}`;
      break;
    default:
      text = `OBV · ${formatOrMissing(valueOn(series.obv, day), 1, sessions, displaySignedCompact)}`;
  }
  return (
    <span className="flex items-center gap-1.5">
      {info.color && <Swatch token={info.color} shape="line" />}
      {text}
    </span>
  );
}
