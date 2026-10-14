import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { PieChart as PieChartIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia } from "@/shared/components/ui/empty";
import { displayMoney, displayMoneyCompact, displayPercent } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";

// Cores na ordem fixa da paleta; do sexto ativo em diante, tudo vira "Outros"
const COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)", "var(--chart-5)"];
const OTHERS_COLOR = "var(--input)";

type Slice = { name: string; value: number; pct: number; color: string };

/** Onde está o dinheiro investido, ativo a ativo. */
export function AllocationDonut({ portfolio }: { portfolio: PortfolioState }) {
  const positions = [
    ...portfolio.variable_income.map((p) => ({ name: p.ticker, value: p.current_value, pct: p.portfolio_pct })),
    ...portfolio.fixed_income.map((p) => ({ name: p.asset.name, value: p.current_value, pct: p.portfolio_pct })),
  ]
    .map((p) => ({ ...p, value: Number(p.value), pct: Number(p.pct) }))
    .sort((a, b) => b.value - a.value);

  const top = positions.slice(0, COLORS.length).map((p, i): Slice => ({ ...p, color: COLORS[i] }));
  const rest = positions.slice(COLORS.length);
  const slices: Slice[] = rest.length
    ? [
        ...top,
        {
          name: `Outros (${rest.length})`,
          value: rest.reduce((sum, p) => sum + p.value, 0),
          pct: rest.reduce((sum, p) => sum + p.pct, 0),
          color: OTHERS_COLOR,
        },
      ]
    : top;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribuição dos investimentos</CardTitle>
      </CardHeader>
      <CardContent>
        {slices.length === 0 ? (
          <Empty variant="dashed">
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <PieChartIcon />
              </EmptyMedia>
              <EmptyDescription>
                Seus investimentos aparecem aqui, separados entre renda variável e renda fixa.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        ) : (
          <div className="grid items-center gap-4 sm:grid-cols-[180px_1fr]">
            <div className="relative h-[180px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={slices}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={58}
                    outerRadius={84}
                    paddingAngle={1}
                    stroke="var(--card)"
                    strokeWidth={2}
                  >
                    {slices.map((s) => (
                      <Cell key={s.name} fill={s.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ borderRadius: 10, borderColor: "var(--border)", fontSize: 12 }}
                    formatter={(v) => displayMoney(Number(v))}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="pointer-events-none absolute inset-0 grid place-content-center text-center">
                <span className="text-[11px] text-muted-foreground">Investido</span>
                <span className="font-mono font-semibold">{displayMoneyCompact(portfolio.invested_value)}</span>
                <span className="text-[11px] text-muted-foreground">
                  {positions.length} {positions.length === 1 ? "ativo" : "ativos"}
                </span>
              </div>
            </div>
            <ul className="grid gap-1.5 text-[13px]">
              {slices.map((s) => (
                <li key={s.name} className="flex items-center gap-2">
                  <span
                    className="size-2.5 shrink-0 rounded-sm"
                    style={{ backgroundColor: s.color }}
                    aria-hidden="true"
                  />
                  <span className="flex-1 truncate">{s.name}</span>
                  <span className="font-mono">{displayMoney(s.value)}</span>
                  <span className="w-14 text-right font-mono text-muted-foreground">{displayPercent(s.pct, 1)}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
