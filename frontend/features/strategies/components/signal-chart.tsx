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
import { displayMoney } from "@/shared/lib/utils/display";
import type { StrategySignal } from "@/types";

type SignalLine = StrategySignal["lines"][number];

/** Linha já salva que a prévia substitui: desenhada tracejada, só para comparar. */
export type SavedSignalLine = SignalLine & { legend: string };

type SignalChartProps = {
  lines: SignalLine[];
  markers: StrategySignal["markers"];
  savedLines: SavedSignalLine[];
};

/** Cor de cada linha do sinal, lida do tema (o canvas pede hex). */
const LINE_STYLE: Record<SignalLine["key"], { token: string; width: LineWidth }> = {
  price: { token: "--faint-foreground", width: 1 },
  short: { token: "--chart-1-canvas", width: 2 },
  long: { token: "--chart-5", width: 2 },
};

/** Preço e médias da estratégia no ativo, com ▲ nos dias de compra e ▼ nos de venda. */
export function SignalChart({ lines, markers, savedLines }: SignalChartProps) {
  const container = useRef<HTMLDivElement>(null);

  // O gráfico nasce vazio e é redesenhado a cada sinal novo
  useEffect(() => {
    if (!container.current) return;
    const styles = getComputedStyle(document.documentElement);
    const color = (token: string) => styles.getPropertyValue(token).trim();

    const chart = createChart(container.current, {
      height: 210,
      localization: { priceFormatter: displayMoney },
      rightPriceScale: { borderVisible: false },
      timeScale: { borderVisible: false },
      layout: { attributionLogo: false },
    });

    const toData = (line: SignalLine) => line.points.map((point) => ({ time: point.date, value: point.value }));

    for (const saved of savedLines) {
      chart
        .addSeries(LineSeries, {
          color: color(LINE_STYLE[saved.key].token),
          lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          priceLineVisible: false,
          lastValueVisible: false,
        })
        .setData(toData(saved));
    }

    let priceSeries: ReturnType<typeof chart.addSeries<"Line">> | null = null;
    for (const line of lines) {
      const { token, width } = LINE_STYLE[line.key];
      const series = chart.addSeries(LineSeries, {
        color: color(token),
        lineWidth: width,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      series.setData(toData(line));
      if (line.key === "price") priceSeries = series;
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
  }, [lines, markers, savedLines]);

  return <div ref={container} className="h-52.5 w-full" role="img" aria-label="Gráfico do que a estratégia olha" />;
}
