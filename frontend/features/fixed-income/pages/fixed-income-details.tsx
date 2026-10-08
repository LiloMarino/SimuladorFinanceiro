import { useMemo } from "react";
import { FixedIncomeAsset } from "@/features/fixed-income/models/FixedIncomeAsset";
import { useFixedIncomeProjection } from "@/features/fixed-income/hooks/queries/useFixedIncomeProjection";
import { useParams } from "react-router-dom";
import { useSimulationState } from "@/shared/hooks/queries/useSimulationState";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { useApiQuery } from "@/shared/lib/api/useApiQuery";
import { queryKeys } from "@/shared/lib/queryKeys";
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

const ASSET_NOT_FOUND = (
  <ErrorPage
    code="404"
    title="Ativo de renda fixa não encontrado"
    actionHref="/fixed-income"
    actionLabel="Voltar para a Renda Fixa"
  />
);

export default function FixedIncomeDetailPage() {
  usePageLabel("Detalhes Renda Fixa");
  const { id } = useParams<{ id: string }>();
  const { data: assetData, isLoading: isAssetLoading } = useApiQuery({
    queryKey: queryKeys.fixedIncomeAsset(id ?? ""),
    queryFn: ({ signal }) => apiFetch<FixedIncomeAssetApi>(`/api/fixed-income/${id}`, { signal }),
    enabled: !!id,
  });
  const { data: simData, isLoading: isSimLoading } = useSimulationState();

  if (isAssetLoading || isSimLoading) {
    return <LoadingPage />;
  }

  if (!assetData || !id || !simData?.current_date) {
    return ASSET_NOT_FOUND;
  }

  return (
    <FixedIncomeDetail
      id={id}
      assetData={assetData}
      currentDate={simData.current_date}
      availableCash={simData.cash ?? "0"}
    />
  );
}

type FixedIncomeDetailProps = {
  id: string;
  assetData: FixedIncomeAssetApi;
  currentDate: string;
  availableCash: string;
};

function FixedIncomeDetail({ id, assetData, currentDate, availableCash }: FixedIncomeDetailProps) {
  const form = useForm<InvestmentFormSchema>({
    resolver: zodResolver(investmentFormSchema),
    defaultValues: {
      amount: formatMoney("0"),
    },
  });

  const amount = normalizeNumberString(form.watch("amount"));
  const { data: projection, isLoading } = useFixedIncomeProjection(id, amount, currentDate);

  const asset = useMemo(
    () => new FixedIncomeAsset(assetData, parse(currentDate, "dd/MM/yyyy", new Date())),
    [assetData, currentDate],
  );

  if (!projection) {
    return isLoading ? <LoadingPage /> : ASSET_NOT_FOUND;
  }

  return (
    <section className="section-content p-4">
      <div className="mx-auto max-w-6xl">
        <Card className="overflow-hidden p-0 gap-0">
          <FixedIncomeHeader asset={asset} projection={projection} />
          <FixedIncomeBasicInfoGrid asset={asset} projection={projection} />

          {/* Investment Section */}
          <div className="p-6">
            <h3 className="text-lg font-semibold mb-6">Investir neste ativo</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
              <FixedIncomeInvestmentForm form={form} id={id} availableCash={availableCash} />
              <FixedIncomeOperationSummary asset={asset} projection={projection} />
            </div>

            {/* Detalhamento Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <FixedIncomeCalculationDetails projection={projection} />
              <FixedIncomeTaxTable projection={projection} />
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
}
