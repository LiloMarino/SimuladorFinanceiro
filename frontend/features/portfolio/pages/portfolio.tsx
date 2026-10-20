import usePageLabel from "@/shared/hooks/usePageLabel";
import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ErrorState } from "@/shared/components/error-state";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useGoalSteps } from "@/shared/hooks/queries/useGoalSteps";
import { usePatrimonialHistory } from "@/shared/hooks/queries/usePatrimonialHistory";
import { AllocationDonut } from "../components/allocation-donut";
import { IncomeTaxCard } from "../components/income-tax-card";
import { NetworthChart } from "../components/networth-chart";
import { PortfolioSummary } from "../components/portfolio-summary";
import { PositionsCard } from "../components/positions-card";
import { SectorAllocationCard } from "../components/sector-allocation-card";

export default function PortfolioPage() {
  usePageLabel("Carteira");
  const { data: portfolio, isLoading, error, refetch } = usePortfolio();
  const { data: history } = usePatrimonialHistory();
  const goalSteps = useGoalSteps();

  if (isLoading) {
    return (
      <div className="grid gap-5">
        <Skeleton className="h-36" />
        <div className="grid gap-5 lg:grid-cols-[1.6fr_1fr]">
          <Skeleton className="h-80" />
          <Skeleton className="h-80" />
        </div>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <Card>
        <CardContent>
          <ErrorState
            title="Não deu pra carregar sua carteira"
            description="A partida continua rodando. Tente de novo; se persistir, o servidor do host pode ter caído."
            error={error}
            onRetry={() => void refetch()}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <PortfolioSummary portfolio={portfolio} />

      <div className="grid items-start gap-5 lg:grid-cols-[1.3fr_1fr]">
        <NetworthChart history={history ?? []} goalSteps={goalSteps} />
        <AllocationDonut portfolio={portfolio} />
      </div>

      <div className="grid items-start gap-5 lg:grid-cols-[1.6fr_1fr]">
        <SectorAllocationCard portfolio={portfolio} />
        <IncomeTaxCard portfolio={portfolio} />
      </div>

      <PositionsCard portfolio={portfolio} />
    </>
  );
}
