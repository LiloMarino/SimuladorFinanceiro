import { useMemo } from "react";
import { FixedIncomeAsset } from "@/features/fixed-income/models/FixedIncomeAsset";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import { useParams } from "react-router-dom";
import { useRealtime } from "@/shared/hooks/useRealtime";
import type { EconomicIndicators, FixedIncomeAssetApi, SimulationState } from "@/types";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { parse } from "date-fns";
import { useForm } from "react-hook-form";
import { investmentFormSchema, type InvestmentFormSchema } from "../schemas/investment-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ErrorPage } from "@/pages/error";
import { LoadingPage } from "@/pages/loading";
import { FixedIncomeHeader } from "../components/fixed-income-header";
import { FixedIncomeBasicInfoGrid } from "../components/fixed-income-basic-info-grid";
import { FixedIncomeInvestmentForm } from "../components/fixed-income-investment-form";
import { FixedIncomeOperationSummary } from "../components/fixed-income-operation-summary";
import { FixedIncomeCalculationDetails } from "../components/fixed-income-calculation-details";
import { FixedIncomeTaxTable } from "../components/fixed-income-tax-table";
import { formatMoney } from "@/shared/lib/utils/format";
import { normalizeNumberString } from "@/shared/lib/utils";

export default function FixedIncomeDetailPage() {
  usePageLabel("Detalhes Renda Fixa");
  const { id } = useParams<{ id: string }>();
  const { data: assetData, loading: isAssetLoading } = useQueryApi<FixedIncomeAssetApi>(`/api/fixed-income/${id}`);
  const { data: rates, loading: isRatesLoading } = useQueryApi<EconomicIndicators>("/api/economic-indicators");
  const {
    data: simData,
    setData: setSimData,
    loading: isSimLoading,
  } = useQueryApi<SimulationState>("/api/get-simulation-state");

  const form = useForm<InvestmentFormSchema>({
    resolver: zodResolver(investmentFormSchema),
    defaultValues: {
      amount: formatMoney("0"),
    },
  });

  useRealtime("simulation_update", (update) => {
    setSimData((prev) => ({ ...prev, ...update }));
  });

  const asset = useMemo(() => {
    if (!assetData || !simData?.currentDate || !rates) return null;
    return new FixedIncomeAsset(assetData, parse(simData.currentDate, "dd/MM/yyyy", new Date()), rates);
  }, [assetData, simData?.currentDate, rates]);

  if (isAssetLoading || isRatesLoading || isSimLoading) {
    return <LoadingPage />;
  }

  if (!asset) {
    return (
      <ErrorPage
        code="404"
        title="Ativo de renda fixa não encontrado"
        actionHref="/fixed-income"
        actionLabel="Voltar para a Renda Fixa"
      />
    );
  }

  const amount = form.watch("amount");
  const simulation = asset.getSimulation(Number(normalizeNumberString(amount)));
  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="mx-auto max-w-6xl">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <FixedIncomeHeader asset={asset} />
          <FixedIncomeBasicInfoGrid asset={asset} />

          {/* Investment Section */}
          <div className="p-6">
            <h3 className="text-lg font-semibold text-slate-900 mb-6">Investir neste ativo</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              <FixedIncomeInvestmentForm form={form} id={id} />
              <FixedIncomeOperationSummary asset={asset} simulation={simulation} />
            </div>

            {/* Detalhamento Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <FixedIncomeCalculationDetails simulation={simulation} />
              <FixedIncomeTaxTable asset={asset} />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
