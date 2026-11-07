import { useId, useState, type KeyboardEvent, type ReactNode } from "react";
import { cn } from "@/shared/lib/utils";
import type { MapPlace } from "@/types";
import {
  MAP_VIEW_BOX,
  REGION_LABELS,
  REGION_PATHS,
  REGION_SHORT_NAMES,
  STATE_LABELS,
  STATE_PATHS,
  type BrazilRegionCode,
  type BrazilStateCode,
} from "../lib/brazil-geometry";
import type { MapDivision } from "../lib/map-lenses";

/** Como o lugar é pintado: cor cheia, listras de duas cores (empate técnico) ou sem dado. */
export type MapFill =
  | { kind: "solid"; color: string; text: string }
  | { kind: "stripes"; colors: [string, string]; text: string }
  | { kind: "empty" };

type BrazilMapProps = {
  division: MapDivision;
  /** Os lugares da divisão na ordem do Tab: do maior eleitorado ao menor. */
  places: Pick<MapPlace, "code" | "name">[];
  fills: Record<string, MapFill>;
  /** A largura em pixels; a altura segue a proporção do contorno. */
  width: number;
  selected?: string | null;
  onSelect?: (code: string) => void;
  /** O conteúdo da dica de um lugar; sem ele o mapa não mostra dica. */
  tip?: (code: string) => ReactNode;
  /** Sem interação o mapa é só desenho: sem foco, hover nem clique. */
  interactive?: boolean;
  className?: string;
};

const LABEL_FONT_PX = 12;
const STRIPE_STEP = 7;
// Os estados só levam sigla a partir desta largura; abaixo dela o mapa fica sem rótulo
const STATE_LABEL_MIN_WIDTH = 330;
const REGION_LABEL_MIN_WIDTH = 250;

type Anchor = { x: number; y: number };

export function BrazilMap({
  division,
  places,
  fills,
  width,
  selected = null,
  onSelect,
  tip,
  interactive = true,
  className,
}: BrazilMapProps) {
  const uid = useId();
  const [hovered, setHovered] = useState<string | null>(null);
  const [focused, setFocused] = useState<string | null>(null);
  const [anchor, setAnchor] = useState<Anchor | null>(null);
  const scale = width / MAP_VIEW_BOX.width;
  const height = Math.round(MAP_VIEW_BOX.height * scale);
  const paths: Record<string, string> = division === "state" ? STATE_PATHS : REGION_PATHS;
  const shown = hovered ?? focused;
  const flipped = anchor !== null && anchor.x > width * 0.6;
  const showLabels = width >= (division === "state" ? STATE_LABEL_MIN_WIDTH : REGION_LABEL_MIN_WIDTH);

  const fillOf = (code: string) => {
    const fill = fills[code];
    if (!fill || fill.kind === "empty") return "var(--muted)";
    if (fill.kind === "solid") return fill.color;
    return `url(#${uid}-${code})`;
  };

  const select = (code: string) => onSelect?.(code);
  const onKey = (event: KeyboardEvent<SVGPathElement>, code: string) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      select(code);
    }
  };

  return (
    <div className={cn("relative", className)} style={{ width, height }}>
      <svg
        viewBox={`0 0 ${MAP_VIEW_BOX.width} ${MAP_VIEW_BOX.height}`}
        width={width}
        height={height}
        role={interactive ? "group" : "img"}
        aria-label={division === "state" ? "Mapa do Brasil por estado" : "Mapa do Brasil por região"}
      >
        {/* Listras dos empates técnicos */}
        <defs>
          {places.map((place) => {
            const fill = fills[place.code];
            if (fill?.kind !== "stripes") return null;
            return (
              <pattern
                key={place.code}
                id={`${uid}-${place.code}`}
                patternUnits="userSpaceOnUse"
                width={STRIPE_STEP}
                height={STRIPE_STEP}
                patternTransform="rotate(45)"
              >
                <rect width={STRIPE_STEP} height={STRIPE_STEP} fill={fill.colors[0]} />
                <rect width={STRIPE_STEP / 2} height={STRIPE_STEP} fill={fill.colors[1]} />
              </pattern>
            );
          })}
        </defs>

        {/* Lugares */}
        {places.map((place) => {
          const d = paths[place.code];
          if (!d) return null;
          return (
            <path
              key={place.code}
              d={d}
              fill={fillOf(place.code)}
              style={{ stroke: "var(--card)", strokeWidth: 1 }}
              vectorEffect="non-scaling-stroke"
              className={cn("outline-none", interactive && "cursor-pointer hover:brightness-95")}
              {...(interactive
                ? {
                    tabIndex: 0,
                    role: "button",
                    "aria-label": place.name,
                    "aria-pressed": selected === place.code,
                    onClick: () => select(place.code),
                    onKeyDown: (event: KeyboardEvent<SVGPathElement>) => onKey(event, place.code),
                    onMouseEnter: () => setHovered(place.code),
                    onMouseMove: (event: React.MouseEvent<SVGPathElement>) => {
                      const box = event.currentTarget.ownerSVGElement?.getBoundingClientRect();
                      if (box) setAnchor({ x: event.clientX - box.left, y: event.clientY - box.top });
                    },
                    onMouseLeave: () => setHovered(null),
                    onFocus: (event: React.FocusEvent<SVGPathElement>) => {
                      setFocused(place.code);
                      const bounds = event.currentTarget.getBBox();
                      setAnchor({ x: (bounds.x + bounds.width / 2) * scale, y: bounds.y * scale });
                    },
                    onBlur: () => setFocused(null),
                  }
                : { "aria-hidden": true })}
            />
          );
        })}

        {/* Halo do lugar selecionado e do que tem o foco */}
        {[selected, focused !== selected ? focused : null].map((code, index) =>
          code && paths[code] ? (
            <path
              key={`${index}-${code}`}
              d={paths[code]}
              fill="none"
              vectorEffect="non-scaling-stroke"
              pointerEvents="none"
              style={{ stroke: "var(--foreground)", strokeWidth: index === 0 ? 2.5 : 2 }}
            />
          ) : null,
        )}

        {/* Rótulos */}
        {showLabels
          ? places.map((place) => {
              const point =
                division === "state"
                  ? STATE_LABELS[place.code as BrazilStateCode]
                  : REGION_LABELS[place.code as BrazilRegionCode];
              if (!point) return null;
              const fill = fills[place.code];
              const text = division === "state" ? place.code : REGION_SHORT_NAMES[place.code as BrazilRegionCode];
              return (
                <text
                  key={place.code}
                  x={point.x}
                  y={point.y}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize={LABEL_FONT_PX / scale}
                  fontWeight={600}
                  pointerEvents="none"
                  style={{ fill: fill && fill.kind !== "empty" ? fill.text : "var(--muted-foreground)" }}
                >
                  {text}
                </text>
              );
            })
          : null}
      </svg>

      {/* Dica do lugar */}
      {tip && shown && anchor ? (
        <div
          role="tooltip"
          className="pointer-events-none absolute z-10 w-max max-w-64 rounded-md bg-foreground px-3 py-2 text-xs text-background shadow-md"
          style={{
            left: flipped ? anchor.x - 12 : anchor.x + 12,
            top: anchor.y + 12,
            transform: flipped ? "translateX(-100%)" : undefined,
          }}
        >
          {tip(shown)}
        </div>
      ) : null}
    </div>
  );
}
