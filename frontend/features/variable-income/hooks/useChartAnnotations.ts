import { useEffect, useRef, type RefObject } from "react";
import {
  createSeriesMarkers,
  type IChartApi,
  type ISeriesApi,
  type ISeriesMarkersPluginApi,
  type SeriesMarker,
  type SeriesType,
  type Time,
} from "lightweight-charts";
import { ChartOverlay, type OverlayShape } from "../lib/chart-overlay";

/** O que desenhar em cada série; o que falta (ou vem vazio) sai do gráfico. */
export interface Annotations {
  markers: SeriesMarker<Time>[];
  /** Por chave de série: `price`, `rsi`, `macd` e `average`. */
  shapes: Record<string, OverlayShape[]>;
}

interface ChartRefs {
  chart: RefObject<IChartApi | null>;
  /** Por chave, a série em que a anotação se liga; lida na hora, porque o gráfico é recriado. */
  series: Record<string, () => ISeriesApi<SeriesType> | null | undefined>;
}

interface Attached {
  chart: IChartApi;
  overlays: Map<string, { series: ISeriesApi<SeriesType>; overlay: ChartOverlay }>;
  markers: ISeriesMarkersPluginApi<Time> | null;
}

/**
 * Aplica marcadores e overlays ao gráfico que está no ar. Quando `chartKey` muda o gráfico foi
 * recriado: o que estava ligado a ele se foi com ele, e as anotações são ligadas de novo à
 * série nova. Este efeito vem depois do que cria o gráfico.
 */
export function useChartAnnotations(refs: ChartRefs, chartKey: string, annotations: Annotations) {
  const attached = useRef<Attached | null>(null);

  useEffect(() => {
    const chart = refs.chart.current;
    if (!chart) return;
    if (attached.current?.chart !== chart) attached.current = { chart, overlays: new Map(), markers: null };
    const state = attached.current;

    for (const [key, seriesOf] of Object.entries(refs.series)) {
      const series = seriesOf();
      if (!series) continue;
      const known = state.overlays.get(key);
      let entry = known?.series === series ? known : undefined;
      if (!entry) {
        const background = getComputedStyle(document.documentElement).getPropertyValue("--card").trim();
        entry = { series, overlay: new ChartOverlay(background || "#ffffff") };
        series.attachPrimitive(entry.overlay);
        state.overlays.set(key, entry);
      }
      entry.overlay.setShapes(annotations.shapes[key] ?? []);
    }

    const price = refs.series.price?.();
    if (price) {
      state.markers ??= createSeriesMarkers(price, []);
      state.markers.setMarkers(annotations.markers);
    }
    // O gráfico novo é sinalizado por `chartKey`; `refs` muda de identidade a cada render
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [chartKey, annotations]);
}
