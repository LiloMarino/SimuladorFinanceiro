import { useMemo, useState, type PointerEvent } from "react";
import {
  axisTicks,
  displayThousands,
  splitGainLoss,
  valueScale,
  type NetworthPoint,
  type Run,
} from "../lib/networth-model";
import { NetworthTooltip, TOOLTIP_GAP, TOOLTIP_WIDTH } from "./networth-tooltip";

const HEIGHT = 280;
const LEFT = 54;
const RIGHT = 8;
const TOP = 8;
const BOTTOM = 22;
// Até este número de pontos cada dia leva a sua bolinha
const DOT_LIMIT = 12;

type Coord = { x: number; y: number };

const fixed = (n: number) => n.toFixed(1);
const linePath = (coords: Coord[]) =>
  coords.map((c, i) => `${i === 0 ? "M" : "L"}${fixed(c.x)} ${fixed(c.y)}`).join(" ");
const closedPath = (forward: Coord[], back: Coord[]) =>
  `${linePath(forward)} ${[...back]
    .reverse()
    .map((c) => `L${fixed(c.x)} ${fixed(c.y)}`)
    .join(" ")} Z`;

/** A geometria do gráfico: depende só dos pontos e da largura, não do ponteiro. */
function buildShape(points: NetworthPoint[], width: number) {
  const plotWidth = width - LEFT - RIGHT;
  const plotHeight = HEIGHT - TOP - BOTTOM;
  const { ticks, floor, ceiling } = valueScale(points.flatMap((p) => [p.networth, p.provided, -p.debt, p.goal ?? 0]));
  const xOf = (index: number) => LEFT + (points.length > 1 ? (index / (points.length - 1)) * plotWidth : 0);
  const yOf = (value: number) => TOP + ((ceiling - value) / (ceiling - floor || 1)) * plotHeight;
  const zeroY = yOf(0);

  const provided = points.map((p, i) => ({ x: xOf(i), y: yOf(p.provided) }));
  const networth = points.map((p, i) => ({ x: xOf(i), y: yOf(p.networth) }));
  const baseline = points.map((_, i) => ({ x: xOf(i), y: zeroY }));
  const debt = points.map((p, i) => ({ x: xOf(i), y: yOf(-p.debt) }));

  // Os trechos nascem em valor, para achar onde as linhas se cruzam; o desenho converte cada um em pixels
  const { gains, losses } = splitGainLoss(
    points.map((p, i) => ({ x: xOf(i), provided: p.provided, networth: p.networth })),
  );
  const band = (run: Run) =>
    closedPath(
      run.map((r) => ({ x: r.x, y: yOf(r.networth) })),
      run.map((r) => ({ x: r.x, y: yOf(r.provided) })),
    );

  // A meta em degraus: mantém o valor até o dia do reajuste
  const goalSteps = points.flatMap((p, i) => (p.goal === undefined ? [] : [{ x: xOf(i), y: yOf(p.goal) }]));
  const goalPath = goalSteps
    .map((c, i) => {
      const before = goalSteps[i - 1];
      return before ? `L${fixed(c.x)} ${fixed(before.y)} L${fixed(c.x)} ${fixed(c.y)}` : `M${fixed(c.x)} ${fixed(c.y)}`;
    })
    .join(" ");

  return {
    ticks,
    yOf,
    provided,
    networth,
    providedArea: closedPath(provided, baseline),
    debtArea: closedPath(debt, baseline),
    debtLine: linePath(debt),
    providedLine: linePath(provided),
    networthLine: linePath(networth),
    gainBands: gains.map((run) => ({ key: run[0]?.x ?? 0, d: band(run) })),
    lossBands: losses.map((run) => ({ key: run[0]?.x ?? 0, d: band(run) })),
    goalPath,
    xOf,
    plotWidth,
    plotHeight,
  };
}

