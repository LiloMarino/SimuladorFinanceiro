import { CartesianGrid, ComposedChart, Line, ReferenceArea, ReferenceDot, ReferenceLine, XAxis, YAxis } from "recharts";
import { InfoHint } from "@/shared/components/info-hint";
import { partyColor } from "@/shared/lib/party-colors";
import type { ElectionTimeline, MapPlace, TimelinePoint } from "@/types";
import { placeTrend, runoffStart, trendParties, trendSummary, trendTick, type TrendRow } from "../lib/map-trend";
import { CHART_FONT_SIZE, CHART_TICK } from "@/shared/lib/chart-text";

const CHART_WIDTH = 300;
const CHART_HEIGHT = 150;
const TICK = { ...CHART_TICK, fontFamily: "var(--font-mono)" };
const UNDECIDED_COLOR = "var(--warning)";
/** O eixo Y sobe de 20 em 20 até cobrir o maior valor. */
const Y_STEP = 20;
const Y_MIN_TOP = 80;

type MapPlaceTrendProps = {
  timeline: ElectionTimeline;
  place: MapPlace;
  /** O ponto escolhido na régua: a linha tracejada do gráfico. */
  selected: TimelinePoint;
  /** O partido da frase de resumo. */
  focusParty: number | null;
  onSelect: (point: TimelinePoint) => void;
};

type ChartRow = { index: number; undecided: number | null } & Record<`p${number}`, number | undefined>;

function chartRows(rows: TrendRow[], partyIds: number[]): ChartRow[] {
  return rows.map((row, index) => ({
    index,
    undecided: row.undecided,
    ...Object.fromEntries(partyIds.map((id) => [`p${id}`, row.values[id]])),
  }));
}

// O losango do 1º turno no eixo X
function Diamond({ cx, cy }: { cx?: number; cy?: number }) {
  if (cx === undefined || cy === undefined) return null;
  return (
    <rect
      x={cx - 4}
      y={cy - 4}
      width={8}
      height={8}
      rx={1.5}
      transform={`rotate(45 ${cx} ${cy})`}
      fill="var(--foreground)"
    />
  );
}

/** A intenção de cada partido no lugar ao longo do ciclo, com o ponto da régua marcado; clicar num ponto leva a régua até ele. */
export function MapPlaceTrend({ timeline, place, selected, focusParty, onSelect }: MapPlaceTrendProps) {
  const rows = placeTrend(timeline.points, place.code);
  if (rows.length < 2) return null;

  const partyIds = trendParties(rows);
  const data = chartRows(rows, partyIds);
  const maxValue = Math.max(...rows.flatMap((row) => [...Object.values(row.values), row.undecided ?? 0]));
  const top = Math.max(Y_MIN_TOP, Math.ceil(maxValue / Y_STEP) * Y_STEP);
  const yTicks = Array.from({ length: top / Y_STEP + 1 }, (_, index) => index * Y_STEP);
  const xTicks = rows.map((_, index) => index).filter((index) => trendTick(rows, index) !== "");
  const runoffFrom = runoffStart(rows);
  const firstRound = rows.findIndex((row) => row.kind === "FIRST_ROUND");
  const selectedIndex = rows.findIndex((row) => row.date === selected.date);
  const last = rows.at(-1)!;
  const lastIndex = rows.length - 1;

  const summaryParty = timeline.parties.find((party) => party.id === (focusParty ?? partyIds[0]));
  const summary = summaryParty ? trendSummary(rows, summaryParty.id, summaryParty.abbr, place.name) : null;

  const pick = (state: { activeTooltipIndex?: number | string | null | undefined }) => {
    const row = rows[Number(state.activeTooltipIndex)];
    const point = row && timeline.points.find((item) => item.date === row.date);
    if (point) onSelect(point);
  };

  return (
    <div className="grid gap-2">
      <div className="flex items-center justify-between gap-2 text-[13px]">
        <span className="inline-flex items-center gap-1 font-semibold">
          {place.name} ao longo da campanha
          <InfoHint label="Como ler o gráfico">
            Cada linha é a intenção de voto de um partido neste lugar, uma medida por ponto da régua. Se o PTD está em
            40% numa pesquisa, 40 de cada 100 eleitores do lugar disseram que votariam nele. A faixa sombreada é o 2º
            turno, e o número na ponta é o último valor.
          </InfoHint>
        </span>
        <span className="text-xs text-muted-foreground">clique num ponto</span>
      </div>

      <ComposedChart
        width={CHART_WIDTH}
        height={CHART_HEIGHT}
        data={data}
        margin={{ top: 10, right: 34, left: 0, bottom: 0 }}
        onClick={pick}
        style={{ cursor: "pointer" }}
      >
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="index"
          type="number"
          domain={[0, lastIndex]}
          ticks={xTicks}
          tickFormatter={(index: number) => trendTick(rows, index)}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis domain={[0, top]} ticks={yTicks} tick={TICK} axisLine={false} tickLine={false} width={28} />
        {runoffFrom !== null && <ReferenceArea x1={runoffFrom} x2={lastIndex} fill="var(--muted)" fillOpacity={0.7} />}
        {firstRound !== -1 && <ReferenceDot x={firstRound} y={0} r={0} shape={<Diamond />} />}
        {selectedIndex !== -1 && (
          <ReferenceLine x={selectedIndex} stroke="var(--primary)" strokeDasharray="4 3" strokeWidth={1.5} />
        )}
        <Line
          dataKey="undecided"
          type="linear"
          stroke={UNDECIDED_COLOR}
          strokeWidth={1.5}
          strokeDasharray="3 3"
          dot={false}
          activeDot={false}
          isAnimationActive={false}
        />
        {partyIds.map((id) => {
          const party = timeline.parties.find((item) => item.id === id);
          const color = party ? partyColor(party) : "var(--faint-foreground)";
          return (
            <Line
              key={id}
              dataKey={`p${id}`}
              type="linear"
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 3 }}
              isAnimationActive={false}
              connectNulls={false}
            />
          );
        })}
        {partyIds.map((id) => {
          const party = timeline.parties.find((item) => item.id === id);
          const finalValue = last.values[id];
          if (finalValue === undefined) return null;
          return (
            <ReferenceDot
              key={id}
              x={lastIndex}
              y={finalValue}
              r={0}
              label={{
                value: `${Math.round(finalValue)}%`,
                position: "right",
                fontSize: CHART_FONT_SIZE,
                fontWeight: 700,
                fill: party ? partyColor(party) : "var(--foreground)",
              }}
            />
          );
        })}
      </ComposedChart>

      {summary && (
        <p className="text-xs text-muted-foreground">{summary} A linha tracejada é o ponto escolhido na régua.</p>
      )}
    </div>
  );
}
