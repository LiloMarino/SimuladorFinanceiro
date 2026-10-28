import { useMemo, useState, type PointerEvent } from "react";
import { niceScale } from "@/shared/lib/chart-scale";
import { displayIsoDate, displayMoney, displayShortMonthYear } from "@/shared/lib/utils/display";
import {
  axisTicks,
  displaySignedThousands,
  displayThousands,
  type AxisTick,
  type NetworthPoint,
} from "../lib/networth-model";

const PANEL_HEIGHT = 74;
const AXIS_HEIGHT = 18;
const LEFT = 54;
const RIGHT = 8;
const TOP = 6;
const BOTTOM = 4;

const CLASSES = [
  {
    key: "equity",
    label: "Renda variável",
    color: "var(--chart-1)",
    lineClass: "stroke-chart-1",
    areaClass: "fill-chart-1/12",
    dotClass: "stroke-chart-1",
  },
  {
    key: "fixed",
    label: "Renda fixa",
    color: "var(--chart-2)",
    lineClass: "stroke-chart-2",
    areaClass: "fill-chart-2/12",
    dotClass: "stroke-chart-2",
  },
  {
    key: "cash",
    label: "Caixa",
    color: "var(--faint-foreground)",
    lineClass: "stroke-faint-foreground",
    areaClass: "fill-faint-foreground/12",
    dotClass: "stroke-faint-foreground",
  },
] as const;

type ClassConfig = (typeof CLASSES)[number];

/** Um painel por classe, um embaixo do outro, cada um com a própria escala e o mesmo eixo de tempo. */
export function NetworthClassPanels({ points, width }: { points: NetworthPoint[]; width: number }) {
  const [hover, setHover] = useState<number | null>(null);
  const plotWidth = width - LEFT - RIGHT;
  const xTicks = useMemo(
    () =>
      axisTicks(
        points.map((p) => p.date),
        plotWidth,
      ),
    [points, plotWidth],
  );

  return (
    <div className="grid gap-3.5">
      {CLASSES.map((config, i) => (
        <ClassPanel
          key={config.key}
          config={config}
          points={points}
          width={width}
          hover={hover}
          onHover={setHover}
          xTicks={i === CLASSES.length - 1 ? xTicks : undefined}
        />
      ))}
      <span className="text-xs text-muted-foreground">
        Cada painel tem a própria escala: compare o formato das curvas, não a altura entre painéis.
      </span>
    </div>
  );
}

function ClassPanel({
  config,
  points,
  width,
  hover,
  onHover,
  xTicks,
}: {
  config: ClassConfig;
  points: NetworthPoint[];
  width: number;
  hover: number | null;
  onHover: (index: number | null) => void;
  /** Só o último painel desenha o eixo de tempo */
  xTicks: AxisTick[] | undefined;
}) {
  const values = useMemo(() => points.map((p) => p[config.key]), [points, config.key]);
  const plotWidth = width - LEFT - RIGHT;
  const plotHeight = PANEL_HEIGHT - TOP - BOTTOM;
  const height = PANEL_HEIGHT + (xTicks ? AXIS_HEIGHT : 0);

  const shape = useMemo(() => {
    const low = Math.min(...values);
    const high = Math.max(...values);
    const { floor, ceiling } = low === 0 && high === 0 ? { floor: 0, ceiling: 1000 } : niceScale(low, high);
    const xOf = (index: number) => LEFT + (values.length > 1 ? (index / (values.length - 1)) * plotWidth : 0);
    const yOf = (value: number) => TOP + ((ceiling - value) / (ceiling - floor || 1)) * plotHeight;
    const coords = values.map((v, i) => ({ x: xOf(i), y: yOf(v) }));
    const line = coords.map((c, i) => `${i === 0 ? "M" : "L"}${c.x.toFixed(1)} ${c.y.toFixed(1)}`).join(" ");
    const base = TOP + plotHeight;
    const last = coords.at(-1);
    const first = coords[0];
    const area = first && last ? `${line} L${last.x.toFixed(1)} ${base} L${first.x.toFixed(1)} ${base} Z` : "";
    return { floor, ceiling, xOf, yOf, line, area };
  }, [values, plotWidth, plotHeight]);

  const shownIndex = hover ?? values.length - 1;
  const shown = points[shownIndex];
  const start = points[0];
  const shownValue = values[shownIndex] ?? 0;
  const change = shownValue - (values[0] ?? 0);

  const onMove = (event: PointerEvent<SVGRectElement>) => {
    const box = event.currentTarget.getBoundingClientRect();
    const ratio = (event.clientX - box.left) / box.width;
    onHover(Math.max(0, Math.min(points.length - 1, Math.round(ratio * (points.length - 1)))));
  };

  return (
    <div className="grid gap-1">
      <div className="flex items-baseline justify-between gap-2 text-xs">
        <span className="flex items-center gap-1.5 text-[13px] font-semibold">
          <span className="size-2.25 rounded-xs" style={{ backgroundColor: config.color }} aria-hidden="true" />
          {config.label}
        </span>
        <span className="flex flex-wrap items-baseline justify-end gap-x-1.5">
          <span className="font-mono text-[13px] font-semibold">{displayMoney(shownValue)}</span>
          <span className="text-muted-foreground">
            · {hover === null || !shown ? "hoje" : displayIsoDate(shown.date)}
          </span>
          {start && (
            <span className={`font-mono ${change < 0 ? "text-destructive" : "text-success"}`}>
              {displaySignedThousands(change)} desde {displayShortMonthYear(start.date)}
            </span>
          )}
        </span>
      </div>

      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="block font-sans text-[11px]"
        role="img"
        aria-label={`${config.label} ao longo da partida`}
      >
        {[shape.ceiling, shape.floor].map((tick) => (
          <g key={tick}>
            <line x1={LEFT} x2={width - RIGHT} y1={shape.yOf(tick)} y2={shape.yOf(tick)} className="stroke-border" />
            <text x={LEFT - 8} y={shape.yOf(tick) + 4} textAnchor="end" className="fill-faint-foreground">
              {displayThousands(tick)}
            </text>
          </g>
        ))}
        <path d={shape.area} className={config.areaClass} />
        <path d={shape.line} fill="none" className={config.lineClass} strokeWidth={2} strokeLinejoin="round" />

        {xTicks?.map((tick) => (
          <text
            key={tick.index}
            x={shape.xOf(tick.index)}
            y={PANEL_HEIGHT + 10}
            textAnchor={tick.anchor}
            className="fill-faint-foreground"
          >
            {tick.label}
          </text>
        ))}

        {hover !== null && (
          <g pointerEvents="none">
            <line
              x1={shape.xOf(hover)}
              x2={shape.xOf(hover)}
              y1={0}
              y2={TOP + plotHeight}
              className="stroke-foreground/35"
            />
            <circle
              cx={shape.xOf(hover)}
              cy={shape.yOf(shownValue)}
              r={4}
              className={`fill-card ${config.dotClass}`}
              strokeWidth={2}
            />
          </g>
        )}

        <rect
          x={LEFT}
          y={0}
          width={plotWidth}
          height={TOP + plotHeight}
          fill="transparent"
          onPointerMove={onMove}
          onPointerLeave={() => onHover(null)}
        />
      </svg>
    </div>
  );
}