/** Patrimônio e aportado em linhas; entre elas, verde onde o dinheiro rendeu e vermelho onde encolheu. */
export function NetworthGainChart({ points, width }: { points: NetworthPoint[]; width: number }) {
  const [hover, setHover] = useState<number | null>(null);
  const shape = useMemo(() => buildShape(points, width), [points, width]);
  const xTicks = useMemo(
    () =>
      axisTicks(
        points.map((p) => p.date),
        shape.plotWidth,
      ),
    [points, shape.plotWidth],
  );
  const hasDebt = points.some((p) => p.debt > 0);

  const onMove = (event: PointerEvent<SVGRectElement>) => {
    const box = event.currentTarget.getBoundingClientRect();
    const ratio = (event.clientX - box.left) / box.width;
    setHover(Math.max(0, Math.min(points.length - 1, Math.round(ratio * (points.length - 1)))));
  };

  const hovered = hover === null ? undefined : points[hover];
  const hoveredX = hover === null ? undefined : shape.xOf(hover);
  const tooltipLeft =
    hoveredX === undefined
      ? 0
      : hoveredX + TOOLTIP_GAP + TOOLTIP_WIDTH <= width
        ? hoveredX + TOOLTIP_GAP
        : hoveredX - TOOLTIP_GAP - TOOLTIP_WIDTH;

  return (
    <div className="relative" style={{ width, height: HEIGHT }}>
      <svg
        width={width}
        height={HEIGHT}
        viewBox={`0 0 ${width} ${HEIGHT}`}
        className="block font-sans text-[11px]"
        role="img"
        aria-label="Patrimônio e aportado ao longo da partida"
      >
        {/* Grade e eixo Y */}
        {shape.ticks.map((tick) => (
          <g key={tick}>
            <line
              x1={LEFT}
              x2={width - RIGHT}
              y1={shape.yOf(tick)}
              y2={shape.yOf(tick)}
              className={tick === 0 ? "stroke-input" : "stroke-border"}
            />
            <text x={LEFT - 8} y={shape.yOf(tick) + 4} textAnchor="end" className="fill-faint-foreground">
              {displayThousands(tick)}
            </text>
          </g>
        ))}

        {/* O que saiu do bolso, com ganho e perda sobre ele */}
        <path d={shape.providedArea} className="fill-muted" />
        {shape.gainBands.map((band) => (
          <path key={band.key} d={band.d} className="fill-success/22" />
        ))}
        {shape.lossBands.map((band) => (
          <path key={band.key} d={band.d} className="fill-destructive/22" />
        ))}

        {/* Dívida abaixo do zero */}
        {hasDebt && (
          <>
            <path d={shape.debtArea} className="fill-destructive/16" />
            <path d={shape.debtLine} fill="none" className="stroke-destructive/70" strokeWidth={1.2} />
          </>
        )}

        {/* Meta, aportado e patrimônio */}
        {shape.goalPath !== "" && (
          <path
            d={shape.goalPath}
            fill="none"
            className="stroke-foreground"
            strokeWidth={2}
            strokeDasharray="2 4"
            strokeLinecap="round"
          />
        )}
        <path
          d={shape.providedLine}
          fill="none"
          className="stroke-faint-foreground"
          strokeWidth={1.6}
          strokeDasharray="6 4"
        />
        <path d={shape.networthLine} fill="none" className="stroke-foreground" strokeWidth={2} strokeLinejoin="round" />
        {points.length <= DOT_LIMIT &&
          shape.networth.map((c) => <circle key={c.x} cx={c.x} cy={c.y} r={3.5} className="fill-foreground" />)}

        {/* Eixo X */}
        {xTicks.map((tick) => (
          <text
            key={tick.index}
            x={shape.xOf(tick.index)}
            y={HEIGHT - BOTTOM + 16}
            textAnchor={tick.anchor}
            className="fill-faint-foreground"
          >
            {tick.label}
          </text>
        ))}

        {/* Ponteiro */}
        {hover !== null && hovered && hoveredX !== undefined && (
          <g pointerEvents="none">
            <line x1={hoveredX} x2={hoveredX} y1={TOP} y2={HEIGHT - BOTTOM} className="stroke-foreground/35" />
            <circle
              cx={hoveredX}
              cy={shape.provided[hover]?.y}
              r={4}
              className="fill-card stroke-faint-foreground"
              strokeWidth={2}
            />
            <circle
              cx={hoveredX}
              cy={shape.networth[hover]?.y}
              r={4}
              className="fill-card stroke-foreground"
              strokeWidth={2}
            />
            {hovered.debt > 0 && (
              <circle
                cx={hoveredX}
                cy={shape.yOf(-hovered.debt)}
                r={4}
                className="fill-card stroke-destructive"
                strokeWidth={2}
              />
            )}
          </g>
        )}

        <rect
          x={LEFT}
          y={TOP}
          width={shape.plotWidth}
          height={shape.plotHeight}
          fill="transparent"
          onPointerMove={onMove}
          onPointerLeave={() => setHover(null)}
        />
      </svg>

      {hovered && <NetworthTooltip point={hovered} left={tooltipLeft} />}
    </div>
  );
}
