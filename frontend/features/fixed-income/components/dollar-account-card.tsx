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
        <div className="flex h-full flex-col justify-between gap-4">
          {/* Cabeçalho */}
          <div className="flex items-start justify-between gap-3">
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
                Rende o juro americano todo dia útil e volta ao caixa em qualquer pregão, pelo dólar do dia.
              </span>
            </div>
            <div className="flex shrink-0 items-center gap-3">
              <a
                href={DOLLAR_ACCOUNT_DOCS_URL}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:text-primary-hover"
              >
                Saiba mais
                <ExternalLink className="size-3" />
              </a>
              <Button
                variant="outline"
                size="sm"
                nativeButton={false}
                render={<Link to={`/fixed-income/${offer.asset_uuid}`} />}
              >
                Investir
              </Button>
            </div>
          </div>

          {/* Métricas */}
          <div className="flex flex-wrap gap-x-6 gap-y-3">
            <Metric
              metric={FED_RATE}
              value={
                indicators
                  ? `${displayPercent(indicators.fed)} a.a.`
                  : displayRateLabel(offer.rate_index, offer.interest_rate)
              }
            />
            <Metric metric={DOLLAR_TODAY} value={offer.fx_rate ? `US$ 1 = ${displayMoney(offer.fx_rate)}` : "—"} />
            {showHelp && indicators && (
              <Metric
                metric={BREAK_EVEN}
                value={displayPercent(breakEvenDollarRise(indicators.cdi, indicators.fed), 1)}
              />
            )}
            <Metric metric={DOLLAR_ACCOUNT_TAX} value="15% do ganho" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function Metric({ metric, value }: { metric: MetricInfo; value: ReactNode }) {
  return (
    <div className="grid gap-0.5">
      <span className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
        {metric.label}
        <MetricHint metric={metric} />
      </span>
      <b className="font-mono font-semibold whitespace-nowrap">{value}</b>
    </div>
  );
}
