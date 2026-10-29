import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { InfoHint } from "@/shared/components/info-hint";
import { PremiumCurveChart } from "@/shared/components/premium-curve-chart";
import { Card, CardContent } from "@/shared/components/ui/card";
import { DEBT_GDP, RISK_PREMIUM } from "@/shared/lib/budget-metrics";
import { displayDate, displayPercent, displayShortMonthYear } from "@/shared/lib/utils/display";
import type { Budget } from "@/types";
import { debtSeries, type DebtRow } from "../lib/budget";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };
const DEBT_COLOR = "var(--chart-5)";

type DebtPremiumCardProps = { budget: Budget };

function DebtTooltip({ active, payload }: { active?: boolean; payload?: { payload: DebtRow }[] }) {
  const row = payload?.[0]?.payload;
  if (!active || !row) return null;
  const value = row.history ?? row.projection;
  if (value === undefined) return null;
  return (
    <div className="grid gap-1 rounded-lg border bg-popover px-2.5 py-2 text-xs shadow-md">
      <span className="text-muted-foreground">{displayDate(new Date(row.time))}</span>
      <span className="flex items-center justify-between gap-6">
        <span>{row.history === undefined ? "Projeção" : DEBT_GDP.label}</span>
        <span className="font-mono font-semibold">{displayPercent(value, 1)}</span>
      </span>
    </div>
  );
}

/** A dívida em % do PIB desde o início e a projeção até o fim do mandato, se nada mais mudar. */
function DebtChart({ budget }: { budget: Budget }) {
  const rows = debtSeries(budget);

  return (
    <ResponsiveContainer width="100%" height={210}>
      <LineChart data={rows} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
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
          domain={[(min: number) => Math.min(0.4, min), (max: number) => Math.max(0.6, max)]}
          tickFormatter={(value: number) => displayPercent(value, 0)}
          tick={TICK}
          axisLine={false}
          tickLine={false}
          width={40}
        />
        <Tooltip cursor={{ stroke: "var(--foreground)", strokeOpacity: 0.4 }} content={<DebtTooltip />} />
        <ReferenceLine
          y={Number(budget.premium_floor)}
          stroke="var(--muted-foreground)"
          strokeDasharray="5 4"
          label={{ value: "50%", position: "insideBottomRight", fontSize: 10.5, fill: "var(--muted-foreground)" }}
        />
        <Line dataKey="history" stroke={DEBT_COLOR} strokeWidth={2} dot={false} isAnimationActive={false} />
        <Line
          dataKey="projection"
          stroke={DEBT_COLOR}
          strokeWidth={2}
          strokeDasharray="5 4"
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

/** Dívida e prêmio de risco: o caminho da dívida até o fim do mandato e o quanto cada nível dela encarece o Tesouro. */
export function DebtPremiumCard({ budget }: DebtPremiumCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <div className="flex items-center gap-1.5">
            <h2 className="text-[15px] font-semibold">Dívida e prêmio de risco</h2>
            <InfoHint label="Como ler a dívida e o prêmio">
              <div className="space-y-1 text-left">
                <p>{RISK_PREMIUM.definition}</p>
                <p>{RISK_PREMIUM.example}</p>
                <p>{RISK_PREMIUM.reading}</p>
              </div>
            </InfoHint>
          </div>

          <div className="grid gap-1">
            <span className="text-xs font-medium text-muted-foreground">
              Dívida ÷ PIB, com a projeção até o fim do mandato
            </span>
            <DebtChart budget={budget} />
          </div>

          <div className="grid gap-1">
            <span className="text-xs font-medium text-muted-foreground">
              Prêmio de risco pela dívida (pontos ao ano, pela dívida em % do PIB)
            </span>
            <PremiumCurveChart budget={budget} height={200} />
          </div>

          <p className="rounded-md bg-subtle px-2.5 py-1.5 text-xs text-muted-foreground">
            O prêmio soma à taxa dos títulos novos do Tesouro na renda fixa e ao juro que a própria dívida paga.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
