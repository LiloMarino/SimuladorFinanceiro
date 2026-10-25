import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import type { GovernmentPanel } from "@/types";
import { approvalTone, pointsTone, signedPoints, successionLabel } from "../lib/government";
import { APPROVAL } from "../lib/government-metrics";
import { ApprovalChart } from "./approval-chart";

const WEIGHTS = [
  ["Inflação", "+4 na meta; −3 por ponto acima"],
  ["Bolsa em 12 meses", "±1 a cada 5%, até ±6"],
  ["Imposto novo", "−1 a −5 ao valer, some em 6 meses"],
  ["Corte de imposto", "+1 a +3, enquanto o governo dura"],
  ["Promessa", "−3 por faixa de distância"],
] as const;

const TONES = { success: "text-success", warning: "text-warning", destructive: "text-destructive" } as const;

type ApprovalCardProps = { panel: GovernmentPanel };

/** A popularidade do governo: o número de hoje, o histórico mensal e cada fator que a compõe. */
export function ApprovalCard({ panel }: ApprovalCardProps) {
  const approval = panel.approval;
  if (!approval) return null;
  const tone = TONES[approvalTone(approval)];

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 content-start gap-3.5">
          <h2 className="text-[15px] font-semibold">Popularidade</h2>

          <div className="grid gap-1">
            <span className={cn("font-mono text-4xl leading-tight font-semibold tabular-nums", tone)}>
              {approval.value}%
            </span>
            <span className="text-xs leading-snug text-muted-foreground">
              De cada 100 eleitores, {approval.value} aprovam o governo. É também a chance de cada medida passar no Congresso.
            </span>
          </div>

          <ApprovalChart approval={approval} />

          {/* Fatores da aprovação de hoje */}
          <ul className="grid">
            {approval.factors.map((factor) => (
              <li
                key={`${factor.kind}-${factor.measure_id ?? ""}`}
                className="flex items-center gap-2.5 border-t py-1.75 text-[13px]"
              >
                <span
                  className={cn(
                    "w-11 shrink-0 font-mono font-semibold",
                    factor.kind !== "BASE" && pointsTone(factor.points),
                  )}
                >
                  {factor.kind === "BASE" ? factor.points : signedPoints(factor.points)}
                </span>
                <span className="flex-1">{factor.description}</span>
              </li>
            ))}
            <li className="flex items-center gap-2.5 border-t-2 border-foreground py-2 text-[13px]">
              <span className={cn("w-11 shrink-0 font-mono font-bold", tone)}>{approval.value}%</span>
              <b className="flex-1">Aprovação hoje</b>
            </li>
            {approval.upcoming.map((effect) => (
              <li
                key={effect.measure_id}
                className="flex items-center gap-2.5 border-t py-1.75 text-[13px] text-muted-foreground"
              >
                <span className="min-w-11 shrink-0 font-mono font-semibold whitespace-nowrap">
                  {signedPoints(effect.impact)}
                </span>
                <span className="flex-1">{effect.description}</span>
              </li>
            ))}
          </ul>

          {/* Como cada fator pesa */}
          <div className="grid gap-1.5">
            <span className="flex items-center gap-1 text-xs font-medium">
              Como cada fator pesa
              <MetricHint metric={APPROVAL} />
            </span>
            <dl className="grid gap-0.5 text-xs">
              {WEIGHTS.map(([factor, rule]) => (
                <div key={factor} className="flex justify-between gap-2 border-b border-dashed py-0.75 last:border-b-0">
                  <dt className="text-muted-foreground">{factor}</dt>
                  <dd className="font-mono">{rule}</dd>
                </div>
              ))}
            </dl>
          </div>

          <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-normal text-muted-foreground">
            A linha vermelha tracejada é o piso: {approval.impeachment_months} meses seguidos abaixo de {approval.floor}%
            levam a impeachment, e {successionLabel(panel)}.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
