import { CardState } from "@/shared/components/card-state";
import { Badge } from "@/shared/components/ui/badge";
import { Skeleton } from "@/shared/components/ui/skeleton";
import type { GovernmentPanel, MeasureKind } from "@/types";
import { useBudget } from "@/shared/hooks/queries/useBudget";
import { BaseCard } from "./base-card";
import { BudgetReadersCard } from "./budget-readers-card";
import { BudgetCard } from "./budget-card";
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

  // Cada cartão que lê o orçamento carrega e falha sozinho; base, impostos e gasto seguem na aba
  const pending = (title: React.ReactNode, label: string, skeleton: React.ReactNode) => (
    <CardState
      title={title}
      label={label}
      error={error}
      onRetry={() => void refetch()}
      errorTitle="Não deu para carregar o orçamento."
      errorDescription="A partida segue normal; a conta do governo continua sendo feita a cada fechamento de mês."
    >
      {skeleton}
    </CardState>
  );

  return (
    <div className="grid gap-5">
      {/* A base do governo no Congresso */}
      <BaseCard />

      {/* A conta do mês */}
      {budget ? (
        <BudgetCard budget={budget} />
      ) : (
        pending(
          <span className="flex items-center gap-2">
            A conta do país
            <Badge variant="secondary" size="sm">
              a sala vê
            </Badge>
          </span>,
          "Carregando a conta do país",
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }, (_, index) => (
              <Skeleton key={index} className="h-24" />
            ))}
          </div>,
        )
      )}

      {/* Impostos e gasto público em vigor, e a dívida com o prêmio */}
      <div className="grid items-start gap-5 xl:grid-cols-2">
        <div className="grid gap-5">
          <TaxesCard panel={panel} onPropose={onPropose} />
          <SpendingCard panel={panel} onPropose={onPropose} />
        </div>
        {budget ? (
          <DebtPremiumCard budget={budget} />
        ) : (
          pending("Dívida e prêmio de risco", "Carregando a dívida e o prêmio", <Skeleton className="h-64" />)
        )}
      </div>

      {/* De onde vem a receita */}
      {budget ? (
        <RevenueCard budget={budget} />
      ) : (
        pending("De onde vem a receita", "Carregando a receita", <Skeleton className="h-40" />)
      )}

      {/* Quem lê a conta */}
      {panel.approval && <BudgetReadersCard approval={panel.approval} />}
    </div>
  );
}
