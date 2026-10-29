import type { GovernmentPanel, MeasureKind } from "@/types";
import { useBudget } from "@/shared/hooks/queries/useBudget";
import { BudgetReadersCard } from "./budget-readers-card";
import { BudgetCard } from "./budget-card";
import { BudgetError, BudgetSkeleton } from "./budget-states";
import { DebtPremiumCard } from "./debt-premium-card";
import { RevenueCard } from "./revenue-card";
import { SpendingCard } from "./spending-card";
import { TaxesCard } from "./taxes-card";

type AccountsTabProps = {
  panel: GovernmentPanel;
  onPropose: (kind?: MeasureKind) => void;
};

/** A aba Contas: o orçamento do país, de onde vem a receita, a dívida com o prêmio e os impostos e o gasto público em vigor. */
export function AccountsTab({ panel, onPropose }: AccountsTabProps) {
  const { data: budget, error, refetch } = useBudget();

  if (!budget) {
    return error ? <BudgetError onRetry={() => void refetch()} /> : <BudgetSkeleton />;
  }

  return (
    <div className="grid gap-5">
      {/* A conta do mês */}
      <BudgetCard budget={budget} />

      {/* Impostos e gasto público em vigor, e a dívida com o prêmio */}
      <div className="grid items-start gap-5 xl:grid-cols-2">
        <div className="grid gap-5">
          <TaxesCard panel={panel} onPropose={onPropose} />
          <SpendingCard panel={panel} onPropose={onPropose} />
        </div>
        <DebtPremiumCard budget={budget} />
      </div>

      {/* De onde vem a receita */}
      <RevenueCard budget={budget} />

      {/* Quem lê a conta */}
      {panel.approval && <BudgetReadersCard approval={panel.approval} />}
    </div>
  );
}
