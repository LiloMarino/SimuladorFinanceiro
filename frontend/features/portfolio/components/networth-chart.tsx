import { useState } from "react";
import { Area, AreaChart, CartesianGrid, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { LineChart as LineChartIcon } from "lucide-react";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import {
  displayDate,
  displayMoney,
  displayMoneyCompact,
  displayMonthSlashYear,
  parseLocalDate,
} from "@/shared/lib/utils/display";
import type { PortfolioHistoryPoint } from "@/types";

const METRICS = {
  total_networth: { label: "Patrimônio", color: "var(--chart-1)" },
  total_equity: { label: "Renda variável", color: "var(--chart-1)" },
  total_fixed: { label: "Renda fixa", color: "var(--chart-2)" },
  total_cash: { label: "Caixa", color: "var(--faint-foreground)" },
} as const;

type Metric = keyof typeof METRICS;

/** Evolução da carteira; no patrimônio, a linha tracejada é o que o jogador pôs. */
export function NetworthChart({ history }: { history: PortfolioHistoryPoint[] }) {
  const [metric, setMetric] = useState<Metric>("total_networth");
  const { label, color } = METRICS[metric];
  const showProvided = metric === "total_networth";

  // Recharts desenha número; os valores seguem em string até aqui
  const data = history.map((p) => ({
    date: p.snapshot_date,
    value: Number(p[metric]),
    provided: Number(p.total_provided),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Evolução do patrimônio</CardTitle>
        <CardDescription>
          {showProvided ? "A linha tracejada é o que você aportou: acima dela, está ganhando." : `${label}, dia a dia.`}
        </CardDescription>
        <CardAction>
          <ToggleGroup
            variant="segmented"
            aria-label="Série do gráfico"
            value={[metric]}
            onValueChange={(values) => values[0] && setMetric(values[0] as Metric)}
          >
            {(Object.keys(METRICS) as Metric[]).map((key) => (
              <ToggleGroupItem key={key} value={key}>
                {METRICS[key].label}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </CardAction>
      </CardHeader>
      <CardContent>
        {data.length < 2 ? (
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
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
              <defs>
                <linearGradient id="networth-fill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" stopColor={color} stopOpacity={0.18} />
                  <stop offset="1" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} stroke="var(--border)" />
              <XAxis
                dataKey="date"
                tickFormatter={(d: string) => displayMonthSlashYear(d)}
                tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
                axisLine={false}
                tickLine={false}
                minTickGap={48}
              />
              <YAxis
                tickFormatter={(v: number) => displayMoneyCompact(v)}
                tick={{ fontSize: 11, fill: "var(--faint-foreground)" }}
                axisLine={false}
                tickLine={false}
                width={84}
                domain={["auto", "auto"]}
              />
              <Tooltip
                cursor={{ stroke: "var(--input)" }}
                contentStyle={{ borderRadius: 10, borderColor: "var(--border)", fontSize: 12 }}
                labelFormatter={(d) => displayDate(parseLocalDate(String(d)))}
                formatter={(v, name) => [displayMoney(Number(v)), name === "provided" ? "Aportado" : label]}
              />
              <Area type="monotone" dataKey="value" stroke={color} strokeWidth={2} fill="url(#networth-fill)" />
              {showProvided && (
                <Line
                  type="stepAfter"
                  dataKey="provided"
                  stroke="var(--faint-foreground)"
                  strokeWidth={1.5}
                  strokeDasharray="5 4"
                  dot={false}
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
