import type { VoterValue } from "@/types";
import { VALUE_INFO, VOTER_VALUES } from "@/shared/lib/party-flags";

type RadarSeries = {
  key: string;
  /** De 0 a 100 em cada valor */
  scores: Record<VoterValue, number>;
  color: string;
  /** Tracejada e quase sem preenchimento: a referência (a fundação, ou o que o grupo quer) */
  dashed?: boolean;
};

const RINGS = [0.25, 0.5, 0.75, 1];
const LABEL_GAP = 18;

type ProfileRadarProps = {
  series: RadarSeries[];
  width: number;
  height: number;
  label: string;
};

/** O perfil em seis eixos, um por valor, de 0 no centro a 100 na ponta; a última série fica por cima. */
export function ProfileRadar({ series, width, height, label }: ProfileRadarProps) {
  const radius = height * 0.4;
  const cx = width / 2;
  const cy = height / 2;
  const angle = (index: number) => -Math.PI / 2 + (index * 2 * Math.PI) / VOTER_VALUES.length;
  const point = (index: number, fraction: number): [number, number] => [
    cx + Math.cos(angle(index)) * radius * fraction,
    cy + Math.sin(angle(index)) * radius * fraction,
  ];
  const polygon = (fraction: (value: VoterValue) => number) =>
    VOTER_VALUES.map((value, index) =>
      point(index, fraction(value))
        .map((n) => n.toFixed(1))
        .join(","),
    ).join(" ");

  return (
    <svg
      role="img"
      aria-label={label}
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
      className="block max-w-full overflow-visible"
    >
      {/* Grade */}
      {RINGS.map((ring) => (
        <polygon key={ring} points={polygon(() => ring)} fill="none" className="stroke-border" />
      ))}
      {VOTER_VALUES.map((value, index) => {
        const [x, y] = point(index, 1);
        return <line key={value} x1={cx} y1={cy} x2={x} y2={y} className="stroke-border" />;
      })}

      {/* Séries */}
      {series.map((item) => (
        <g key={item.key}>
          <polygon
            points={polygon((value) => item.scores[value] / 100)}
            fill={item.color}
            fillOpacity={item.dashed ? 0.06 : 0.16}
            stroke={item.color}
            strokeWidth={2}
            strokeDasharray={item.dashed ? "4 3" : undefined}
            strokeLinejoin="round"
          />
          {!item.dashed &&
            VOTER_VALUES.map((value, index) => {
              const [x, y] = point(index, item.scores[value] / 100);
              return <circle key={value} cx={x} cy={y} r={2.5} fill={item.color} />;
            })}
        </g>
      ))}

      {/* Eixos */}
      {VOTER_VALUES.map((value, index) => {
        const [x, y] = point(index, 1);
        const dx = Math.cos(angle(index));
        const dy = Math.sin(angle(index));
        const anchor = Math.abs(dx) < 0.1 ? "middle" : dx > 0 ? "start" : "end";
        return (
          <text
            key={value}
            x={x + dx * LABEL_GAP * 0.7}
            y={y + dy * LABEL_GAP + 4}
            fontSize={11}
            fontWeight={500}
            textAnchor={anchor}
            fill={VALUE_INFO[value].color}
          >
            {VALUE_INFO[value].short}
          </text>
        );
      })}
    </svg>
  );
}
