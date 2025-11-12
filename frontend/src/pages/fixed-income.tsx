import FixedIncomeCard from "@/components/cards/fixed-income-card";
import { Spinner } from "@/components/ui/spinner";
import { useQueryApi } from "@/hooks/useQueryApi";
import { FixedIncomeAsset } from "@/models/fixed-income-asset";
import type { FixedIncomeAssetApi } from "@/types";

export default function FixedIncomePage() {
  const { data: assets, loading } = useQueryApi<FixedIncomeAssetApi[]>("/api/fixed-income");

  if (loading) {
    return (
      <section className="flex min-h-[80vh] items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </section>
    );
  }

  return (
    <section className="p-4">
      {assets && assets.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {assets.map((asset) => (
            <FixedIncomeCard key={asset.name} asset={new FixedIncomeAsset(asset)} />
          ))}
        </div>
      ) : (
        <div className="flex justify-center items-center h-full text-muted-foreground">Nenhum ativo encontrado.</div>
      )}
    </section>
  );
}
