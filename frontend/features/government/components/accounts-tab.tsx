import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import type { GovernmentPanel, MeasureKind } from "@/types";
import { useBudget } from "@/shared/hooks/queries/useBudget";
import { BaseCard } from "./base-card";
import { BudgetCard } from "./budget-card";
import { useToday } from "../hooks/useToday";
import { DebtCard } from "./debt-card";
import { SelicCard } from "./selic-card";
import { SpendingCard } from "./spending-card";
import { TaxesCard } from "./taxes-card";

type AccountsTabProps = {
  panel: GovernmentPanel;
  onPropose: (kind?: MeasureKind) => void;
};

/** A aba Contas, em uma coluna na ordem da conta: a base no Congresso, a SELIC (quando é do governo), a conta do país, o que entra (impostos e receita), o que sai (gasto público) e a dívida. */
export function AccountsTab({ panel, onPropose }: AccountsTabProps) {
  const { data: budget, error, refetch } = useBudget();
  const today = useToday(panel);

  // Cada cartão que lê o orçamento carrega e falha sozinho; a base e o gasto seguem na aba
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

      {/* A SELIC, quando a partida a põe nas mãos do governo */}
      {panel.monetary && <SelicCard monetary={panel.monetary} today={today} isPresident={panel.is_president} />}

      {/* A conta do mês */}
      {budget ? (
        <BudgetCard budget={budget} />
      ) : (
        pending(
          "A conta do país",
          "Carregando a conta do país",
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }, (_, index) => (
              <Skeleton key={index} className="h-24" />
            ))}
          </div>,
        )
      )}

      {/* Entra: impostos e receita */}
      {budget ? (
        <TaxesCard panel={panel} budget={budget} onPropose={onPropose} />
      ) : (
        pending("Impostos e receita", "Carregando os impostos e a receita", <Skeleton className="h-64" />)
      )}

      {/* Sai: gasto público */}
      <SpendingCard panel={panel} onPropose={onPropose} />

      {/* A dívida */}
      {budget ? <DebtCard budget={budget} /> : pending("Dívida", "Carregando a dívida", <Skeleton className="h-64" />)}
    </div>
  );
}
