import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useRealtime } from "@/shared/hooks/useRealtime";
import { FixedIncomeAsset } from "@/features/fixed-income/models/FixedIncomeAsset";
import type { FixedIncomeAssetApi, SimulationState } from "@/types";
import { parse } from "date-fns";
import FixedIncomeCard from "@/features/fixed-income/components/fixed-income-card";
import { LoadingPage } from "@/pages/loading";

export default function FixedIncomePage() {
  const { data: assets, setData: setAssets, loading } = useQueryApi<FixedIncomeAssetApi[]>("/api/fixed-income");
  const { data: simData, setData: setSimData } = useQueryApi<SimulationState>("/api/get-simulation-state");

  useRealtime("simulation_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  useRealtime("fixed_assets_update", ({ assets }) => {
    setAssets(assets);
  });

  if (loading) {
    return <LoadingPage />;
  }

  const currentDate = parse(simData?.currentDate ?? "", "dd/MM/yyyy", new Date());

  return (
    <section className="p-4">
      {assets && assets.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {assets.map((asset) => (
            <FixedIncomeCard key={asset.name} asset={new FixedIncomeAsset(asset, currentDate)} />
          ))}
        </div>
      ) : (
        <div className="flex justify-center items-center h-full text-muted-foreground">Nenhum ativo encontrado.</div>
      )}
    </section>
  );
}
