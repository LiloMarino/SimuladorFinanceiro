import { format } from "date-fns";
import { CartesianGrid, Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { InfoHint } from "@/shared/components/info-hint";
import { MetricHint } from "@/shared/components/metric-hint";
import { DEBT_GDP } from "@/shared/lib/budget-metrics";
import { displayDate, displayPercent } from "@/shared/lib/utils/display";
import type { TreasuryHistoryPoint } from "@/types";
import {
  closingDate,
  closingLabel,
  historyRows,
  INDEX_COLORS,
  PREMIUM_BANDS,
  pointsOf,
  type HistoryRow,
} from "../lib/treasury";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };
const AXIS_WIDTH = 48;
const MARGIN = { top: 8, right: 8, left: 0, bottom: 0 };

const BAND_FILLS = ["var(--success-soft)", "var(--info-soft)", "var(--warning-soft)", "var(--destructive-soft)"];

const timeLabel = (time: number) => closingLabel(format(new Date(time), "yyyy-MM-dd"));

type RateChartCardProps = {
  history: TreasuryHistoryPoint[];
  nextReview: string;
  withGovernment: boolean;
};

/** As taxas dos títulos a cada fechamento de mês e, com o governo, a dívida ÷ PIB sobre as faixas do prêmio. */
export function RateChartCard({ history, nextReview, withGovernment }: RateChartCardProps) {
  const rows = historyRows(history);

  return (
    <Card>
      {/* Cabeçalho */}
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-1.5">
            A taxa e a dívida
            <InfoHint label="Como ler o gráfico">
              Cada ponto é o fechamento de um mês. As linhas coloridas são as taxas dos títulos mais curtos; com o
              governo ligado, a linha de baixo mostra a dívida ÷ PIB sobre as faixas do prêmio.
            </InfoHint>
          </span>
        </CardTitle>
        <CardDescription>
          {withGovernment
            ? "Cada ponto é um fechamento de mês, em “equivale hoje”: a taxa de um ano, com o IPCA de 12 meses somado ao IPCA+."
            : "Cada ponto é um fechamento de mês, em “equivale hoje”. Sem a expansão do governo, as taxas seguem só a Selic e o IPCA."}
        </CardDescription>
      </CardHeader>

      <CardContent>
        {rows.length < 2 ? (
          <Empty>
            <EmptyHeader>
              <EmptyTitle>O gráfico começa no fim do mês</EmptyTitle>
              <EmptyDescription>
                Cada ponto é um fechamento de mês. O primeiro sai em {displayDate(closingDate(nextReview))}; até lá, a
                taxa de cada título está na tabela acima.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        ) : (
          <div className="grid gap-2">
            <Legend withGovernment={withGovernment} />
            <RatesChart rows={rows} withGovernment={withGovernment} />
            {withGovernment && <DebtChart rows={rows} />}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

const LEGEND_ITEMS = [
  { label: "Selic", color: INDEX_COLORS.SELIC },
  { label: "Prefixado mais curto", color: INDEX_COLORS.Prefixado },
  { label: "IPCA+ mais curto", color: INDEX_COLORS.IPCA },
];

function Legend({ withGovernment }: { withGovernment: boolean }) {
  return (
    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
      {LEGEND_ITEMS.map((item) => (
        <span key={item.label} className="flex items-center gap-1.5">
          <span aria-hidden className="h-0.5 w-3.5 rounded-full" style={{ backgroundColor: item.color }} />
          {item.label}
        </span>
      ))}
      {withGovernment && (
        <span className="flex items-center gap-1.5">
          <span aria-hidden className="h-0.5 w-3.5 rounded-full bg-foreground" />
          Dívida ÷ PIB
        </span>
      )}
    </div>
  );
}

function RatesChart({ rows, withGovernment }: { rows: HistoryRow[]; withGovernment: boolean }) {
  return (
    <ResponsiveContainer width="100%" height={210}>
      <LineChart data={rows} syncId="treasury" margin={MARGIN}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="time"
          type="number"
          scale="time"
          domain={["dataMin", "dataMax"]}
          tickFormatter={timeLabel}
          tick={TICK}
          axisLine={false}
          tickLine={false}
          hide={withGovernment}
        />
        <YAxis
          domain={["auto", "auto"]}
          tickFormatter={(value: number) => displayPercent(value, 1)}
          tick={TICK}
          axisLine={false}
          tickLine={false}
          width={AXIS_WIDTH}
        />
        <Tooltip
          cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
          content={({ active, payload }) => (
            <RatesTooltip
              active={active}
              row={payload[0]?.payload as HistoryRow | undefined}
              withGovernment={withGovernment}
            />
          )}
        />
        <Line dataKey="selic" stroke={INDEX_COLORS.SELIC} strokeWidth={2} dot={false} isAnimationActive={false} />
        <Line
          dataKey="prefixed"
          stroke={INDEX_COLORS.Prefixado}
          strokeWidth={2}
          dot={false}
          connectNulls
          isAnimationActive={false}
        />
        <Line
          dataKey="inflation"
          stroke={INDEX_COLORS.IPCA}
          strokeWidth={2}
          dot={false}
          connectNulls
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function DebtChart({ rows }: { rows: HistoryRow[] }) {
  const top = Math.max(1.2, Math.ceil(Math.max(...rows.map((row) => row.debt ?? 0)) * 10) / 10);

  return (
    <div className="grid gap-1">
      <span className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
        Dívida ÷ PIB <MetricHint metric={DEBT_GDP} />
        <span className="font-normal">· o fundo é a faixa do prêmio: Moderado, Alto, Crítico</span>
      </span>
      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={rows} syncId="treasury" margin={MARGIN}>
          {PREMIUM_BANDS.map((band, index) => (
            <ReferenceArea
              key={band.name}
              y1={band.from}
              y2={PREMIUM_BANDS[index + 1]?.from ?? top}
              fill={BAND_FILLS[index]}
              fillOpacity={1}
              ifOverflow="hidden"
            />
          ))}
          <XAxis
            dataKey="time"
            type="number"
            scale="time"
            domain={["dataMin", "dataMax"]}
            tickFormatter={timeLabel}
            tick={TICK}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, top]}
            ticks={[0, 0.5, 1]}
            tickFormatter={(value: number) => `${Math.round(value * 100)}%`}
            tick={TICK}
            axisLine={false}
            tickLine={false}
            width={AXIS_WIDTH}
          />
          <Tooltip cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }} content={() => null} />
          <Line
            dataKey="debt"
            stroke="var(--foreground)"
            strokeWidth={2}
            dot={false}
            connectNulls
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

type RatesTooltipProps = { active: boolean | undefined; row: HistoryRow | undefined; withGovernment: boolean };

function RatesTooltip({ active, row, withGovernment }: RatesTooltipProps) {
  if (!active || !row) return null;

  const lines: { label: string; value: string; color: string }[] = [
    { label: "Selic", value: displayPercent(row.selic), color: INDEX_COLORS.SELIC },
  ];
  if (row.prefixed !== null && row.prefixedName)
    lines.push({ label: row.prefixedName, value: displayPercent(row.prefixed), color: INDEX_COLORS.Prefixado });
  if (row.inflation !== null && row.inflationName)
    lines.push({ label: row.inflationName, value: displayPercent(row.inflation), color: INDEX_COLORS.IPCA });

  return (
    <div className="grid gap-1 rounded-lg border bg-popover px-2.5 py-2 text-xs shadow-md">
      <b className="font-semibold">{timeLabel(row.time)} · fechamento</b>
      {lines.map((line) => (
        <span key={line.label} className="flex items-center justify-between gap-6">
          <span className="flex items-center gap-1.5">
            <span aria-hidden className="size-2 rounded-full" style={{ backgroundColor: line.color }} />
            {line.label}
          </span>
          <span className="font-mono font-semibold">{line.value}</span>
        </span>
      ))}
      {withGovernment && row.debt !== null && (
        <>
          <span className="flex items-center justify-between gap-6 border-t border-muted pt-1">
            <span>Dívida ÷ PIB</span>
            <span className="font-mono font-semibold">{displayPercent(row.debt, 1)}</span>
          </span>
          <span className="flex items-center justify-between gap-6">
            <span>Prêmio</span>
            <span className="font-mono font-semibold">+{pointsOf(row.premium)}</span>
          </span>
        </>
      )}
    </div>
  );
}
