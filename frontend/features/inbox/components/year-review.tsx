import { Bar, BarChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import { KeyValueRow } from "@/shared/components/key-value-row";
import {
  displayMonthName,
  displayMonthShort,
  displaySignedMoney,
  displaySignedPercent,
} from "@/shared/lib/utils/display";
import type { YearReview } from "@/types";
import { YEAR_RETURN } from "../lib/metrics";
import { NetworthChange, ReturnComparison } from "./return-comparison";

const TICK = { fontSize: 10.5, fill: "var(--faint-foreground)" };

type YearReviewViewProps = { review: YearReview };

/** O ano de um jogador: a rentabilidade mês a mês, o melhor mês e a maior queda. */
export function YearReviewView({ review }: YearReviewViewProps) {
  // Alta e queda são séries empilhadas: cada mês preenche uma só, e a cor vem da série
  const rows = review.months.map((m) => {
    const value = Number(m.return_pct);
    return { month: m.month, value, gain: value >= 0 ? value : null, loss: value < 0 ? value : null };
  });

  return (
    <div className="grid gap-4">
      <NetworthChange start={review.networth_start} end={review.networth_end} />
      <ReturnComparison metric={YEAR_RETURN} value={review.return_pct} cdi={review.cdi_pct} ibov={review.ibov_pct} />

      {/* Rentabilidade mês a mês */}
      {rows.length > 0 && (
        <div className="grid gap-1">
          <span className="text-xs font-medium text-muted-foreground">Rentabilidade mês a mês</span>
          <ResponsiveContainer width="100%" height={96}>
            <BarChart data={rows} margin={{ top: 4, right: 4, left: 4, bottom: 0 }}>
              <XAxis
                dataKey="month"
                tickFormatter={displayMonthShort}
                tick={TICK}
                axisLine={false}
                tickLine={false}
                interval={0}
              />
              <ReferenceLine y={0} stroke="var(--border)" />
              <Tooltip
                cursor={{ fill: "var(--muted)" }}
                content={({ active, payload }) => {
                  const row = payload?.[0]?.payload as (typeof rows)[number] | undefined;
                  if (!active || !row) return null;
                  return (
                    <div className="grid gap-0.5 rounded-lg border bg-popover px-2.5 py-1.5 text-xs shadow-md">
                      <span className="text-muted-foreground">{displayMonthName(row.month)}</span>
                      <span className="font-mono font-semibold">{displaySignedPercent(row.value)}</span>
                    </div>
                  );
                }}
              />
              <Bar dataKey="gain" stackId="month" fill="var(--success)" isAnimationActive={false} radius={2} />
              <Bar dataKey="loss" stackId="month" fill="var(--destructive)" isAnimationActive={false} radius={2} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Destaques do ano */}
      <div className="grid">
        {review.best_month && (
          <KeyValueRow
            label={`Melhor mês: ${displayMonthName(review.best_month.month)}`}
            value={displaySignedPercent(review.best_month.return_pct)}
          />
        )}
        {review.worst_month && (
          <KeyValueRow
            label={`${Number(review.worst_month.return_pct) < 0 ? "Maior queda" : "Pior mês"}: ${displayMonthName(review.worst_month.month)}`}
            value={displaySignedPercent(review.worst_month.return_pct)}
          />
        )}
        <KeyValueRow label="Aportes no ano" value={displaySignedMoney(review.contributions)} />
      </div>
    </div>
  );
}
