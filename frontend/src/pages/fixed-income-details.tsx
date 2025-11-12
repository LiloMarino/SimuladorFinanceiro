import { useMemo } from "react";
import { FixedIncomeAsset } from "@/models/fixed-income-asset";
import { useQueryApi } from "@/hooks/useQueryApi";
import { Spinner } from "@/components/ui/spinner";
import { useParams } from "react-router-dom";
import { useRealtime } from "@/hooks/useRealtime";
import type { FixedIncomeAssetApi, SimulationState } from "@/types";
import usePageLabel from "@/hooks/usePageLabel";

export default function FixedIncomeDetailPage() {
  usePageLabel("Detalhes Renda Fixa");

  const { id } = useParams<{ id: string }>();
  const { data, loading } = useQueryApi<FixedIncomeAssetApi>(`/api/fixed-income/${id}`);
  const { data: simData, setData: setSimData } = useQueryApi<SimulationState>("/api/get-simulation-state");

  useRealtime("simulation_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  const asset = useMemo(() => {
    if (!data || !simData?.currentDate) return null;
    return new FixedIncomeAsset(data, new Date(simData.currentDate));
  }, [data, simData]);

  if (loading) {
    return (
      <section className="flex min-h-[80vh] items-center justify-center">
        <Spinner className="h-8 w-8 text-muted-foreground" />
      </section>
    );
  }

  if (!asset) {
    return <div className="p-6 text-center text-gray-500">Ativo não encontrado.</div>;
  }

  return <>Template aqui</>;
}
