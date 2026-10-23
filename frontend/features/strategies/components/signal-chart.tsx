import { useEffect, useRef } from "react";
import {
  createChart,
  createSeriesMarkers,
  LineSeries,
  LineStyle,
  type LineWidth,
  type SeriesMarker,
  type Time,
} from "lightweight-charts";
import { cn } from "@/shared/lib/utils";
import { displayMoney } from "@/shared/lib/utils/display";
import type { StrategySignal } from "@/types";

type SignalLine = StrategySignal["lines"][number];
type SignalStyle = SignalLine["style"];

/** Linha já salva que a prévia substitui: desenhada tracejada, só para comparar. */
export type SavedSignalLine = SignalLine & { legend: string };

type SignalChartProps = {
  lines: SignalLine[];
  levels: StrategySignal["levels"];
  markers: StrategySignal["markers"];
  savedLines: SavedSignalLine[];
};

/** Cor de cada estilo de linha, lida do tema (o canvas pede hex). */
const LINE_STYLE: Record<SignalStyle, { token: string; width: LineWidth }> = {
  price: { token: "--faint-foreground", width: 1 },
  fast: { token: "--chart-1-canvas", width: 2 },
  slow: { token: "--chart-5", width: 2 },
  channel: { token: "--chart-3", width: 1 },
  oscillator: { token: "--chart-1-canvas", width: 2 },
};

const PRICE_PANE = 0;
const OSCILLATOR_PANE = 1;
const PRICE_HEIGHT = 210;
const OSCILLATOR_HEIGHT = 140;

// O preço sai em reais
const MONEY_FORMAT = { type: "custom", minMove: 0.01, formatter: displayMoney } as const;

/** O eixo do oscilador (0 a 100) mostra só o 0 e as faixas da estratégia, para os números não se sobreporem. */
const oscillatorFormat = (levels: StrategySignal["levels"]) =>
  ({
    type: "custom",
    minMove: 1,
    formatter: (value: number) => (value === 0 || levels.some((level) => level.value === value) ? value.toFixed(0) : ""),
  }) as const;

/** Preço e linhas da estratégia, com o oscilador num 2º painel de 0 a 100 e ▲ nos dias de compra e ▼ nos de venda. */
export function SignalChart({ lines, levels, markers, savedLines }: SignalChartProps) {
  const container = useRef<HTMLDivElement>(null);
  const hasOscillator = lines.some((line) => line.pane === "oscillator");
  const height = hasOscillator ? PRICE_HEIGHT + OSCILLATOR_HEIGHT : PRICE_HEIGHT;

  // O gráfico nasce vazio e é redesenhado a cada sinal novo
  useEffect(() => {
    if (!container.current) return;
    const styles = getComputedStyle(document.documentElement);
    const color = (token: string) => styles.getPropertyValue(token).trim();

    const chart = createChart(container.current, {
      height,
      rightPriceScale: { borderVisible: false },
      timeScale: { borderVisible: false },
      layout: { attributionLogo: false },
    });

    const toData = (line: SignalLine) => line.points.map((point) => ({ time: point.date, value: point.value }));
    const paneOf = (line: SignalLine) => (line.pane === "oscillator" ? OSCILLATOR_PANE : PRICE_PANE);

    for (const saved of savedLines) {
      chart
        .addSeries(
          LineSeries,
          {
            color: color(LINE_STYLE[saved.style].token),
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            priceLineVisible: false,
            lastValueVisible: false,
            priceFormat: saved.pane === "oscillator" ? oscillatorFormat(levels) : MONEY_FORMAT,
          },
          paneOf(saved),
        )
        .setData(toData(saved));
    }

    let priceSeries: ReturnType<typeof chart.addSeries<"Line">> | null = null;
    let oscillatorSeries: ReturnType<typeof chart.addSeries<"Line">> | null = null;
    for (const line of lines) {
      const { token, width } = LINE_STYLE[line.style];
      const oscillator = line.pane === "oscillator";
      const series = chart.addSeries(
        LineSeries,
        {
          color: color(token),
          lineWidth: width,
          priceLineVisible: false,
          lastValueVisible: false,
          priceFormat: oscillator ? oscillatorFormat(levels) : MONEY_FORMAT,
          ...(oscillator && {
            autoscaleInfoProvider: () => ({ priceRange: { minValue: 0, maxValue: 100 } }),
          }),
        },
        paneOf(line),
      );
      series.setData(toData(line));
      if (line.style === "price") priceSeries = series;
      if (oscillator) oscillatorSeries ??= series;
    }

    // Faixas do oscilador, como o 30 e o 70 do IFR
    for (const level of levels) {
      oscillatorSeries?.createPriceLine({
        price: level.value,
        color: color("--faint-foreground"),
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        axisLabelVisible: true,
        title: level.label,
      });
    }

    if (oscillatorSeries) {
      const [pricePane, oscillatorPane] = chart.panes();
      pricePane?.setStretchFactor(PRICE_HEIGHT);
      oscillatorPane?.setStretchFactor(OSCILLATOR_HEIGHT);
      chart.priceScale("right", OSCILLATOR_PANE).applyOptions({ scaleMargins: { top: 0.05, bottom: 0.05 } });
    }

    if (priceSeries) {
      const success = color("--success");
      const destructive = color("--destructive");
      const marks: SeriesMarker<Time>[] = markers.map((marker) =>
        marker.side === "buy"
          ? { time: marker.date, position: "belowBar", shape: "arrowUp", color: success }
          : { time: marker.date, position: "aboveBar", shape: "arrowDown", color: destructive },
      );
      createSeriesMarkers(priceSeries, marks);
    }

    chart.timeScale().fitContent();
    return () => chart.remove();
  }, [lines, levels, markers, savedLines, height]);

  return (
    <div
      ref={container}
      className={cn("w-full", hasOscillator ? "h-87.5" : "h-52.5")}
      role="img"
      aria-label="Gráfico do que a estratégia olha"
    />
  );
}
