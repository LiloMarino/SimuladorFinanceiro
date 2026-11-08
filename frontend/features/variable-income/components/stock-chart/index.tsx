import { useState, useMemo } from "react";
import { AlertCircle, Settings, X } from "lucide-react";
import { Alert, AlertAction, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { displayMoney, displayNumber } from "@/shared/lib/utils/display";
import { useCorporateEvents } from "../../hooks/queries/useCorporateEvents";
import { CorporateEventNote } from "./corporate-event-note";
import type {
  CandlePattern,
  CandlePatterns,
  IndicatorKey,
  IndicatorSettings,
  StockCandle,
  TechnicalIndicators,
} from "@/types";
import { IndicatorSelector } from "../indicator-selector";
import { PatternCard } from "../candle-patterns/pattern-card";
import { PatternNotice, PatternSwitch, type PatternNoticeProps } from "../candle-patterns/pattern-controls";
import { PatternList } from "../candle-patterns/pattern-list";
import { useChartAnnotations, type Annotations } from "../../hooks/useChartAnnotations";
import {
  corporateShapes,
  AVERAGE_PHRASES,
  MACD_PHRASES,
  crossoverShapes,
  patternMarkers,
  patternShapes,
  rsiShapes,
} from "../../lib/chart-annotations";
import { nextScaleWithPatterns, patternOn, patternsSince, statsOf } from "@/shared/lib/pattern-view";
import {
  averageColor,
  INDICATOR_BY_KEY,
  PANEL_KEYS,
  averageLabel,
  isShown,
  toggled,
  withParams,
} from "../../lib/indicators";
import {
  CARD_WIDTH,
  NO_SERIES,
  POP_WIDTH,
  PRICE_HEIGHT,
  SCALE_LABELS,
  TIME_AXIS_HEIGHT,
  TIME_SCALES,
  paneHeight,
  type ChartType,
  type CrosshairHover,
  type Series,
  type TimeScale,
} from "./chart-config";
import {
  bandsValue,
  dayOf,
  displayCrosshairDay,
  displayOrDash,
  formatOrMissing,
  fromDay,
  popLeft,
  readAnnotationColors,
  valueOn,
} from "./chart-helpers";
import { LegendItem } from "./legend-item";
import { PaneLabel } from "./pane-label";
import { PopRow } from "./pop-row";
import { useStockChartInstance } from "./useStockChartInstance";

/** As dicas de análise técnica do gráfico; `null` quando a partida as desliga. */
interface ChartHints {
  patterns: CandlePatterns | undefined;
  patternsStatus: "pending" | "error" | "success";
  onRetryPatterns: () => void;
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

const byTime = (a: { time: unknown }, b: { time: unknown }) => String(a.time).localeCompare(String(b.time));

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
  const [hover, setHover] = useState<CrosshairHover | null>(null);
  const [expanded, setExpanded] = useState<IndicatorKey | null>(null);
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

  // O gráfico nasce aqui, antes do efeito de anotações que se liga às refs dele
  const { chartRef, chartInstance, seriesRef, linesRef } = useStockChartInstance({
    ticker,
    history: initialData,
    indicators,
    chartType,
    selectedScale,
    hasHistory,
    panels,
    averages,
    showBollinger,
    rsiOverbought: rsi_overbought,
    rsiOversold: rsi_oversold,
    panelHeight,
    height,
    layout,
    onHover: setHover,
  });

  // Dicas de análise técnica: padrões de vela e legendas dos indicadores sobre o gráfico
  const candleMode = chartType === "candle";
  const hintsOn = hints !== null;
  const showPatterns = hintsOn && settings.patterns;
  const hoverDay = hover?.day ?? null;
  const days = useMemo(() => initialData.map(dayOf), [initialData]);
  const { data: corporate } = useCorporateEvents(ticker);
  const corporateEvents = corporate?.events;
  const hoverEvents = hoverDay === null ? [] : (corporateEvents ?? []).filter((event) => event.ex_date === hoverDay);
  const lastDay = days[days.length - 1];
  const periodStart = fromDay(initialData, selectedScale);
  const allPatterns = hints?.patterns?.patterns;
  const periodPatterns = useMemo(() => patternsSince(allPatterns ?? [], periodStart), [allPatterns, periodStart]);
  const activePattern =
    hoverDay !== null && candleMode && showPatterns ? patternOn(periodPatterns, hoverDay) : undefined;
  const chartKey = [chartType, selectedScale, ticker, hasHistory, layout, height].join("|");
  const [firstAverage, secondAverage] = averages;
  const shortAverage = firstAverage && secondAverage && firstAverage.period > secondAverage.period ? 1 : 0;

  const annotations = useMemo<Annotations>(() => {
    const colors = readAnnotationColors();
    // Os selos de provento e desdobramento valem com ou sem as dicas técnicas
    const corporateOnChart = corporateShapes(corporateEvents ?? [], days, colors);
    if (!hintsOn) return { markers: [], shapes: { price: corporateOnChart } };
    const series = indicators?.series ?? NO_SERIES;
    const shapes: Annotations["shapes"] = { price: corporateOnChart };
    let markers: Annotations["markers"] = [];

    if (candleMode && settings.patterns) {
      markers = patternMarkers(periodPatterns, colors);
      shapes.price = [...patternShapes(periodPatterns, activePattern, days, colors), ...corporateOnChart];
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
    return { markers: markers.sort(byTime), shapes };
    // `panels` e `averages` mudam junto com `layout`, que já está nas dependências
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [
    hintsOn,
    corporateEvents,
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
    const from = days[Math.max(0, index - 15)];
    const to = days[Math.min(days.length - 1, index + 10)];
    if (from === undefined || to === undefined) return;
    const timeScale = chart.timeScale();
    timeScale.setVisibleRange({ from, to });
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
  const series: Series = indicators?.series ?? NO_SERIES;
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
  const notice = patternNotice();

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
          <div className="flex items-center gap-4">
            {/* Legenda dos marcadores de proventos */}
            {corporateEvents && corporateEvents.length > 0 && (
              <ul className="flex gap-3 text-xs text-muted-foreground">
                <li className="flex items-center gap-1.5">
                  <Badge variant="dividend">P</Badge>
                  Provento
                </li>
                <li className="flex items-center gap-1.5">
                  <Badge variant="split">D</Badge>
                  Desdobramento ou grupamento
                </li>
              </ul>
            )}
            <Button variant="outline" size="sm" onClick={goToToday}>
              Ir pro dia de hoje
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="grid gap-2.5">
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
                        token={averageColor(index)}
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

          {/* Avisos dos padrões */}
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
                        token={averageColor(index)}
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
                  {hoverEvents.map((event) => (
                    <CorporateEventNote key={`${event.kind}-${event.ex_date}`} event={event} />
                  ))}
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
            <PatternList patterns={periodPatterns} activeDay={activePattern?.end ?? null} onSelect={focusPattern} />
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
