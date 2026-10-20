import { Area, AreaChart, CartesianGrid, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { LineChart as LineChartIcon } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import {
  displayDate,
  displayMoney,
  displayMoneyCompact,
  displayMonthSlashYear,
  displayNumber,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import { goalAt } from "@/shared/lib/goal";
import type { PortfolioHistoryPoint, SeriesPoint } from "@/types";

// Da base para o topo da pilha: caixa, renda fixa, renda variável
const BANDS = [
  { key: "cash", label: "Caixa", color: "var(--input)" },
  { key: "fixed", label: "Renda fixa", color: "var(--chart-2)" },
  { key: "equity", label: "Renda variável", color: "var(--chart-1)" },
] as const;

type Point = {
  date: string;
  cash: number;
  fixed: number;
  equity: number;
  total: number;
  provided: number;
  /** Meta vigente no dia: reta na corrida, em degraus no viver de renda; ausente fora da corrida */
  goal?: number;
};

// A altura do gráfico e a do eixo X são fixas: com elas, os rótulos do fim ficam na posição exata
const CHART_HEIGHT = 300;
const CHART_MARGIN = { top: 8, right: 112, left: 0, bottom: 0 };
const X_AXIS_HEIGHT = 24;
const PLOT_HEIGHT = CHART_HEIGHT - CHART_MARGIN.top - X_AXIS_HEIGHT;
const LABEL_SPACING = 16;

/** Eixo Y em múltiplos redondos, com no máximo 5 divisões acima de zero. */
function niceScale(max: number) {
  if (max <= 0) return { ticks: [0, 1], top: 1 };
  const base = 10 ** Math.floor(Math.log10(max / 4));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * base).find((s) => max / s <= 5) ?? 10 * base;
  const count = Math.ceil(max / step);
  return { ticks: Array.from({ length: count + 1 }, (_, i) => i * step), top: count * step };
}

const displayThousands = (value: number) => {
  if (value === 0) return "0";
  return value >= 1_000_000
    ? `${displayNumber(value / 1_000_000, 1)} mi`
    : `${displayNumber(value / 1_000, value % 1_000 === 0 ? 0 : 1)} mil`;
};

/** Evolução da carteira: uma faixa por classe e, por cima, a linha tracejada do que foi aportado. */
export function NetworthChart({ history, goalSteps }: { history: PortfolioHistoryPoint[]; goalSteps?: SeriesPoint[] }) {
  // Recharts desenha número; os valores seguem em string até aqui
  const data: Point[] = history.map((p) => ({
    date: p.snapshot_date,
    cash: Number(p.total_cash),
    fixed: Number(p.total_fixed),
    equity: Number(p.total_equity),
    total: Number(p.total_networth),
    provided: Number(p.total_provided),
    goal: goalAt(goalSteps ?? [], p.snapshot_date),
  }));
  const last = data.at(-1);
  const hasGoal = data.some((p) => p.goal !== undefined);
  const scale = niceScale(Math.max(0, ...data.map((p) => Math.max(p.total, p.provided, p.goal ?? 0))));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evolução do patrimônio</CardTitle>
        <CardDescription>
          Cada faixa é uma classe; a tracejada é o que você aportou. O topo acima dela é ganho.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {data.length < 2 || !last ? (
          <Empty variant="dashed">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <LineChartIcon />
              </EmptyMedia>
              <EmptyTitle>O gráfico começa no próximo pregão</EmptyTitle>
              <EmptyDescription>Cada dia simulado vira um ponto aqui.</EmptyDescription>
            </EmptyHeader>
          </Empty>
        ) : (
          <div className="grid gap-3">
            <div className="relative">
              <ResponsiveContainer width="100%" height={CHART_HEIGHT}>
                <AreaChart data={data} margin={CHART_MARGIN}>
                  <CartesianGrid vertical={false} stroke="var(--border)" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(d: string) => displayMonthSlashYear(d)}
                    tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
                    axisLine={false}
                    tickLine={false}
                    minTickGap={48}
                    height={X_AXIS_HEIGHT}
                  />
                  <YAxis
                    ticks={scale.ticks}
                    domain={[0, scale.top]}
                    tickFormatter={displayThousands}
                    tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
                    axisLine={false}
                    tickLine={false}
                    width={56}
                  />
                  <Tooltip
                    cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
                    content={<NetworthTooltip />}
                  />
                  {BANDS.map((band) => (
                    <Area
                      key={band.key}
                      type="monotone"
                      stackId="networth"
                      dataKey={band.key}
                      stroke="var(--card)"
                      strokeWidth={1}
                      fill={band.color}
                      fillOpacity={0.9}
                      isAnimationActive={false}
                    />
                  ))}
                  <Line
                    type="linear"
                    dataKey="provided"
                    stroke="var(--foreground)"
                    strokeWidth={1.6}
                    strokeDasharray="6 4"
                    dot={false}
                    isAnimationActive={false}
                  />
                  {hasGoal && (
                    <Line
                      type="stepAfter"
                      dataKey="goal"
                      stroke="var(--foreground)"
                      strokeWidth={2}
                      strokeDasharray="2 4"
                      strokeLinecap="round"
                      dot={false}
                      isAnimationActive={false}
                    />
                  )}
                </AreaChart>
              </ResponsiveContainer>
              <EndLabels last={last} top={scale.top} />
            </div>

            {/* Legenda */}
            <ul className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
              {[...BANDS].reverse().map((band) => (
                <li key={band.key} className="flex items-center gap-1.5">
                  <span className="size-2.5 rounded-sm" style={{ backgroundColor: band.color }} aria-hidden="true" />
                  {band.label}
                </li>
              ))}
              <li className="flex items-center gap-1.5">
                <span className="w-4 border-t-2 border-dashed border-foreground" aria-hidden="true" />
                Aportado
              </li>
              {hasGoal && (
                <li className="flex items-center gap-1.5">
                  <span className="w-4 border-t-2 border-dotted border-foreground" aria-hidden="true" />
                  Meta
                </li>
              )}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/** Nome e valor de cada faixa na ponta direita, sem se sobrepor. */
function EndLabels({ last, top }: { last: Point; top: number }) {
  const yOf = (value: number) => CHART_MARGIN.top + (1 - value / top) * PLOT_HEIGHT;

  const items = [
    { key: "total", y: yOf(last.total), name: "Patrimônio", value: last.total, strong: true },
    { key: "provided", y: yOf(last.provided), name: "aportado", value: last.provided, strong: false },
    ...(last.goal !== undefined
      ? [{ key: "goal", y: yOf(last.goal), name: "Meta", value: last.goal, strong: false }]
      : []),
    ...BANDS.map((band, i) => {
      const below = BANDS.slice(0, i).reduce((sum, b) => sum + last[b.key], 0);
      return {
        key: band.key,
        y: yOf(below + last[band.key] / 2),
        name: band.label,
        value: null,
        strong: false,
        // Faixa fina demais não comporta o nome
        visible: (last[band.key] / top) * PLOT_HEIGHT >= LABEL_SPACING,
        color: band.key === "fixed" ? "text-chart-2" : band.key === "equity" ? "text-chart-1" : "text-faint-foreground",
      };
    }),
  ].filter((item) => !("visible" in item) || item.visible);

  // Do topo para baixo, empurrando para baixo o rótulo que colide com o de cima;
  // o rótulo com valor ocupa duas linhas e pede o dobro de espaço
  const heightOf = (item: (typeof items)[number]) => (item.value !== null ? 2 * LABEL_SPACING : LABEL_SPACING);
  const placed = items
    .sort((a, b) => a.y - b.y)
    .reduce<((typeof items)[number] & { top: number })[]>((acc, item) => {
      const previous = acc.at(-1);
      const minimum = previous ? previous.top + (heightOf(previous) + heightOf(item)) / 2 : item.y;
      return [...acc, { ...item, top: Math.max(item.y, minimum) }];
    }, []);

  return (
    <div className="pointer-events-none absolute inset-y-0 right-0 w-28 text-[11px]" aria-hidden="true">
      {placed.map((item) => (
        <div
          key={item.key}
          className={`absolute left-2 -translate-y-1/2 leading-tight whitespace-nowrap ${"color" in item ? item.color : "text-foreground"}`}
          style={{ top: item.top }}
        >
          <span className={item.strong ? "font-semibold" : undefined}>
            {item.key === "provided" ? "┄ " : item.key === "goal" ? "··· " : ""}
            {item.name}
          </span>
          {item.value !== null && (
            <span className="block font-mono text-muted-foreground">{displayMoneyCompact(item.value)}</span>
          )}
        </div>
      ))}
    </div>
  );
}

type TooltipProps = { active?: boolean; payload?: { payload: Point }[] };

function NetworthTooltip({ active, payload }: TooltipProps) {
  const point = payload?.[0]?.payload;
  if (!active || !point) return null;

  const gain = point.total - point.provided;
  const positive = gain >= 0;

  return (
    <div className="grid min-w-52 gap-1.5 rounded-[10px] border border-border bg-popover p-3 text-xs shadow-md">
      <span className="font-mono text-muted-foreground">{displayDate(parseLocalDate(point.date))}</span>
      <div className="flex items-center justify-between gap-4 text-[13px] font-bold">
        <span>Patrimônio</span>
        <span className="font-mono">{displayMoney(point.total)}</span>
      </div>
      {[...BANDS].reverse().map((band) => (
        <div key={band.key} className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-1.5">
            <span className="size-2 rounded-sm" style={{ backgroundColor: band.color }} aria-hidden="true" />
            {band.label}
          </span>
          <span className="font-mono">{displayMoney(point[band.key])}</span>
        </div>
      ))}
      <div className="flex items-center justify-between gap-4 border-t border-border pt-1.5 text-muted-foreground">
        <span>┄ Aportado</span>
        <span className="font-mono">{displayMoney(point.provided)}</span>
      </div>
      <span className={positive ? "font-mono text-success" : "font-mono text-destructive"}>
        {positive ? "+" : "-"}
        {displayMoney(Math.abs(gain))} {positive ? "acima" : "abaixo"} do aportado
      </span>
      {point.goal !== undefined && (
        <div className="flex items-center justify-between gap-4 text-muted-foreground">
          <span>··· Falta para a meta</span>
          <span className="font-mono">{displayMoney(Math.max(0, point.goal - point.total))}</span>
        </div>
      )}
    </div>
  );
}
