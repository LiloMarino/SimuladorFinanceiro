import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { FixedIncomeAsset } from "@/features/fixed-income/models/FixedIncomeAsset";
import { useParams } from "react-router-dom";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
import { economicIndicatorsOptions } from "@/shared/lib/queries/economicIndicatorsOptions";
import type { FixedIncomeAssetApi } from "@/types";
import usePageLabel from "@/shared/hooks/usePageLabel";
import { parse } from "date-fns";
import { useForm } from "react-hook-form";
import { investmentFormSchema, type InvestmentFormSchema } from "../schemas/investment-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ErrorPage } from "@/pages/error";
import { LoadingPage } from "@/pages/loading";
import { Card } from "@/shared/components/ui/card";
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
  const { data: assetData, isLoading: isAssetLoading } = useApiQuery({
    queryKey: queryKeys.fixedIncomeAsset(id ?? ""),
    queryFn: ({ signal }) => apiFetch<FixedIncomeAssetApi>(`/api/fixed-income/${id}`, { signal }),
    enabled: !!id,
  });
  const { data: rates, isLoading: isRatesLoading } = useQuery(economicIndicatorsOptions());
  const { data: simData, isLoading: isSimLoading } = useSimulationState();

  const form = useForm<InvestmentFormSchema>({
    resolver: zodResolver(investmentFormSchema),
    defaultValues: {
      amount: formatMoney("0"),
    },
  });

  const asset = useMemo(() => {
    if (!assetData || !simData?.current_date || !rates) return null;
    return new FixedIncomeAsset(assetData, parse(simData.current_date, "dd/MM/yyyy", new Date()), rates);
  }, [assetData, simData?.current_date, rates]);

  if (isAssetLoading || isRatesLoading || isSimLoading) {
    return <LoadingPage />;
  }

  if (!asset || !id) {
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
    <section className="section-content p-4">
      <div className="mx-auto max-w-6xl">
        <Card className="overflow-hidden p-0 gap-0">
          <FixedIncomeHeader asset={asset} />
          <FixedIncomeBasicInfoGrid asset={asset} />

          {/* Investment Section */}
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-6">Investir neste ativo</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              <FixedIncomeInvestmentForm form={form} id={id} availableCash={simData?.cash ?? 0} />
              <FixedIncomeOperationSummary asset={asset} simulation={simulation} />
            </div>

            {/* Detalhamento Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <FixedIncomeCalculationDetails simulation={simulation} />
              <FixedIncomeTaxTable asset={asset} />
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
}
