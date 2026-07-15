import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { useFixedIncomeAssets } from "@/features/fixed-income/hooks/queries/useFixedIncomeAssets";
import { FixedIncomeAsset } from "@/features/fixed-income/models/FixedIncomeAsset";
import { parse } from "date-fns";
import FixedIncomeCard from "@/features/fixed-income/components/fixed-income-card";
import { LoadingPage } from "@/pages/loading";
import { ErrorPage } from "@/pages/error";

export default function FixedIncomePage() {
  const { data: assets, isLoading: loading, error } = useFixedIncomeAssets();
  const { data: simData } = useSimulationState();

  if (loading) {
    return <LoadingPage />;
  }

  if (!assets) {
    return (
      <ErrorPage
        code={String(error?.status) || "500"}
        title="Erro ao carregar ativos"
        message={String(error?.message)}
      />
    );
  }

  const currentDate = parse(simData?.current_date ?? "", "dd/MM/yyyy", new Date());

  return (
    <section className="p-4">
      {assets.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {assets.map((asset) => (
            <FixedIncomeCard key={asset.name} asset={new FixedIncomeAsset(asset, currentDate)} />
          ))}
        </div>
      ) : (
        <div className="flex justify-center items-center h-full text-muted-foreground">Nenhum ativo disponível.</div>
      )}
    </section>
  );
}
