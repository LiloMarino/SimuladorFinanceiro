import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { InfoHint } from "@/shared/components/info-hint";
import { MetricHint } from "@/shared/components/metric-hint";
import { useAuth } from "@/shared/hooks/useAuth";
import { useGoalProgress } from "@/shared/hooks/queries/useGoalProgress";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { displayGoalPercent, ownStanding } from "@/shared/lib/goal";
import { GOAL_PERCENT } from "@/shared/lib/goal-metrics";
import { useEconomicIndicators } from "@/shared/hooks/queries/useEconomicIndicators";
import { displayMoney, displayMoneyCompact, displayPercent } from "@/shared/lib/utils/display";
import type { PortfolioState } from "@/types";

const INDICATOR_HINTS = {
  CDI: "Juro que os bancos cobram entre si por um dia, publicado pelo Banco Central. Aqui, o CDI do dia simulado levado para o ano. Ex.: 14,9% a.a. faz R$ 1.000 num CDB 100% do CDI virarem cerca de R$ 1.149 em um ano, se a taxa não mudar.",
  SELIC:
    "Taxa básica de juros do Banco Central, o indexador do Tesouro Selic. Aqui, a taxa do dia simulado levada para o ano. Fica sempre muito perto do CDI.",
  IPCA: "Inflação oficial: quanto os preços subiram nos 12 meses até o mês simulado. Ex.: 4,5% quer dizer que o que custava R$ 100 passou a custar R$ 104,50. Investimento que rende menos que isso perde poder de compra.",
};

/** Faixa-resumo: patrimônio, como ele está dividido e os indicadores do dia. */
export function PortfolioSummary({ portfolio }: { portfolio: PortfolioState }) {
  const { user } = useAuth();
  const { simulation } = useSimulation();
  const { data: goal } = useGoalProgress();
  const match = simulation?.simulation;
  const ownGoal = goal && match ? ownStanding(goal, match.player_grouping, user?.nickname ?? "") : undefined;
  const positive = Number(portfolio.total_return_value) >= 0;
  const allocation = [
    {
      label: "Renda variável",
      value: portfolio.variable_income_value,
      pct: portfolio.variable_income_networth_pct,
      color: "bg-chart-1",
    },
    {
      label: "Renda fixa",
      value: portfolio.fixed_income_value,
      pct: portfolio.fixed_income_networth_pct,
      color: "bg-chart-2",
    },
    { label: "Caixa", value: portfolio.cash, pct: portfolio.cash_pct, color: "bg-input" },
  ];
  const allInCash = Number(portfolio.invested_value) === 0;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-6 lg:grid-cols-[1.1fr_1.5fr_1fr] lg:gap-0">
          {/* Patrimônio */}
          <div className="grid content-start gap-1.5 lg:pr-6">
            <span className="text-xs font-medium text-muted-foreground">Patrimônio total</span>
            <div className="flex items-center gap-3">
              <span className="font-mono text-[30px] leading-none font-semibold">
                {displayMoney(portfolio.total_networth)}
              </span>
              {!allInCash && (
                <Badge variant={positive ? "success" : "destructive"}>
                  {positive ? "▲" : "▼"} {displayPercent(portfolio.total_return_pct)}
                </Badge>
              )}
            </div>
            <span className="text-[13px] text-muted-foreground">
              {allInCash ? (
                "Tudo em caixa. Comece comprando ações ou investindo em renda fixa."
              ) : (
                <>
                  <span className={positive ? "text-success" : "text-destructive"}>
                    {positive ? "+" : ""}
                    {displayMoney(portfolio.total_return_value)}
                  </span>{" "}
                  sobre {displayMoney(portfolio.capital_provided)} aportados
                </>
              )}
            </span>
            {goal && ownGoal && (
              <span className="flex items-center gap-1 text-[13px] text-muted-foreground">
                <b className="font-mono text-foreground">{displayGoalPercent(ownGoal.fraction)}</b> da meta de{" "}
                {displayMoneyCompact(goal.goal)}
                <MetricHint metric={GOAL_PERCENT} />
              </span>
            )}
          </div>

          {/* Alocação */}
          <div className="grid content-start gap-2.5 lg:border-l lg:px-6">
            <span className="text-xs font-medium text-muted-foreground">
              Alocação · investido {displayMoney(portfolio.invested_value)} · {displayPercent(portfolio.invested_pct)}
            </span>
            <div className="flex h-2.5 gap-0.5 overflow-hidden rounded-full bg-muted">
              {allocation.map((a) => (
                <span key={a.label} className={a.color} style={{ width: `${Number(a.pct) * 100}%` }} />
              ))}
            </div>
            <ul className="grid grid-cols-3 gap-3">
              {allocation.map((a) => (
                <li key={a.label} className="grid gap-0.5">
                  <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <span className={`size-2 rounded-sm ${a.color}`} aria-hidden="true" />
                    {a.label}
                  </span>
                  <span className="font-mono text-sm font-semibold">{displayMoney(a.value)}</span>
                  <span className="font-mono text-xs text-muted-foreground">{displayPercent(a.pct)}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Indicadores */}
          <EconomicIndicators />
        </div>
      </CardContent>
    </Card>
  );
}

function EconomicIndicators() {
  const { data, isLoading, isError, refetch } = useEconomicIndicators();

  const items = data
    ? [
        { label: "CDI", value: `${displayPercent(data.cdi)} a.a.`, hint: INDICATOR_HINTS.CDI },
        { label: "SELIC", value: `${displayPercent(data.selic)} a.a.`, hint: INDICATOR_HINTS.SELIC },
        { label: "IPCA 12m", value: displayPercent(data.ipca), hint: INDICATOR_HINTS.IPCA },
      ]
    : [];

  return (
    <div className="grid content-start gap-2 rounded-lg bg-subtle p-4 lg:ml-6 lg:border-l">
      <span className="text-xs font-medium text-muted-foreground">Indicadores hoje</span>
      {isLoading && <Skeleton className="h-20" />}
      {isError && (
        <div className="grid justify-items-start gap-2 text-[13px] text-muted-foreground">
          Não deu pra carregar CDI, SELIC e IPCA.
          <Button variant="outline" size="sm" onClick={() => void refetch()}>
            Tentar de novo
          </Button>
        </div>
      )}
      {items.map((i) => (
        <div key={i.label} className="flex items-center justify-between text-[13px]">
          <span className="flex items-center gap-1 text-muted-foreground">
            {i.label}
            <InfoHint label={`O que é ${i.label}`}>{i.hint}</InfoHint>
          </span>
          <span className="font-mono font-semibold">{i.value}</span>
        </div>
      ))}
    </div>
  );
}
