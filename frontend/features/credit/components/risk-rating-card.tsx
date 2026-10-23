import { MetricLabel } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { displaySpread, displayWholePercent } from "@/shared/lib/credit";
import { LEVERAGE, RISK_RATING, VOLATILITY } from "@/shared/lib/credit-metrics";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth, displayPercent } from "@/shared/lib/utils/display";
import type { CreditLadderTier, CreditRating } from "@/types";
import { CreditGradeMark } from "./credit-grade-mark";

type RiskRatingCardProps = { rating: CreditRating };

const pluralDelays = (count: number) => `${count} ${count === 1 ? "atraso" : "atrasos"}`;

/** Nota de risco: a letra, a escada de faixas e os três fatores que somam os pontos. */
export function RiskRatingCard({ rating }: RiskRatingCardProps) {
  const current = rating.ladder.find((tier) => tier.grade === rating.grade);
  const subtitle =
    current && current.spread !== null
      ? `SELIC ${displaySpread(current.spread)} ao ano e dívida até ${displayWholePercent(current.debt_limit)} do patrimônio`
      : "Sem crédito novo nesta faixa";

  const factors = [
    {
      key: "leverage",
      name: <MetricLabel metric={LEVERAGE} />,
      value: LEVERAGE.format(rating.leverage.value),
      part: rating.leverage,
      description: "Sem dívida vale 40; cada 10% tira 4.",
    },
    {
      key: "volatility",
      name: <MetricLabel metric={VOLATILITY} />,
      value: rating.volatility.value === null ? "Pouco histórico" : `${displayPercent(rating.volatility.value, 0)} a.a.`,
      part: rating.volatility,
      description: "45% ao ano ou mais vale zero.",
    },
    {
      key: "payments",
      name: "Pagamentos em dia",
      value: pluralDelays(rating.payments.late_installments),
      part: rating.payments,
      description: "Cada parcela atrasada em 12 meses tira 10.",
    },
  ];

  return (
    <Card>
      <CardContent>
        <div className="grid gap-4">
          {/* Nota atual */}
          <div className="flex items-center gap-4">
            <CreditGradeMark grade={rating.grade} />
            <div className="grid gap-0.5">
              <span className="flex items-center gap-1.5 text-[15px] font-semibold">
                <MetricLabel metric={RISK_RATING} />
                <span className="font-mono font-medium text-muted-foreground">{RISK_RATING.format(rating.points)}</span>
              </span>
              <span className="text-[13px] text-muted-foreground">{subtitle}</span>
              <span className="text-xs text-muted-foreground">
                Recalculada no fim de cada mês · a próxima é em {displayDayMonth(rating.next_review)}
              </span>
            </div>
          </div>

          {/* Escada de faixas */}
          <div className="grid gap-1.5">
            <ol className="grid grid-cols-8 gap-1">
              {rating.ladder.map((tier) => (
                <LadderCell key={tier.grade} tier={tier} current={tier.grade === rating.grade} previous={tier.grade === rating.previous_grade} />
              ))}
            </ol>
            <span className="text-xs text-muted-foreground">
              Spread sobre a SELIC, em pontos ao ano, e o limite da dívida em % do patrimônio. D não recebe crédito novo.
            </span>
          </div>

          {/* Fatores */}
          <div>
            {factors.map((factor) => (
              <div
                key={factor.key}
                className="grid grid-cols-[minmax(0,1fr)_92px_96px_52px] items-center gap-x-3.5 gap-y-1 border-t border-muted py-2.5"
              >
                <span className="font-medium">{factor.name}</span>
                <span className="text-right font-mono text-[13px] text-muted-foreground">{factor.value}</span>
                <Progress
                  value={(Number(factor.part.points) / Number(factor.part.max_points)) * 100}
                  size="sm"
                  aria-label={`Pontos de ${factor.key}`}
                />
                <span className="text-right font-mono font-semibold">
                  {Number(factor.part.points)}
                  <span className="font-normal text-muted-foreground">/{Number(factor.part.max_points)}</span>
                </span>
                <span className="col-span-full text-xs text-muted-foreground">{factor.description}</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function LadderCell({ tier, current, previous }: { tier: CreditLadderTier; current: boolean; previous: boolean }) {
  const closed = tier.spread === null;
  return (
    <li
      aria-current={current ? "true" : undefined}
      className={cn(
        "grid justify-items-center gap-0.5 rounded-[7px] bg-subtle pt-1.5 pb-1 text-[11px] text-muted-foreground",
        current && "bg-foreground text-background/80",
        previous && !current && "bg-card ring-1 ring-input ring-inset",
      )}
    >
      <b className={cn("font-mono text-[13px] text-foreground", current && "text-background")}>{tier.grade}</b>
      <span>{closed ? "—" : displaySpread(tier.spread ?? 0)}</span>
      <span className="text-[10px]">{closed ? "—" : displayWholePercent(tier.debt_limit)}</span>
    </li>
  );
}
