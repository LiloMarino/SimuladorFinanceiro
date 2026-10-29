import { Link } from "react-router-dom";
import { InfoHint } from "@/shared/components/info-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { DEBT_GDP, RISK_PREMIUM } from "@/shared/lib/budget-metrics";
import { cn } from "@/shared/lib/utils";
import { displayMoneyLarge } from "@/shared/lib/utils/display";
import type { EconomyPanel } from "@/types";
import { economyRows } from "../lib/economy";
import { SeriesChart } from "./series-chart";

type DebtCardProps = {
  panel: EconomyPanel;
  /** A dívida e o PIB do último fechamento, já resolvidos pelo pai: o cartão só existe com a expansão Governo */
  debt: NonNullable<EconomyPanel["debt"]>;
};

/** A dívida em % do PIB ao longo da partida, com os valores em reais do último fechamento. */
export function DebtCard({ panel, debt }: DebtCardProps) {
  const result = debt.month_result === null ? null : Number(debt.month_result);

  return (
    <Card>
      <CardContent>
        <div className="grid min-w-0 gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)] lg:items-center">
          <div className="grid gap-2">
            <div className="flex items-center gap-1.5">
              <h2 className="text-[15px] font-semibold">{DEBT_GDP.label}</h2>
              <InfoHint label="Como ler a dívida">
                <div className="space-y-1 text-left">
                  <p>{DEBT_GDP.definition}</p>
                  <p>{DEBT_GDP.example}</p>
                  <p>{DEBT_GDP.reading}</p>
                </div>
              </InfoHint>
            </div>
            <SeriesChart
              rows={economyRows(panel)}
              dataKey="debt"
              label="Dívida ÷ PIB"
              color="var(--chart-5)"
              reference={{ value: 0.5, label: "50%: o prêmio começa" }}
              height={200}
            />
          </div>

          <div className="grid gap-2.5">
            <p className="text-[13px] leading-normal">
              A dívida do governo, perto de tudo o que o país produz num ano. Acima de 50%, os títulos novos do Tesouro
              passam a cobrar o {RISK_PREMIUM.label.toLowerCase()}: {RISK_PREMIUM.description.toLowerCase()}.
            </p>
            <div className="grid gap-1.5 text-[13px]">
              <div className="flex items-center justify-between gap-4">
                <span>Dívida</span>
                <span className="font-mono font-semibold">{displayMoneyLarge(debt.debt_amount)}</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>PIB em 12 meses</span>
                <span className="font-mono font-semibold">{displayMoneyLarge(debt.gdp)}</span>
              </div>
              {result !== null && (
                <div className="flex items-center justify-between gap-4">
                  <span>Resultado do mês</span>
                  <span className={cn("font-mono font-semibold", result < 0 ? "text-destructive" : "text-success")}>
                    {displayMoneyLarge(result)}
                  </span>
                </div>
              )}
            </div>
            <Link to="/government?tab=accounts" className="text-[13px] font-medium text-primary hover:underline">
              Ver o orçamento no Governo ›
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
