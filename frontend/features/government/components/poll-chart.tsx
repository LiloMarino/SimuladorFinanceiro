import { Area, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { displayDate, displayShortMonthYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";
import { marginRange } from "../lib/voters";
import { partyColor } from "@/shared/lib/party-colors";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };
const UNDECIDED_KEY = "undecided";
const UNDECIDED_COLOR = "var(--faint-foreground)";

type PollRow = { time: number; margin: number } & Record<string, number | [number, number]>;

const partyKey = (partyId: number) => `party-${partyId}`;
const bandKey = (partyId: number) => `band-${partyId}`;
const numberFormat = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });

/** Uma linha por pesquisa publicada, com a faixa da margem de cada partido. */
function pollRows(panel: ElectionPanel): PollRow[] {
  return panel.polls.map((poll) => {
    const row: PollRow = {
      time: parseLocalDate(poll.date).getTime(),
      margin: poll.margin,
      [UNDECIDED_KEY]: Number(poll.undecided),
    };
    for (const entry of poll.entries) {
      const points = Number(entry.points);
      row[partyKey(entry.party_id)] = points;
      row[bandKey(entry.party_id)] = marginRange(points, poll.margin);
    }
    return row;
  });
}

type PollChartProps = { panel: ElectionPanel; height?: number };

/** As linhas de intenção de voto desde a abertura da campanha; a faixa clara em volta é a margem de erro. */
export function PollChart({ panel, height = 220 }: PollChartProps) {
  const rows = pollRows(panel);
  const names = new Map(panel.parties.map((party) => [partyKey(party.id), party.abbr]));
  names.set(UNDECIDED_KEY, "Indecisos");

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={["dataMin", "dataMax"]}
          tickFormatter={(time: number) => displayShortMonthYear(new Date(time))}
          tick={TICK}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          domain={[0, 100]}
          ticks={[0, 25, 50, 75, 100]}
          tickFormatter={(value: number) => `${value}`}
          tick={TICK}
          axisLine={false}
          tickLine={false}
          width={32}
        />
        <Tooltip
          cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
          content={({ active, payload }) => {
            const row = payload[0]?.payload as PollRow | undefined;
            if (!active || !row) return null;
            return (
              <div className="grid gap-1 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                <span className="text-muted-foreground">
                  {displayDate(new Date(row.time))}
                  {row.margin > 0 && ` · margem de ${row.margin} pontos`}
                </span>
                {payload
                  .filter((item) => names.has(String(item.dataKey)))
                  .map((item) => (
                    <span key={String(item.dataKey)} className="flex items-center justify-between gap-4">
                      <span className="flex items-center gap-1.5">
                        <span className="size-2 rounded-full" style={{ backgroundColor: item.color }} />
                        {names.get(String(item.dataKey))}
                      </span>
                      <span className="font-mono font-semibold">{numberFormat.format(Number(item.value))}</span>
                    </span>
                  ))}
              </div>
            );
          }}
        />
        {panel.parties.map((party) => (
          <Area
            key={`band-${party.id}`}
            dataKey={bandKey(party.id)}
            type="linear"
            fill={partyColor(party)}
            fillOpacity={0.12}
            stroke="none"
            activeDot={false}
            isAnimationActive={false}
          />
        ))}
        {panel.parties.map((party) => (
          <Line
            key={party.id}
            dataKey={partyKey(party.id)}
            type="linear"
            stroke={partyColor(party)}
            strokeWidth={2}
            strokeDasharray={party.is_computer ? "5 4" : "none"}
            dot={false}
            connectNulls
            isAnimationActive={false}
          />
        ))}
        <Line
          dataKey={UNDECIDED_KEY}
          type="linear"
          stroke={UNDECIDED_COLOR}
          strokeWidth={1.5}
          strokeDasharray="2 3"
          dot={false}
          isAnimationActive={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
