import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { MetricHint } from "@/shared/components/metric-hint";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { CHART_FONT_SIZE, CHART_TICK } from "@/shared/lib/chart-text";
import {
  displayMonthSlashYear,
  displayPercent,
  displayPercentagePoints,
  displayShortDate,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { IncomeSeries } from "@/types";
import { SERIES_INFO, todaySentence } from "../lib/series";

type IncomeSeriesSectionProps = {
  series: IncomeSeries[];
};

/** "O que move sua renda": um gráfico de 12 meses por indicador, ou a alavanca do governo com as mudanças recentes. */
export function IncomeSeriesSection({ series }: IncomeSeriesSectionProps) {
  return (
    <section className="grid gap-3">
      <div className="grid gap-0.5">
        <h2 className="text-[15px] font-semibold">O que move sua renda</h2>
        <p className="text-[13px] text-muted-foreground">
          Os indicadores que mexem no seu salário, nos últimos 12 meses
        </p>
      </div>
      {series.length === 0 ? (
        <Card>
          <CardContent>
            <Empty>
              <EmptyHeader>
                <EmptyTitle>Sua renda só sobe com o IPCA</EmptyTitle>
                <EmptyDescription>
                  Nenhum indicador da economia mexe no salário da sua profissão: o reajuste anual repõe a inflação e
                  mais nada.
                </EmptyDescription>
              </EmptyHeader>
            </Empty>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {series.map((item) => (
            <SeriesCard key={item.key} series={item} />
          ))}
        </div>
      )}
    </section>
  );
}

function SeriesCard({ series }: { series: IncomeSeries }) {
  const info = SERIES_INFO[series.key];
  const sentence = todaySentence(series);
  return (
    <Card>
      <CardHeader className="grid-cols-[1fr_auto]">
        <div className="grid gap-1">
          <CardTitle>
            <span className="flex items-center gap-1.5">
              {info.title}
              <MetricHint metric={info.metric} />
            </span>
          </CardTitle>
          <CardDescription>{info.subtitle}</CardDescription>
        </div>
        <span className="font-mono text-lg font-semibold tabular-nums">{info.display(series.current)}</span>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3">
          {series.lever ? <LeverChanges series={series} /> : <SeriesChart series={series} />}
          {sentence && (
            <p className="text-[13px]">
              <b className="font-semibold">{sentence.lead}</b> {sentence.text}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function SeriesChart({ series }: { series: IncomeSeries }) {
  const info = SERIES_INFO[series.key];
  const rows = series.points.map((point) => ({ month: point.month, value: Number(point.value) }));
  return (
    <ResponsiveContainer width="100%" height={170}>
      <LineChart data={rows} margin={{ top: 14, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--border)" />
        <XAxis
          dataKey="month"
          tickFormatter={(month: string) => displayMonthSlashYear(month)}
          tick={CHART_TICK}
          axisLine={false}
          tickLine={false}
          interval="preserveStartEnd"
          minTickGap={24}
        />
        <YAxis
          tickFormatter={(value: number) => displaySignedPercent(value, 0)}
          tick={CHART_TICK}
          axisLine={false}
          tickLine={false}
          width={44}
          domain={["auto", "auto"]}
        />
        {series.neutral !== null && (
          <ReferenceLine
            y={Number(series.neutral)}
            stroke="var(--muted-foreground)"
            strokeDasharray="4 3"
            label={{
              value: `neutro: ${displayPercent(series.neutral, 1, { trim: true })}`,
              position: "insideTopLeft",
              fontSize: CHART_FONT_SIZE,
              fill: "var(--muted-foreground)",
            }}
          />
        )}
        {series.guides.map((guide) => (
          <ReferenceLine
            key={`${guide.value}-${guide.overtime}`}
            y={Number(guide.value)}
            stroke="var(--warning)"
            strokeDasharray="2 3"
            label={{
              value: guide.overtime ? "zero: a hora extra só existe acima" : "referência",
              position: "insideBottomLeft",
              fontSize: CHART_FONT_SIZE,
              fill: "var(--warning)",
            }}
          />
        ))}
        <Tooltip
          cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }}
          content={({ active, payload }) => {
            const row = payload[0]?.payload as (typeof rows)[number] | undefined;
            if (!active || !row) return null;
            return (
              <div className="grid gap-0.5 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                <span className="text-muted-foreground">{displayShortDate(row.month)}</span>
                <span className="font-mono font-semibold">{info.display(String(row.value))}</span>
              </div>
            );
          }}
        />
        <Line
          dataKey="value"
          type="linear"
          stroke="var(--primary)"
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function LeverChanges({ series }: { series: IncomeSeries }) {
  if (series.changes.length === 0) {
    return <p className="text-[13px] text-muted-foreground">O governo ainda não mexeu nesta medida.</p>;
  }
  return (
    <div className="grid gap-1.5">
      <span className="text-xs font-medium text-muted-foreground">Mudanças recentes</span>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Data</TableHead>
            <TableHead>Mudança</TableHead>
            <TableHead numeric>Variação</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {series.changes.map((change) => {
            const delta = Number(change.after) - Number(change.before);
            return (
              <TableRow key={change.change_date}>
                <TableCell numeric>{displayShortDate(change.change_date)}</TableCell>
                <TableCell>
                  <span className="grid">
                    <span>
                      {delta >= 0 ? "Governo subiu" : "Governo baixou"} para{" "}
                      {SERIES_INFO[series.key].display(change.after)}
                    </span>
                    {change.proposer_name !== null && (
                      <span className="text-xs text-muted-foreground">
                        proposto por {change.proposer_name}
                        {change.proposer_party !== null && ` (${change.proposer_party})`}
                      </span>
                    )}
                  </span>
                </TableCell>
                <TableCell numeric>
                  <Badge variant={delta >= 0 ? "success" : "warning"}>{displayPercentagePoints(delta, 1)}</Badge>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
