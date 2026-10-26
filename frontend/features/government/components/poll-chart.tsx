import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { displayDate, displayShortMonthYear, parseLocalDate } from "@/shared/lib/utils/display";
import type { ElectionPanel } from "@/types";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };
const UNDECIDED_KEY = "undecided";
const UNDECIDED_COLOR = "var(--faint-foreground)";

type PollRow = { time: number } & Record<string, number>;

const partyKey = (partyId: number) => `party-${partyId}`;
const numberFormat = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });

/** Uma linha por pesquisa e, no fim, a intenção de hoje; indecisos é o que falta para 100. */
function pollRows(panel: ElectionPanel): PollRow[] {
  const rows: PollRow[] = panel.polls.map((poll) => {
    const row: PollRow = { time: parseLocalDate(poll.date).getTime(), [UNDECIDED_KEY]: 100 };
    for (const entry of poll.entries) {
      const points = Number(entry.points);
      row[partyKey(entry.party_id)] = points;
      row[UNDECIDED_KEY] = (row[UNDECIDED_KEY] ?? 0) - points;
    }
    return row;
  });

  const today = parseLocalDate(panel.today).getTime();
  const lastRow = rows.at(-1);
  if (!lastRow || lastRow.time < today) {
    const row: PollRow = { time: today, [UNDECIDED_KEY]: Number(panel.undecided) };
    for (const party of panel.parties) row[partyKey(party.id)] = Number(party.intention_points);
    rows.push(row);
  }
  return rows;
}

type PollChartProps = { panel: ElectionPanel; height?: number };

/** As linhas de intenção de voto ao longo da campanha; o computador e os indecisos vão tracejados. */
export function PollChart({ panel, height = 220 }: PollChartProps) {
  const rows = pollRows(panel);
  const names = new Map(panel.parties.map((party) => [partyKey(party.id), party.abbr]));
  names.set(UNDECIDED_KEY, "Indecisos");

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
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
            const row = payload?.[0]?.payload as PollRow | undefined;
            if (!active || !row) return null;
            return (
              <div className="grid gap-1 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                <span className="text-muted-foreground">{displayDate(new Date(row.time))}</span>
                {payload.map((item) => (
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
          <Line
            key={party.id}
            dataKey={partyKey(party.id)}
            type="linear"
            stroke={party.color ?? "var(--muted-foreground)"}
            strokeWidth={2}
            strokeDasharray={party.is_computer ? "5 4" : undefined}
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
      </LineChart>
    </ResponsiveContainer>
  );
}
