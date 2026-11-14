import { Navigate } from "react-router-dom";
import { CardState } from "@/shared/components/card-state";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useActiveAccount } from "@/shared/hooks/useActiveAccount";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { FundFoundForm } from "../components/fund-found-form";

/** Fundar a gestora: resolve a carteira e os tetos de taxa da partida e entrega o formulário já com eles. */
export default function FundFoundPage() {
  usePageLabel("Fundar gestora");
  const { accounts } = useActiveAccount();
  const { simulation } = useSimulation();
  const { data: portfolio, error, refetch } = usePortfolio();
  const rules = simulation?.simulation;

  // Quem já tem gestora abre a dela
  if (accounts?.some((account) => account.fund_id !== null)) return <Navigate to="/funds" replace />;

  if (!portfolio || !rules) {
    return (
      <CardState
        bare
        label="Carregando a carteira"
        error={error}
        onRetry={() => void refetch()}
        errorTitle="Não deu para carregar a sua carteira"
      >
        <Skeleton className="h-16" />
        <Skeleton className="h-80" />
      </CardState>
    );
  }

  return (
    <>
      <header className="grid gap-1">
        <h1 className="text-2xl font-bold">Fundar uma gestora</h1>
        <p className="text-[13px] text-muted-foreground">
          Três passos: o nome, o que você leva da carteira e as taxas que vai cobrar.
        </p>
      </header>
      <FundFoundForm
        portfolio={portfolio}
        maxManagement={rules.fund_max_management_fee}
        maxPerformance={rules.fund_max_performance_fee}
      />
    </>
  );
}
