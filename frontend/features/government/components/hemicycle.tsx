import { cn } from "@/shared/lib/utils";
import type { HemicycleSeat } from "../lib/house";

type HemicycleProps = {
  seats: HemicycleSeat[];
  /** Cadeiras, da esquerda para a direita, onde cada linha vertical de maioria cruza o hemiciclo */
  marks?: { at: number; label: string }[];
  width?: number;
  label: string;
};

const ROWS = [11, 15, 20, 25, 30];
const GEOMETRY = { cx: 210, cy: 215, inner: 90, outer: 195 };

/** As posições de cada cadeira: fileiras concêntricas, ordenadas do lado esquerdo ao direito para cada partido formar uma cunha. */
function layout(total: number) {
  const scale = total / ROWS.reduce((sum, count) => sum + count, 0);
  const counts = ROWS.map((count) => Math.max(1, Math.round(count * scale)));
  counts[counts.length - 1] = Math.max(1, counts[counts.length - 1]! + total - counts.reduce((s, c) => s + c, 0));
  const step = (GEOMETRY.outer - GEOMETRY.inner) / (ROWS.length - 1);
  const spots = counts.flatMap((count, row) =>
    Array.from({ length: count }, (_, index) => {
      const angle = Math.PI - (Math.PI * index) / Math.max(1, count - 1);
      const radius = GEOMETRY.inner + step * row;
      return { angle, x: GEOMETRY.cx + radius * Math.cos(angle), y: GEOMETRY.cy - radius * Math.sin(angle) };
    }),
  );
  return spots.sort((a, b) => b.angle - a.angle);
}

/** O plenário em semicírculo: uma bolinha por cadeira, com cunhas por partido ou cheia/clara por voto. */
export function Hemicycle({ seats, marks = [], width = 420, label }: HemicycleProps) {
  const spots = layout(seats.length);
  const size = (GEOMETRY.outer - GEOMETRY.inner) / (ROWS.length - 1) / 2 - 1.2;

  return (
    <svg
      role="img"
      aria-label={label}
      viewBox="0 0 420 240"
      width={width}
      className="block max-w-full"
      style={{ height: "auto" }}
    >
      {spots.map((spot, index) => {
        const seat = seats[index];
        if (!seat) return null;
        return (
          <g key={index}>
            <circle
              cx={spot.x}
              cy={spot.y}
              r={size}
              fill={seat.tone === "empty" ? "none" : (seat.color ?? "var(--foreground)")}
              fillOpacity={seat.tone === "light" ? 0.28 : 1}
              stroke={seat.tone === "empty" ? "var(--border)" : "none"}
              strokeWidth={1.2}
              strokeDasharray={seat.tone === "empty" ? "2 2" : undefined}
            />
            {seat.ring && (
              <circle
                cx={spot.x}
                cy={spot.y}
                r={size + 2}
                fill="none"
                stroke={seat.color ?? "var(--foreground)"}
                strokeWidth={1.2}
              />
            )}
          </g>
        );
      })}
      {marks.map((mark) => {
        const spot = spots[Math.min(mark.at, spots.length) - 1];
        if (!spot) return null;
        const dx = Math.cos(spot.angle);
        const dy = -Math.sin(spot.angle);
        const from = { x: GEOMETRY.cx + (GEOMETRY.inner - 14) * dx, y: GEOMETRY.cy + (GEOMETRY.inner - 14) * dy };
        const to = { x: GEOMETRY.cx + (GEOMETRY.outer + 10) * dx, y: GEOMETRY.cy + (GEOMETRY.outer + 10) * dy };
        return (
          <g key={mark.label} className={cn("text-muted-foreground")}>
            <line x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke="currentColor" strokeDasharray="3 3" />
            <text x={to.x} y={to.y - 4} textAnchor="middle" fontSize={10} fill="currentColor">
              {mark.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
