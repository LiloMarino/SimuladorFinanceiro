import { Kpi } from "@/shared/components/kpi";
import { MetricHint } from "@/shared/components/metric-hint";
import { Card, CardContent } from "@/shared/components/ui/card";
import { COST_OF_DEBT } from "@/shared/lib/credit-metrics";
import { displayMoney, displaySignedPercent } from "@/shared/lib/utils/display";
import type { ReturnsPlayer } from "@/types";

type CreditCostCardProps = {
  player: ReturnsPlayer & { credit_cost: NonNullable<ReturnsPlayer["credit_cost"]> };
};

/** Quanto o crédito custou a quem pegou: retorno líquido do juro, juro pago e custo médio da dívida. */
export function CreditCostCard({ player }: CreditCostCardProps) {
  const { credit_cost: cost } = player;
  const finalReturn = player.cumulative_return.at(-1)?.value;

  return (
    <Card>
      <CardContent>
        <div className="grid gap-5 sm:grid-cols-3">
          <Kpi
            label="Retorno no período"
            value={finalReturn === undefined ? "—" : displaySignedPercent(finalReturn)}
            tone={finalReturn !== undefined && Number(finalReturn) < 0 ? "destructive" : "success"}
            note="Sobre o patrimônio; juro pago entra como custo"
          />
          <Kpi
            label="Juro pago até hoje"
            value={displayMoney(cost.interest_paid)}
            note={`${cost.paid_installments} ${cost.paid_installments === 1 ? "parcela" : "parcelas"}, ${
              cost.late_installments === 0 ? "nenhuma com multa" : `${cost.late_installments} com multa`
            }`}
          />
          <Kpi
            label={
              <>
                Custo da dívida
                <MetricHint metric={COST_OF_DEBT} />
              </>
            }
            value={cost.cost_of_debt === null ? "—" : COST_OF_DEBT.format(cost.cost_of_debt)}
            note="Média dos juros travados, pesada pelo saldo"
          />
        </div>
      </CardContent>
    </Card>
  );
}
