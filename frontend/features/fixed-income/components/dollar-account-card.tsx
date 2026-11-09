import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ExternalLink } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { FlagUs } from "@/shared/components/icons/flag-us";
import { DailyLiquidityBadge } from "@/shared/components/daily-liquidity-badge";
import { MetricHint } from "@/shared/components/metric-hint";
import { useEconomicIndicators } from "@/shared/hooks/queries/useEconomicIndicators";
import type { MetricInfo } from "@/shared/lib/metric-info";
import { displayMoney, displayPercent, displayRateLabel } from "@/shared/lib/utils/display";
import type { FixedIncomeOffer } from "@/types";
import { breakEvenDollarRise } from "../lib/carry";
import {
  BREAK_EVEN,
  DOLLAR_ACCOUNT_DOCS_URL,
  DOLLAR_ACCOUNT_TAX,
  DOLLAR_TODAY,
  FED_RATE,
} from "../lib/dollar-account-metrics";

type DollarAccountCardProps = {
  offer: FixedIncomeOffer;
  held: boolean;
  /** Com a ajuda desligada (modo Especialista) o empate com o CDI fica por conta do jogador */
  showHelp: boolean;
};

/** A conta em dólar do topo da Renda fixa: o juro americano, o dólar de hoje e o empate com o CDI. */
export function DollarAccountCard({ offer, held, showHelp }: DollarAccountCardProps) {
  const { data: indicators } = useEconomicIndicators();

  return (
    <Card variant="info" className="h-full">
      <CardContent className="h-full">
        <div className="grid h-full content-between gap-4">
          <div className="grid gap-1">
            <span className="flex flex-wrap items-center gap-2">
              <DailyLiquidityBadge>Sempre disponível</DailyLiquidityBadge>
              <FlagUs size={20} />
              <b className="text-[15px] font-semibold">Conta em dólar</b>
              {held && (
                <Badge variant="info" size="sm">
                  na carteira
                </Badge>
              )}
            </span>
            <span className="text-[13px] text-muted-foreground">
              Seu dinheiro vira dólar e rende o juro americano, todo dia útil. Volta ao caixa em qualquer pregão, pelo
              dólar do dia.
            </span>
          </div>

          <div className="grid grid-cols-2 gap-x-5 gap-y-3">
            <Metric
              metric={FED_RATE}
              value={displayRateLabel(offer.rate_index, offer.interest_rate)}
              description={indicators ? `Fed a ${displayPercent(indicators.fed)} a.a., em dólar` : FED_RATE.description}
            />
            <Metric
              metric={DOLLAR_TODAY}
              value={offer.fx_rate ? `US$ 1 = ${displayMoney(offer.fx_rate)}` : "—"}
              description={DOLLAR_TODAY.description}
            />
            {showHelp && indicators && (
              <Metric
                metric={BREAK_EVEN}
                value={displayPercent(breakEvenDollarRise(indicators.cdi, indicators.fed), 1)}
                description={BREAK_EVEN.description}
              />
            )}
            <Metric
              metric={DOLLAR_ACCOUNT_TAX}
              value={<Badge variant="secondary">15% do ganho</Badge>}
              description={DOLLAR_ACCOUNT_TAX.description}
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              nativeButton={false}
              render={<Link to={`/fixed-income/${offer.asset_uuid}`} />}
            >
              Investir
            </Button>
            <a
              href={DOLLAR_ACCOUNT_DOCS_URL}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:text-primary-hover"
            >
              Saiba mais
              <ExternalLink className="size-3" />
            </a>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function Metric({ metric, value, description }: { metric: MetricInfo; value: ReactNode; description: string }) {
  return (
    <div className="grid gap-0.5">
      <span className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
        {metric.label}
        <MetricHint metric={metric} />
      </span>
      <b className="font-mono font-semibold">{value}</b>
      <span className="text-xs text-muted-foreground">{description}</span>
    </div>
  );
}
