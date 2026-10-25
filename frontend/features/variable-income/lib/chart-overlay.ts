import type {
  IChartApiBase,
  IPrimitivePaneRenderer,
  IPrimitivePaneView,
  ISeriesApi,
  ISeriesPrimitive,
  SeriesAttachedParameter,
  SeriesType,
  Time,
} from "lightweight-charts";

type DrawTarget = Parameters<IPrimitivePaneRenderer["draw"]>[0];

/** O que o overlay desenha sobre o painel da série; `time` é o dia ISO e `value`, o preço ou o nível. */
export type OverlayShape =
  | { kind: "band"; from: string; to: string; color: string }
  | { kind: "outline"; from: string; to: string; color: string }
  | { kind: "circle"; time: string; value: number; color: string }
  // `dy` afasta a legenda da linha do nível, em px (negativo sobe)
  | { kind: "level-label"; value: number; text: string; color: string; dy?: number }
  | { kind: "note"; time: string; value: number; text: string; color: string };

const FONT = "12px -apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif";
const CIRCLE_RADIUS = 5;

/** Desenha faixas, contornos, círculos e legendas sobre o painel da série em que está ligado. */
export class ChartOverlay implements ISeriesPrimitive<Time> {
  private shapes: OverlayShape[] = [];
  private chart: IChartApiBase<Time> | null = null;
  private series: ISeriesApi<SeriesType, Time> | null = null;
  private requestUpdate: (() => void) | null = null;

  private readonly background: string;

  /** `background` é a cor do cartão do tema: as legendas nascem sobre ela. */
  constructor(background: string) {
    this.background = background;
  }

  // As faixas ficam atrás das velas; o resto, por cima
  private readonly views: readonly IPrimitivePaneView[] = [
    { zOrder: () => "bottom", renderer: () => this.renderer((shape) => shape.kind === "band") },
    { zOrder: () => "top", renderer: () => this.renderer((shape) => shape.kind !== "band") },
  ];

  attached({ chart, series, requestUpdate }: SeriesAttachedParameter<Time>) {
    this.chart = chart;
    this.series = series;
    this.requestUpdate = requestUpdate;
  }

  detached() {
    this.chart = null;
    this.series = null;
    this.requestUpdate = null;
  }

  paneViews() {
    return this.views;
  }

  setShapes(shapes: OverlayShape[]) {
    this.shapes = shapes;
    this.requestUpdate?.();
  }

  private renderer(accepts: (shape: OverlayShape) => boolean): IPrimitivePaneRenderer {
    return { draw: (target) => this.draw(target, accepts) };
  }

  private draw(target: DrawTarget, accepts: (shape: OverlayShape) => boolean) {
    const { chart, series } = this;
    if (!chart || !series) return;
    const timeScale = chart.timeScale();
    const halfBar = timeScale.options().barSpacing / 2;
    const x = (day: string) => timeScale.timeToCoordinate(day as Time);
    const y = (value: number) => series.priceToCoordinate(value);

    target.useMediaCoordinateSpace(({ context: ctx, mediaSize }) => {
      ctx.font = FONT;
      ctx.textBaseline = "middle";
      for (const shape of this.shapes.filter(accepts)) {
        if (shape.kind === "band" || shape.kind === "outline") {
          const from = x(shape.from);
          const to = x(shape.to);
          if (from === null || to === null) continue;
          const left = from - halfBar;
          const width = to - from + halfBar * 2;
          ctx.fillStyle = shape.color;
          if (shape.kind === "band") {
            ctx.globalAlpha = 0.14;
            ctx.fillRect(left, 0, width, mediaSize.height);
            ctx.globalAlpha = 1;
          } else {
            ctx.strokeStyle = shape.color;
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 3]);
            ctx.strokeRect(left, 2, width, mediaSize.height - 4);
            ctx.setLineDash([]);
          }
        } else if (shape.kind === "circle") {
          const cx = x(shape.time);
          const cy = y(shape.value);
          if (cx === null || cy === null) continue;
          ctx.beginPath();
          ctx.arc(cx, cy, CIRCLE_RADIUS, 0, Math.PI * 2);
          ctx.lineWidth = 2;
          ctx.strokeStyle = shape.color;
          ctx.stroke();
        } else if (shape.kind === "level-label") {
          const cy = y(shape.value);
          if (cy === null) continue;
          drawLabel(ctx, shape.text, 8, cy + (shape.dy ?? 0), shape.color, this.background, "left");
        } else {
          const cx = x(shape.time);
          const cy = y(shape.value);
          if (cx === null || cy === null) continue;
          // A frase fica ao lado do círculo, do lado que tem mais espaço
          const room = mediaSize.width - cx;
          const width = ctx.measureText(shape.text).width + 12;
          const fitsRight = room > width + CIRCLE_RADIUS + 8;
          // A legenda nunca passa da borda esquerda do painel
          const anchor = fitsRight ? cx + CIRCLE_RADIUS + 6 : Math.max(cx - CIRCLE_RADIUS - 6, width + 4);
          drawLabel(ctx, shape.text, anchor, cy, shape.color, this.background, fitsRight ? "left" : "right");
        }
      }
    });
  }
}

type DrawContext = Parameters<Parameters<DrawTarget["useMediaCoordinateSpace"]>[0]>[0]["context"];

function drawLabel(
  ctx: DrawContext,
  text: string,
  x: number,
  y: number,
  color: string,
  background: string,
  align: "left" | "right",
) {
  const width = ctx.measureText(text).width + 12;
  const left = align === "left" ? x : x - width;
  ctx.globalAlpha = 0.9;
  ctx.fillStyle = background;
  ctx.beginPath();
  ctx.roundRect(left, y - 10, width, 20, 5);
  ctx.fill();
  ctx.globalAlpha = 1;
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.textAlign = "left";
  ctx.fillText(text, left + 6, y);
}
