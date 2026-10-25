import { Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { PieChart as PieChartIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia } from "@/shared/components/ui/empty";
import { displayMoney, displayMoneyCompact, displayPercent } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";

type Slice = { name: string; value: number; pct: number; fill: string };
type Group = { label: string; slices: Slice[]; pct: number };

// Do maior ativo ao menor, o tom da classe vai clareando; o piso mantém o contraste com o cartão
const TONE_STEPS = [100, 78, 60, 46, 36, 28];

const toneOf = (base: string, index: number) =>
  `color-mix(in srgb, ${base} ${TONE_STEPS[Math.min(index, TONE_STEPS.length - 1)]}%, var(--card))`;

function toGroup(label: string, base: string, items: { name: string; value: string; pct: string }[]): Group {
  const slices = items
    .map((p) => ({ name: p.name, value: Number(p.value), pct: Number(p.pct) }))
    .sort((a, b) => b.value - a.value)
    .map((p, i): Slice => ({ ...p, fill: toneOf(base, i) }));
  return { label, slices, pct: slices.reduce((sum, s) => sum + s.pct, 0) };
}

/** Onde está o dinheiro investido: renda variável em azuis, renda fixa em verdes, ativo a ativo. */
export function AllocationDonut({ portfolio }: { portfolio: PortfolioState }) {
  const groups = [
    toGroup(
      "Renda variável",
      "var(--chart-1)",
      portfolio.variable_income.map((p) => ({ name: p.ticker, value: p.current_value, pct: p.portfolio_pct })),
    ),
    toGroup(
      "Renda fixa",
      "var(--chart-2)",
      portfolio.fixed_income.map((p) => ({ name: p.asset.name, value: p.current_value, pct: p.portfolio_pct })),
    ),
  ].filter((g) => g.slices.length > 0);
  const slices = groups.flatMap((g) => g.slices);

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
          <div className="grid items-center gap-4 sm:grid-cols-[136px_minmax(0,1fr)]">
            <div className="relative h-[136px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={slices}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={44}
                    outerRadius={64}
                    paddingAngle={1}
                    stroke="var(--card)"
                    strokeWidth={2}
                  />
                  <Tooltip
                    contentStyle={{ borderRadius: 10, borderColor: "var(--border)", fontSize: 12 }}
                    formatter={(v) => displayMoney(Number(v))}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="pointer-events-none absolute inset-0 grid place-content-center text-center">
                <span className="text-[11px] text-muted-foreground">Investido</span>
                <span className="font-mono text-[13px] font-semibold">
                  {displayMoneyCompact(portfolio.invested_value)}
                </span>
                <span className="text-[11px] text-muted-foreground">
                  {slices.length} {slices.length === 1 ? "ativo" : "ativos"}
                </span>
              </div>
            </div>

            <div className="grid min-w-0 gap-3">
              {groups.map((group) => (
                <section key={group.label} className="grid gap-1.5">
                  <header className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{group.label}</span>
                    <span className="font-mono">{displayPercent(group.pct, 1)}</span>
                  </header>
                  <ul className="grid gap-1.5 text-[13px]">
                    {group.slices.map((s) => (
                      <li key={s.name} className="flex min-w-0 items-center gap-2">
                        <span
                          className="size-2.5 shrink-0 rounded-sm"
                          style={{ backgroundColor: s.fill }}
                          aria-hidden="true"
                        />
                        <span className="min-w-0 flex-1 truncate" title={s.name}>
                          {s.name}
                        </span>
                        <span className="shrink-0 font-mono text-xs text-muted-foreground">
                          {displayMoney(s.value)}
                        </span>
                        <span className="w-12 shrink-0 text-right font-mono">{displayPercent(s.pct, 1)}</span>
                      </li>
                    ))}
                  </ul>
                </section>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
